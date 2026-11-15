"""Unit and integration tests for Lazy OS browser driver interface and fallback (Milestone M5.5).

Verifies:
- BaseBrowserDriver interface compliance.
- PurePythonBrowserDriver (pure-Python sandbox driver).
- WebDriverBrowserDriver (W3C WebDriver client with daemon detection).
- get_browser_driver factory and automatic fallback.
- Quarantine isolation (Rule F9) with 0600 permissions.
"""
from __future__ import annotations

import os
from pathlib import Path
import pytest

from lazy.brokers.web_broker import (
    BaseBrowserDriver,
    PurePythonBrowserDriver,
    WebDriverBrowserDriver,
    IsolatedBrowserDriver,
    get_browser_driver,
    WebBroker,
)


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def test_site_dir(repo_root: Path) -> Path:
    return repo_root / "tests" / "fixtures" / "website"


class TestBrowserDriverInterface:
    def test_pure_python_driver_implements_interface(self, test_site_dir: Path, tmp_path: Path):
        driver = PurePythonBrowserDriver(quarantine_dir=tmp_path / "quarantine")
        assert isinstance(driver, BaseBrowserDriver)
        assert driver.driver_name == "pure_python"

        # Test local fixture navigation
        dom = driver.navigate(f"file://{test_site_dir / 'index.html'}")
        assert dom.title == "Lazy OS Test Portal"
        assert len(dom.links) >= 3

        # Test form fill and submit
        driver.navigate(f"file://{test_site_dir / 'login.html'}")
        fill_res = driver.fill("user_input", "admin")
        assert fill_res["action"] == "fill"
        submit_res = driver.submit("login_form")
        assert submit_res["status"] == "submitted"
        assert submit_res["submitted_fields"]["user_input"] == "admin"

    def test_webdriver_driver_implements_interface(self, tmp_path: Path):
        driver = WebDriverBrowserDriver(
            quarantine_dir=tmp_path / "quarantine",
            webdriver_url="http://127.0.0.1:19999",  # Unbound port
        )
        assert isinstance(driver, BaseBrowserDriver)
        assert driver.driver_name == "webdriver"
        # Daemon is not reachable on unbound port
        assert driver.is_daemon_reachable() is False

    def test_webdriver_graceful_fallback_for_local_files(self, test_site_dir: Path, tmp_path: Path):
        driver = WebDriverBrowserDriver(
            quarantine_dir=tmp_path / "quarantine",
            webdriver_url="http://127.0.0.1:19999",
        )
        # Should gracefully use fallback for file:// navigation without crash
        dom = driver.navigate(f"file://{test_site_dir / 'index.html'}")
        assert dom.title == "Lazy OS Test Portal"

    def test_get_browser_driver_factory(self, tmp_path: Path):
        # Auto fallback when daemon not running
        d_auto = get_browser_driver(
            driver_type="auto",
            quarantine_dir=tmp_path / "quarantine",
            webdriver_url="http://127.0.0.1:19999",
        )
        assert isinstance(d_auto, PurePythonBrowserDriver)
        assert d_auto.driver_name == "pure_python"

        # Explicit pure_python
        d_pure = get_browser_driver(driver_type="pure_python", quarantine_dir=tmp_path / "quarantine")
        assert isinstance(d_pure, PurePythonBrowserDriver)

        # Explicit webdriver
        d_wd = get_browser_driver(
            driver_type="webdriver",
            quarantine_dir=tmp_path / "quarantine",
            webdriver_url="http://127.0.0.1:19999",
        )
        assert isinstance(d_wd, WebDriverBrowserDriver)

    def test_quarantine_isolation_permissions(self, test_site_dir: Path, tmp_path: Path):
        quarantine = tmp_path / "quarantine"
        driver = PurePythonBrowserDriver(quarantine_dir=quarantine)
        download_url = f"file://{test_site_dir / 'downloadable.txt'}"

        res = driver.download_to_quarantine(download_url, "test_download.txt")
        assert res["quarantined"] is True
        assert res["permissions"] == "0600"

        saved_file = quarantine / "test_download.txt"
        assert saved_file.is_file()
        # Verify file mode on POSIX systems
        if os.name == "posix":
            mode = oct(saved_file.stat().st_mode & 0o777)
            assert mode == "0o600"
