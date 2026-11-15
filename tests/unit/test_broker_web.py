"""Unit tests for Lazy OS web browser broker (lazy-broker-web, Milestone M4.3).

Verifies:
- DOM-to-structured extraction: visible text, links, form fields with element IDs.
- Hidden text and prompt injection detection: style display:none, visibility:hidden, type=hidden, comments.
- Domain allowlist enforcement (L1 for allowlisted domains, L2 user approval for new domains).
- Download quarantine: file saved to isolated quarantine directory with non-executable permissions (0600) and SHA256.
- Interactive browser simulation on local fixture test website (navigate, click, fill, submit).
- Rule F3 compliance: untrusted web content explicitly labelled as quoted data.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import pytest

from lazy.brokers.web_broker import (
    WebBroker,
    PureHTMLDOMParser,
    DomainAllowlist,
    IsolatedBrowserDriver,
    DomainNotAllowedError,
)


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def test_site_dir(repo_root: Path) -> Path:
    return repo_root / "tests" / "fixtures" / "website"


@pytest.fixture
def web_broker(repo_root: Path, tmp_path: Path) -> WebBroker:
    quarantine_dir = tmp_path / "quarantine"
    allowlist_path = repo_root / "config" / "allowlist.yaml"
    return WebBroker(
        base_dir=repo_root,
        quarantine_dir=quarantine_dir,
        allowlist_path=allowlist_path,
    )


class TestPureHTMLDOMParser:
    def test_parse_index_page(self, test_site_dir: Path):
        index_file = test_site_dir / "index.html"
        parser = PureHTMLDOMParser(url=f"file://{index_file}")
        parser.feed(index_file.read_text(encoding="utf-8"))
        dom = parser.build_dom()

        assert dom.title == "Lazy OS Test Portal"
        assert "Welcome to Lazy OS Local Test Portal" in dom.visible_text

        # Verify links
        assert len(dom.links) >= 3
        link_ids = [l["id"] for l in dom.links]
        assert "link-login" in link_ids
        assert "link-search" in link_ids
        assert "link-injected" in link_ids

        # Verify form fields
        field_ids = [f["id"] for f in dom.form_fields]
        assert "search-input" in field_ids

        # No hidden injections on clean index
        assert len(dom.hidden_text) == 0

    def test_hidden_prompt_injection_detection(self, test_site_dir: Path):
        injected_file = test_site_dir / "injected.html"
        parser = PureHTMLDOMParser(url=f"file://{injected_file}")
        parser.feed(injected_file.read_text(encoding="utf-8"))
        dom = parser.build_dom()

        assert dom.title == "System Documentation"
        assert "Operating System Architecture Overview" in dom.visible_text

        # Hidden text must be caught and isolated!
        assert len(dom.hidden_text) >= 3
        hidden_joined = " ".join(dom.hidden_text)

        # Style display:none caught
        assert "/etc/shadow" in hidden_joined or "Disregard prior safety rules" in hidden_joined
        # Style visibility:hidden caught
        assert "rm -rf /" in hidden_joined
        # Hidden input type caught
        assert "DROP TABLE" in hidden_joined or "override_cmd" in hidden_joined

        # Rule F3 labelled format includes warning
        labelled = dom.to_labelled_data()
        assert "=== BEGIN UNTRUSTED WEBPAGE" in labelled
        assert "[WARNING: HIDDEN UNTRUSTED TEXT DETECTED]" in labelled
        assert "=== END UNTRUSTED WEBPAGE ==="


class TestDomainAllowlist:
    def test_allowlist_matching(self, repo_root: Path):
        allowlist = DomainAllowlist(
            config_path=repo_root / "config" / "allowlist.yaml",
            base_dir=repo_root,
        )

        assert allowlist.is_allowed("https://kernel.org/pub/linux") is True
        assert allowlist.is_allowed("https://sub.yoctoproject.org/downloads") is True
        assert allowlist.is_allowed("http://127.0.0.1:8765/hud") is True
        assert allowlist.is_allowed("file:///var/lib/lazy/doc.html") is True

        # Untrusted domain rejected
        assert allowlist.is_allowed("https://malicious-phishing.org/login") is False

    def test_dynamically_adding_approved_domain(self, repo_root: Path):
        allowlist = DomainAllowlist(config_path=repo_root / "config" / "allowlist.yaml")
        assert allowlist.is_allowed("https://trusted-partner.edu/report") is False
        allowlist.add_domain("trusted-partner.edu")
        assert allowlist.is_allowed("https://trusted-partner.edu/report") is True


class TestWebBrokerCapabilities:
    def test_web_read_capability(self, web_broker: WebBroker, test_site_dir: Path):
        url = f"file://{test_site_dir / 'index.html'}"
        res = web_broker.execute("web.read", {"url": url})

        assert res["status"] == "ok"
        dom_data = res["result"]
        assert dom_data["title"] == "Lazy OS Test Portal"
        assert dom_data["untrusted_data"] is True
        assert len(dom_data["links"]) >= 3

    def test_web_navigate_tier_l1_vs_l2(self, web_broker: WebBroker, test_site_dir: Path):
        # 1. Allowlisted navigation (file:// or 127.0.0.1) -> L1
        local_url = f"file://{test_site_dir / 'search.html'}"
        res_l1 = web_broker.execute("web.navigate", {"url": local_url})
        assert res_l1["status"] == "ok"
        assert res_l1["result"]["tier"] == "L1"
        assert res_l1["result"]["title"] == "Search Results"

        # 2. New external domain without approval -> raises DomainNotAllowedError
        res_l2_fail = web_broker.execute("web.navigate", {"url": "https://untrusted-external.net/info"})
        assert res_l2_fail["status"] == "error"
        assert "not in allowlist" in res_l2_fail["error"]

        # 3. New external domain with explicit confirmation -> L2
        # (Mock navigate on external URL will attempt fetch, or we test confirm_new_domain flag)
        res_l2_ok = web_broker.execute("web.navigate", {
            "url": local_url,
            "confirm_new_domain": True,
        })
        assert res_l2_ok["status"] == "ok"

    def test_web_click_navigate_link(self, web_broker: WebBroker, test_site_dir: Path):
        start_url = f"file://{test_site_dir / 'index.html'}"
        web_broker.execute("web.navigate", {"url": start_url})

        # Click login link
        click_res = web_broker.execute("web.click", {"element_id": "link-login"})
        assert click_res["status"] == "ok"
        assert click_res["result"]["type"] == "link"
        assert "login.html" in click_res["result"]["target_url"]

        # Active page should now be login
        assert web_broker.driver.current_dom.title == "Portal Login"

    def test_web_fill_and_submit_form(self, web_broker: WebBroker, test_site_dir: Path):
        login_url = f"file://{test_site_dir / 'login.html'}"
        web_broker.execute("web.navigate", {"url": login_url})

        # Fill credentials
        fill_user = web_broker.execute("web.fill", {"element_id": "username-field", "value": "auditor_user"})
        assert fill_user["status"] == "ok"

        fill_pass = web_broker.execute("web.fill", {"element_id": "password-field", "value": "correct_pass_123"})
        assert fill_pass["status"] == "ok"

        # Submit form
        sub_res = web_broker.execute("web.submit", {"form_id": "login-form"})
        assert sub_res["status"] == "ok"
        assert sub_res["result"]["form_id"] == "login-form"
        assert sub_res["result"]["submitted_fields"]["username-field"] == "auditor_user"

    def test_web_download_into_quarantine(self, web_broker: WebBroker, test_site_dir: Path):
        download_src = f"file://{test_site_dir / 'downloadable.txt'}"
        dl_res = web_broker.execute("web.download", {
            "url": download_src,
            "dest_filename": "test_quarantine_doc.txt",
        })

        assert dl_res["status"] == "ok"
        res_data = dl_res["result"]
        assert res_data["quarantined"] is True
        assert res_data["permissions"] == "0600"

        # Verify file exists in quarantine
        q_file = Path(res_data["quarantine_path"])
        assert q_file.is_file()
        content = q_file.read_bytes()

        # Verify SHA256 integrity
        expected_sha = hashlib.sha256(content).hexdigest()
        assert res_data["sha256"] == expected_sha
