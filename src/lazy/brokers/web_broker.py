"""Web browser broker for Lazy OS (lazy-broker-web): isolated driver, DOM-to-structured extraction, allowlist, and download quarantine."""
from __future__ import annotations

import abc
import hashlib
from html.parser import HTMLParser
import json
import logging
import os
from pathlib import Path
import re
import socket
from typing import Any, Dict, List, Optional, Set
import urllib.error
import urllib.parse
import urllib.request
import yaml

from lazy.brokers.base import BaseBroker, BrokerExecutionError
from lazy.outbox.models import OutboxItem
from lazy.outbox.queue import OutboxQueue

logger = logging.getLogger("lazy.broker.web")


class DomainNotAllowedError(BrokerExecutionError):
    """Raised when navigation to a non-allowlisted domain is attempted without approval."""


class StructuredDOM:
    """Structured extraction of webpage content with explicit separation of visible and hidden elements."""

    def __init__(
        self,
        url: str,
        title: str = "",
        visible_text: str = "",
        links: Optional[List[Dict[str, Any]]] = None,
        form_fields: Optional[List[Dict[str, Any]]] = None,
        forms: Optional[List[Dict[str, Any]]] = None,
        hidden_text: Optional[List[str]] = None,
    ):
        self.url = url
        self.title = title
        self.visible_text = visible_text.strip()
        self.links = links or []
        self.form_fields = form_fields or []
        self.forms = forms or []
        self.hidden_text = hidden_text or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "visible_text": self.visible_text,
            "links": self.links,
            "form_fields": self.form_fields,
            "forms": self.forms,
            "hidden_text": self.hidden_text,
            "has_hidden_injections": len(self.hidden_text) > 0,
            "untrusted_data": True,  # Rule F3
        }

    def to_labelled_data(self) -> str:
        """Format webpage contents as explicitly labelled quoted data per Rule F3."""
        hidden_warning = ""
        if self.hidden_text:
            hidden_warning = (
                "\n[WARNING: HIDDEN UNTRUSTED TEXT DETECTED]\n"
                + "\n".join(f"- {h}" for h in self.hidden_text)
                + "\n"
            )

        links_str = "\n".join(f"- [{l.get('id', '')}] {l.get('text', '')} -> {l.get('href', '')}" for l in self.links)
        fields_str = "\n".join(
            f"- Field id='{f.get('id', '')}' name='{f.get('name', '')}' type='{f.get('type', 'text')}' value='{f.get('value', '')}'"
            for f in self.form_fields
        )

        return (
            f"=== BEGIN UNTRUSTED WEBPAGE [url={self.url}] ===\n"
            f"Title: {self.title}\n\n"
            f"[VISIBLE CONTENT]\n{self.visible_text}\n\n"
            f"[LINKS]\n{links_str}\n\n"
            f"[FORM FIELDS]\n{fields_str}\n"
            f"{hidden_warning}"
            f"=== END UNTRUSTED WEBPAGE ==="
        )


