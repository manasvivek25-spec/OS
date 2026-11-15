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

        # Required HUD components per specification
        required_ids = [
            "status-strip",
            "metric-cpu",
            "metric-ram",
            "metric-model",
            "metric-mode",
            "metric-net",
            "plan-panel",
            "plan-status",
            "plan-rationale",
            "steps-list",
            "transcript-panel",
            "transcript-feed",
            "input-form",
            "user-input",
            "approvals-panel",
            "active-approval",
            "appr-tier",
            "appr-cap",
            "appr-reason",
            "appr-diff",
            "btn-approve",
            "btn-deny",
            "wake-animation",
        ]
        for elem_id in required_ids:
            assert f'id="{elem_id}"' in html, f"Missing required HUD element id='{elem_id}'"

    def test_css_styling_and_wake_animations(self, hud_dir: Path):
        css = (hud_dir / "hud.css").read_text(encoding="utf-8")
        assert "--bg-dark:" in css
        assert "--accent-cyan:" in css
        assert "@keyframes spin-clockwise" in css
        assert "@keyframes pulse-glow" in css
        assert ".wake-animation-overlay" in css

    def test_javascript_event_handlers(self, hud_dir: Path):
        js = (hud_dir / "hud.js").read_text(encoding="utf-8")
        assert "transcript_update" in js
        assert "plan_view" in js
        assert "step_update" in js
        assert "approval_request" in js
        assert "system_metric" in js
        assert "triggerWakeAnimation" in js


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
                assert "LAZY OS // HUD" in content
                assert "text/html" in resp.headers.get("Content-Type")

            # 2. Fetch /hud.css
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/hud.css") as resp:
                assert resp.status == 200
                content = resp.read().decode("utf-8")
                assert "--accent-cyan" in content
                assert "text/css" in resp.headers.get("Content-Type")

            # 3. Fetch /hud.js
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/hud.js") as resp:
                assert resp.status == 200
                content = resp.read().decode("utf-8")
                assert "Lazy OS Futuristic HUD Controller" in content
                assert "javascript" in resp.headers.get("Content-Type")

        finally:
            server.stop()
