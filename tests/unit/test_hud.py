"""Unit tests for Lazy OS HUD: static assets, offline self-containment, DOM components, and gateway serving."""
from __future__ import annotations

import re
import socket
import time
import urllib.request
from pathlib import Path

import pytest

from lazy.gateway.server import GatewayServer
from lazy.gateway.token import HUDTokenManager


@pytest.fixture
def hud_dir():
    repo_root = Path(__file__).resolve().parent.parent.parent
    return repo_root / "hud"


class TestHUDAssets:
    def test_files_exist_and_non_empty(self, hud_dir: Path):
        html_file = hud_dir / "index.html"
        css_file = hud_dir / "hud.css"
        js_file = hud_dir / "hud.js"

        assert html_file.is_file(), "Missing hud/index.html"
        assert css_file.is_file(), "Missing hud/hud.css"
        assert js_file.is_file(), "Missing hud/hud.js"

        assert len(html_file.read_text(encoding="utf-8")) > 500
        assert len(css_file.read_text(encoding="utf-8")) > 500
        assert len(js_file.read_text(encoding="utf-8")) > 500

    def test_strict_offline_zero_external_cdns(self, hud_dir: Path):
        """Verify HUD works 100% offline without remote CDN or HTTP font/script dependencies."""
        html_content = (hud_dir / "index.html").read_text(encoding="utf-8")
        css_content = (hud_dir / "hud.css").read_text(encoding="utf-8")
        js_content = (hud_dir / "hud.js").read_text(encoding="utf-8")

        # HTML must not link external scripts or stylesheets
        external_links = re.findall(r'(src|href)=["\']https?://[^"\']+["\']', html_content)
        assert len(external_links) == 0, f"Found external web resources in index.html: {external_links}"

        # CSS must not import external fonts or styles
        css_imports = re.findall(r'@import\s+url\(["\']?https?://[^"\')]+["\']?\)', css_content)
        assert len(css_imports) == 0, f"Found external CSS imports: {css_imports}"

        # JS must not load external scripts
        js_fetches = re.findall(r'https?://(?:cdn|unpkg|cdnjs)', js_content)
        assert len(js_fetches) == 0, f"Found external CDN references in hud.js: {js_fetches}"


class TestHUDComponents:
    def test_dom_structure(self, hud_dir: Path):
        html = (hud_dir / "index.html").read_text(encoding="utf-8")

        # Required HUD components per specification (Command Center V2)
        required_ids = [
            "boot-overlay",
            "btn-skip-boot",
            "clock-display",
            "cmd-modal",
            "cmd-palette-input",
            "approvals-drawer",
            "foot-identity",
            "foot-badges",
            "tab-home",
            "tab-ai",
            "tab-system",
            "tab-agents",
            "tab-files",
            "tab-security",
            "tab-apps",
            "tab-settings",
            "main-workspace",
        ]
        for elem_id in required_ids:
            assert f'id="{elem_id}"' in html, f"Missing required HUD element id='{elem_id}'"

    def test_css_styling_and_wake_animations(self, hud_dir: Path):
        css = (hud_dir / "hud.css").read_text(encoding="utf-8")
        assert ("--bg-dark:" in css or "--bg-primary:" in css)
        assert ("--cyan-accent:" in css or "--accent-cyan:" in css)
        assert "@keyframes" in css
        assert ".boot-overlay" in css

    def test_javascript_event_handlers(self, hud_dir: Path):
        js = (hud_dir / "hud.js").read_text(encoding="utf-8")
        assert "fetchIdentityAndBadges" in js
        assert "initNavigation" in js
        assert "initCommandPalette" in js
        assert "initApprovalsDrawer" in js
        assert "fetchMetrics" in js


class TestHUDGatewayServing:
    def test_gateway_serves_hud_assets(self, hud_dir: Path):
        # Find free port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]

        token_mgr = HUDTokenManager(explicit_token="hud_test_token_123")
        server = GatewayServer(host="127.0.0.1", port=port, token_manager=token_mgr, hud_dir=hud_dir)
        server.start()
        time.sleep(0.05)

        try:
            # 1. Fetch /
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/") as resp:
                assert resp.status == 200
                content = resp.read().decode("utf-8")
                assert "LAZY OS" in content
                assert "text/html" in resp.headers.get("Content-Type")

            # 2. Fetch /hud.css
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/hud.css") as resp:
                assert resp.status == 200
                content = resp.read().decode("utf-8")
                assert ("--cyan-accent" in content or "--accent-cyan" in content)
                assert "text/css" in resp.headers.get("Content-Type")

            # 3. Fetch /hud.js
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/hud.js") as resp:
                assert resp.status == 200
                content = resp.read().decode("utf-8")
                assert "fetchIdentityAndBadges" in content
                assert "javascript" in resp.headers.get("Content-Type")

        finally:
            server.stop()