class PureHTMLDOMParser(HTMLParser):
    """Parses HTML into structured DOM separating visible text, links, forms, and hidden text."""

    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.title = ""
        self.visible_chunks: List[str] = []
        self.hidden_chunks: List[str] = []
        self.links: List[Dict[str, Any]] = []
        self.form_fields: List[Dict[str, Any]] = []
        self.forms: List[Dict[str, Any]] = []

        self._in_title = False
        self._hidden_depth = 0
        self._current_tag = ""
        self._current_link: Optional[Dict[str, Any]] = None

    def handle_starttag(self, tag: str, attrs: List[tuple[str, Optional[str]]]) -> None:
        attr_dict = {k.lower(): (v or "") for k, v in attrs}
        self._current_tag = tag.lower()

        # Check for title tag
        if self._current_tag == "title":
            self._in_title = True

        # Check for hidden styling
        style = attr_dict.get("style", "").lower()
        is_hidden_style = (
            "display:none" in style.replace(" ", "")
            or "visibility:hidden" in style.replace(" ", "")
            or "opacity:0" in style.replace(" ", "")
        )

        if is_hidden_style or "hidden" in attr_dict:
            self._hidden_depth += 1

        # Check form tag
        if self._current_tag == "form":
            self.forms.append({
                "id": attr_dict.get("id", ""),
                "action": attr_dict.get("action", ""),
                "method": attr_dict.get("method", "GET").upper(),
            })

        # Check input/button form elements
        if self._current_tag in ("input", "button", "textarea", "select"):
            inp_type = attr_dict.get("type", "text").lower()
            elem_id = attr_dict.get("id", "")
            elem_name = attr_dict.get("name", "")
            elem_val = attr_dict.get("value", "")

            if inp_type == "hidden" or self._hidden_depth > 0:
                if elem_val:
                    self.hidden_chunks.append(f"Hidden input {elem_id or elem_name}: {elem_val}")
            else:
                self.form_fields.append({
                    "id": elem_id,
                    "name": elem_name,
                    "type": inp_type,
                    "value": elem_val,
                })

        # Check anchor links
        if self._current_tag == "a":
            href = attr_dict.get("href", "")
            link_id = attr_dict.get("id", "")
            self._current_link = {"id": link_id, "href": href, "text": ""}

    def handle_endtag(self, tag: str) -> None:
        tag_lower = tag.lower()
        if tag_lower == "title":
            self._in_title = False
        elif tag_lower == "a" and self._current_link:
            self._current_link["text"] = self._current_link["text"].strip()
            self.links.append(self._current_link)
            self._current_link = None

        if self._hidden_depth > 0 and tag_lower in ("div", "span", "p", "section"):
            self._hidden_depth -= 1

    def handle_data(self, data: str) -> None:
        clean = data.strip()
        if not clean:
            return

        if self._in_title:
            self.title += clean + " "
        elif self._hidden_depth > 0:
            self.hidden_chunks.append(clean)
        else:
            if self._current_link is not None:
                self._current_link["text"] += clean + " "
            self.visible_chunks.append(clean)

    def handle_comment(self, data: str) -> None:
        clean = data.strip()
        if clean:
            # HTML comments can hide prompt injections
            self.hidden_chunks.append(f"<!-- {clean} -->")

    def build_dom(self) -> StructuredDOM:
        return StructuredDOM(
            url=self.url,
            title=self.title.strip(),
            visible_text=" ".join(self.visible_chunks),
            links=self.links,
            form_fields=self.form_fields,
            forms=self.forms,
            hidden_text=self.hidden_text_list,
        )

    @property
    def hidden_text_list(self) -> List[str]:
        return [c for c in self.hidden_chunks if c]


class DomainAllowlist:
    """Manages allowed domains for Tier L1 automatic navigation."""

    def __init__(self, config_path: Optional[Path | str] = None, base_dir: Optional[Path | str] = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.config_path = Path(config_path) if config_path else self.base_dir / "config" / "allowlist.yaml"
        self.allowed_domains: Set[str] = set()
        self._load()

    def _load(self) -> None:
        if self.config_path.is_file():
            try:
                data = yaml.safe_load(self.config_path.read_text(encoding="utf-8"))
                for d in data.get("allowlist", []):
                    self.allowed_domains.add(str(d).lower().strip())
            except Exception as e:
                logger.error("Failed to load allowlist from %s: %s", self.config_path, e)
        else:
            # Default fallback allowlist
            self.allowed_domains = {"localhost", "127.0.0.1", "kernel.org", "yoctoproject.org"}

    def is_allowed(self, url: str) -> bool:
        """Check if URL host is in the approved domain allowlist."""
        if url.startswith("file://") or not (url.startswith("http://") or url.startswith("https://")):
            return True  # Local file or fixture path is permitted

        parsed = urllib.parse.urlparse(url)
        host = (parsed.hostname or "").lower()
        if not host:
            return False

        for domain in self.allowed_domains:
            if host == domain or host.endswith("." + domain):
                return True
        return False

    def add_domain(self, domain: str) -> None:
        """Add domain after user approval."""
        self.allowed_domains.add(domain.lower().strip())


class BaseBrowserDriver(abc.ABC):
    """Abstract browser driver interface for Lazy OS (Rule F9)."""

    @abc.abstractmethod
    def navigate(self, url: str) -> StructuredDOM:
        pass

    @abc.abstractmethod
    def click(self, element_id: str) -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    def fill(self, element_id: str, value: str) -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    def submit(self, form_id: str) -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    def download_to_quarantine(self, url: str, dest_filename: str) -> Dict[str, Any]:
        pass

    @property
    @abc.abstractmethod
    def driver_name(self) -> str:
        pass


class PurePythonBrowserDriver(BaseBrowserDriver):
    """Headless isolated pure-Python HTTP and DOM extraction driver (Rule F9)."""

    def __init__(self, base_dir: Optional[Path | str] = None, quarantine_dir: Optional[Path | str] = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.quarantine_dir = Path(quarantine_dir) if quarantine_dir else self.base_dir / "var" / "quarantine"
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)

        self.current_url: str = "about:blank"
        self.history: List[str] = []
        self.current_dom: StructuredDOM = StructuredDOM(url="about:blank")
        self.field_values: Dict[str, str] = {}

    @property
    def driver_name(self) -> str:
        return "pure_python"

    def _resolve_url_content(self, url: str) -> tuple[str, str]:
        """Read HTML content from file:// URL or local path, or HTTP."""
        if url.startswith("file://"):
            raw_path = url[len("file://"):]
            if os.name == "nt" and raw_path.startswith("/") and len(raw_path) > 2 and raw_path[2] == ":":
                raw_path = raw_path[1:]
            p = Path(raw_path)
            if not p.is_absolute():
                p = self.base_dir / p
            return p.read_text(encoding="utf-8", errors="replace"), url
        elif url.startswith("http://") or url.startswith("https://"):
            req = urllib.request.Request(url, headers={"User-Agent": "LazyOS-Browser/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                content = resp.read().decode("utf-8", errors="replace")
                return content, url
        else:
            # Relative local file path
            p = self.base_dir / url
            if not p.is_file():
                raise FileNotFoundError(f"Local document not found: {p}")
            return p.read_text(encoding="utf-8", errors="replace"), f"file://{p}"

    def navigate(self, url: str) -> StructuredDOM:
        """Navigate browser to destination URL."""
        html_content, canonical_url = self._resolve_url_content(url)
        parser = PureHTMLDOMParser(url=canonical_url)
        parser.feed(html_content)

        self.current_url = canonical_url
        self.history.append(canonical_url)
        self.current_dom = parser.build_dom()

        # Initialize field values
        self.field_values = {f["id"]: f["value"] for f in self.current_dom.form_fields if f.get("id")}
        return self.current_dom

    def click(self, element_id: str) -> Dict[str, Any]:
        """Click an interactive element (link or button)."""
        # 1. Check if link
        for link in self.current_dom.links:
            if link.get("id") == element_id:
                target_href = link["href"]
                # Resolve relative URL against current_url
                next_url = urllib.parse.urljoin(self.current_url, target_href)
                self.navigate(next_url)
                return {
                    "action": "click",
                    "element_id": element_id,
                    "target_url": next_url,
                    "type": "link",
                }

        # 2. Check if button in form
        for f in self.current_dom.form_fields:
            if f.get("id") == element_id and f.get("type") in ("submit", "button"):
                return {"action": "click", "element_id": element_id, "type": "button"}

        return {"action": "click", "element_id": element_id, "status": "no_op"}

    def fill(self, element_id: str, value: str) -> Dict[str, Any]:
        """Fill an input field on the page."""
        found = False
        for f in self.current_dom.form_fields:
            if f.get("id") == element_id:
                f["value"] = value
                self.field_values[element_id] = value
                found = True
                break

        if not found:
            self.field_values[element_id] = value

        return {"action": "fill", "element_id": element_id, "value": value}

    def submit(self, form_id: str) -> Dict[str, Any]:
        """Submit form data with currently filled fields."""
        form = next((f for f in self.current_dom.forms if f.get("id") == form_id), None)
        action = form.get("action", self.current_url) if form else self.current_url

        target_url = urllib.parse.urljoin(self.current_url, action)
        submitted_data = dict(self.field_values)

        if action:
            try:
                self.navigate(target_url)
            except Exception as e:
                logger.warning("Form submission navigation error (%s)", e)

        return {
            "status": "submitted",
            "form_id": form_id,
            "target_url": target_url,
            "submitted_fields": submitted_data,
        }

    def download_to_quarantine(self, url: str, dest_filename: str) -> Dict[str, Any]:
        """Download remote or local file exclusively into isolated quarantine directory (Tier L3)."""
        content, _ = self._resolve_url_content(url)
        dest_path = self.quarantine_dir / dest_filename

        raw_bytes = content.encode("utf-8")
        dest_path.write_bytes(raw_bytes)

        # Set permissions to 0600 (read/write by owner only, non-executable!)
        try:
            dest_path.chmod(0o600)
        except Exception:
            pass

        sha256 = hashlib.sha256(raw_bytes).hexdigest()
        return {
            "filename": dest_filename,
            "quarantine_path": str(dest_path),
            "size_bytes": len(raw_bytes),
            "sha256": sha256,
            "quarantined": True,
            "permissions": "0600",
        }


# Backwards compatibility alias
IsolatedBrowserDriver = PurePythonBrowserDriver


class WebDriverBrowserDriver(BaseBrowserDriver):
    """W3C WebDriver HTTP wire protocol browser driver (e.g., headless Chromium / Firefox)."""

    def __init__(
        self,
        base_dir: Optional[Path | str] = None,
        quarantine_dir: Optional[Path | str] = None,
        webdriver_url: str = "http://127.0.0.1:9515",
    ):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.quarantine_dir = Path(quarantine_dir) if quarantine_dir else self.base_dir / "var" / "quarantine"
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
        self.webdriver_url = webdriver_url.rstrip("/")
        self.session_id: Optional[str] = None
        self.current_url: str = "about:blank"
        self.current_dom: StructuredDOM = StructuredDOM(url="about:blank")
        self.field_values: Dict[str, str] = {}
        # Standalone fallback driver instance for local file URLs or when daemon drops
        self._fallback_driver = PurePythonBrowserDriver(base_dir=self.base_dir, quarantine_dir=self.quarantine_dir)

    @property
    def driver_name(self) -> str:
        return "webdriver"

    def is_daemon_reachable(self, timeout: float = 0.5) -> bool:
        """Check if WebDriver HTTP server is responding."""
        try:
            url = f"{self.webdriver_url}/status"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _ensure_session(self) -> str:
        """Establish W3C WebDriver session if not already open."""
        if self.session_id:
            return self.session_id

        payload = json.dumps({
            "capabilities": {
                "alwaysMatch": {
                    "acceptInsecureCerts": True,
                    "pageLoadStrategy": "normal",
                }
            }
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.webdriver_url}/session",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                self.session_id = data.get("value", {}).get("sessionId") or data.get("sessionId")
                if not self.session_id:
                    raise BrokerExecutionError("WebDriver failed to return sessionId")
                return self.session_id
        except Exception as e:
            raise BrokerExecutionError(f"Cannot connect to WebDriver at {self.webdriver_url}: {e}")

    def navigate(self, url: str) -> StructuredDOM:
        """Navigate via WebDriver and extract structured DOM."""
        if url.startswith("file://") or not (url.startswith("http://") or url.startswith("https://")):
            # Local file or fixture path handled via isolated parser
            return self._fallback_driver.navigate(url)

        if not self.is_daemon_reachable():
            logger.info("WebDriver not reachable; falling back to PurePythonBrowserDriver")
            return self._fallback_driver.navigate(url)

        session_id = self._ensure_session()
        nav_payload = json.dumps({"url": url}).encode("utf-8")
        nav_req = urllib.request.Request(
            f"{self.webdriver_url}/session/{session_id}/url",
            data=nav_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(nav_req, timeout=5.0) as resp:
            pass

        # Get page source
        source_req = urllib.request.Request(f"{self.webdriver_url}/session/{session_id}/source")
        with urllib.request.urlopen(source_req, timeout=5.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            html_source = data.get("value", "")

        parser = PureHTMLDOMParser(url=url)
        parser.feed(html_source)
        self.current_url = url
        self.current_dom = parser.build_dom()
        self.field_values = {f["id"]: f["value"] for f in self.current_dom.form_fields if f.get("id")}
        return self.current_dom

    def click(self, element_id: str) -> Dict[str, Any]:
        """Click element via WebDriver or fallback."""
        if not self.session_id or not self.is_daemon_reachable():
            return self._fallback_driver.click(element_id)
        # Attempt click via fallback parser to maintain structured state
        return self._fallback_driver.click(element_id)

    def fill(self, element_id: str, value: str) -> Dict[str, Any]:
        """Fill element via WebDriver or fallback."""
        self.field_values[element_id] = value
        return self._fallback_driver.fill(element_id, value)

    def submit(self, form_id: str) -> Dict[str, Any]:
        """Submit form via WebDriver or fallback."""
        return self._fallback_driver.submit(form_id)

    def download_to_quarantine(self, url: str, dest_filename: str) -> Dict[str, Any]:
        """Download file into isolated quarantine directory."""
        return self._fallback_driver.download_to_quarantine(url, dest_filename)


def get_browser_driver(
    driver_type: str = "auto",
    base_dir: Optional[Path | str] = None,
    quarantine_dir: Optional[Path | str] = None,
    webdriver_url: str = "http://127.0.0.1:9515",
) -> BaseBrowserDriver:
    """Browser driver factory supporting WebDriver and PurePython sandbox fallback."""
    if driver_type == "pure_python":
        return PurePythonBrowserDriver(base_dir=base_dir, quarantine_dir=quarantine_dir)
    elif driver_type == "webdriver":
        return WebDriverBrowserDriver(base_dir=base_dir, quarantine_dir=quarantine_dir, webdriver_url=webdriver_url)
    else:  # auto
        probe_driver = WebDriverBrowserDriver(base_dir=base_dir, quarantine_dir=quarantine_dir, webdriver_url=webdriver_url)
        if probe_driver.is_daemon_reachable():
            logger.info("WebDriver service detected at %s; activating WebDriverBrowserDriver", webdriver_url)
            return probe_driver
        else:
            logger.info("WebDriver service not active; using PurePythonBrowserDriver fallback")
            return PurePythonBrowserDriver(base_dir=base_dir, quarantine_dir=quarantine_dir)


class WebBroker(BaseBroker):
    """Handles browser capabilities: web.read, web.navigate, web.click, web.fill, web.submit, web.download."""

    def __init__(
        self,
        base_dir: Optional[Path | str] = None,
        quarantine_dir: Optional[Path | str] = None,
        allowlist_path: Optional[Path | str] = None,
        outbox: Optional[OutboxQueue] = None,
        driver: Optional[BaseBrowserDriver] = None,
    ):
        super().__init__("lazy-broker-web")
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.allowlist = DomainAllowlist(config_path=allowlist_path, base_dir=self.base_dir)
        self.driver = driver or get_browser_driver(base_dir=self.base_dir, quarantine_dir=quarantine_dir)
        self.outbox = outbox if outbox else OutboxQueue()

        self._register_handlers()

        self._register_handlers()

    def _register_handlers(self) -> None:
        self.register("web.read", self.handle_web_read)
        self.register("web.navigate", self.handle_web_navigate)
        self.register("web.click", self.handle_web_click)
        self.register("web.fill", self.handle_web_fill)
        self.register("web.submit", self.handle_web_submit)
        self.register("web.download", self.handle_web_download)

    def handle_web_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """L0: Extract text and structured content from page."""
        url = params.get("url")
        if url:
            dom = self.driver.navigate(url)
        else:
            dom = self.driver.current_dom
        return dom.to_dict()

    def handle_web_navigate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """L1 for allowlisted domains; L2 for new domains."""
        url = params["url"]
        confirm_new = params.get("confirm_new_domain", False)

        is_allowed = self.allowlist.is_allowed(url)
        if not is_allowed and not confirm_new:
            parsed = urllib.parse.urlparse(url)
            raise DomainNotAllowedError(
                f"Domain '{parsed.netloc}' is not in allowlist. User approval required (Tier L2)."
            )

        if not is_allowed and confirm_new:
            # User confirmed new domain
            parsed = urllib.parse.urlparse(url)
            self.allowlist.add_domain(parsed.netloc)

        dom = self.driver.navigate(url)
        return {
            "status": "navigated",
            "url": dom.url,
            "title": dom.title,
            "tier": "L1" if is_allowed else "L2",
            "has_hidden_injections": len(dom.hidden_text) > 0,
        }

    def handle_web_click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """L2: Click element on active webpage."""
        elem_id = params["element_id"]
        res = self.driver.click(elem_id)
        return res

    def handle_web_fill(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """L2: Fill form field on active webpage."""
        elem_id = params["element_id"]
        value = params["value"]
        res = self.driver.fill(elem_id, value)
        return res

    def handle_web_submit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """L3: Submit web form."""
        form_id = params["form_id"]
        res = self.driver.submit(form_id)
        return res

    def handle_web_download(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """L3: Download external file into quarantine."""
        url = params["url"]
        dest = params["dest_filename"]
        res = self.driver.download_to_quarantine(url, dest)
        return res
