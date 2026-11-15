"""Unit tests for lazy-brokers (fs, sys, hw) (Rule F1, F2).

Exit criteria M1.4:
- every capability has a manifest, a handler and tests.
- sys has systemd client wrapper plus fake for tests.
- hw has sysfs with injectable root and fake sysfs fixtures.
"""

from pathlib import Path
import pytest

from lazy.brokers import (
    BaseBroker,
    BrokerExecutionError,
    FakeSystemdClient,
    FSBroker,
    HWBroker,
    SysBroker,
)
from lazy.policy.manifest import ManifestLoader

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def manifest_loader():
    return ManifestLoader([REPO_ROOT / "config" / "capabilities"])


# ==============================================================================
# 1. MANIFEST & HANDLER MAPPING COMPLETENESS
# ==============================================================================

def test_every_broker_capability_has_manifest_and_handler(manifest_loader: ManifestLoader, tmp_path: Path):
    """[M1.4 Exit Criterion] Verify every capability has a manifest and a registered broker handler."""
    fs_broker = FSBroker(tmp_path / "fs_root")
    sys_broker = SysBroker()
    hw_broker = HWBroker(tmp_path / "sysfs_root")

    fs_caps = [
        "fs.read", "fs.list", "fs.write", "fs.copy", "fs.move", "fs.delete",
        "doc.create_markdown", "doc.create_docx", "code.write"
    ]
    sys_caps = [
        "sys.service_status", "sys.logs_read", "sys.process_list",
        "sys.service_restart", "sys.setting_set", "sys.process_signal"
    ]
    hw_caps = [
        "hw.usb_list", "hw.backlight_set", "hw.volume_set", "hw.rfkill_set",
        "hw.power_profile_set", "hw.governor_set", "hw.usb_authorize"
    ]

    for cap in fs_caps:
        assert manifest_loader.get(cap) is not None, f"Missing manifest for {cap}"
        assert fs_broker.can_handle(cap), f"FSBroker missing handler for {cap}"

    for cap in sys_caps:
        assert manifest_loader.get(cap) is not None, f"Missing manifest for {cap}"
        assert sys_broker.can_handle(cap), f"SysBroker missing handler for {cap}"

    for cap in hw_caps:
        assert manifest_loader.get(cap) is not None, f"Missing manifest for {cap}"
        assert hw_broker.can_handle(cap), f"HWBroker missing handler for {cap}"


# ==============================================================================
# 2. FS BROKER TESTS
# ==============================================================================

def test_fs_broker_crud_operations(tmp_path: Path):
    """Test fs.write, fs.read, fs.copy, fs.move, fs.list, fs.delete."""
    root = tmp_path / "fs_data"
    broker = FSBroker(root)

    # 1. Write file
    w_res = broker.execute("fs.write", {"path": "hello.txt", "content": "Hello Lazy OS"})
    assert w_res["status"] == "ok"
    assert (root / "hello.txt").is_file()

    # 2. Read file
    r_res = broker.execute("fs.read", {"path": "hello.txt"})
    assert r_res["status"] == "ok"
    assert r_res["result"]["content"] == "Hello Lazy OS"

    # 3. List directory
    l_res = broker.execute("fs.list", {"path": "."})
    assert l_res["status"] == "ok"
    entries = [e["name"] for e in l_res["result"]["entries"]]
    assert "hello.txt" in entries

    # 4. Copy file
    c_res = broker.execute("fs.copy", {"src": "hello.txt", "dest": "copy.txt"})
    assert c_res["status"] == "ok"
    assert (root / "copy.txt").is_file()

    # 5. Move file
    m_res = broker.execute("fs.move", {"src": "copy.txt", "dest": "moved.txt"})
    assert m_res["status"] == "ok"
    assert not (root / "copy.txt").exists()
    assert (root / "moved.txt").is_file()

    # 6. Delete file
    d_res = broker.execute("fs.delete", {"path": "moved.txt"})
    assert d_res["status"] == "ok"
    assert not (root / "moved.txt").exists()


def test_fs_broker_document_and_code_generation(tmp_path: Path):
    """Test doc.create_markdown, doc.create_docx, code.write."""
    root = tmp_path / "docs"
    broker = FSBroker(root)

    # Markdown
    md_res = broker.execute("doc.create_markdown", {"path": "report", "content": "# Research Report\nContent"})
    assert md_res["status"] == "ok"
    assert (root / "report.md").is_file()

    # Docx
    dx_res = broker.execute("doc.create_docx", {"path": "summary", "content": "Doc summary content"})
    assert dx_res["status"] == "ok"
    assert (root / "summary.docx").is_file()

    # Code
    cd_res = broker.execute("code.write", {"path": "calc.py", "content": "def add(a, b): return a + b\n"})
    assert cd_res["status"] == "ok"
    assert (root / "calc.py").is_file()


def test_fs_broker_error_handling(tmp_path: Path):
    """Test error handling on missing files and invalid paths."""
    broker = FSBroker(tmp_path)
    res = broker.execute("fs.read", {"path": "non_existent_file.xyz"})
    assert res["status"] == "error"
    assert "not found" in res["error"].lower()


# ==============================================================================
# 3. SYS BROKER TESTS
# ==============================================================================

def test_sys_broker_service_lifecycle():
    """Test sys.service_status, sys.service_restart, sys.logs_read."""
    client = FakeSystemdClient()
    broker = SysBroker(client)

    # Service status
    st_res = broker.execute("sys.service_status", {"service": "bluetooth"})
    assert st_res["status"] == "ok"
    assert st_res["result"]["active"] is True
    assert st_res["result"]["pid"] == 1122

    # Service restart
    rs_res = broker.execute("sys.service_restart", {"service": "bluetooth"})
    assert rs_res["status"] == "ok"
    assert rs_res["result"]["restarted"] is True

    # Logs read
    lg_res = broker.execute("sys.logs_read", {"service": "bluetooth", "lines": 5})
    assert lg_res["status"] == "ok"
    assert len(lg_res["result"]["lines"]) > 0


def test_sys_broker_settings_and_process_management():
    """Test sys.setting_set, sys.process_list, sys.process_signal."""
    client = FakeSystemdClient()
    broker = SysBroker(client)

    # Setting set
    set_res = broker.execute("sys.setting_set", {"key": "timezone", "value": "America/New_York"})
    assert set_res["status"] == "ok"
    assert client.settings["timezone"] == "America/New_York"

    # Process list
    pl_res = broker.execute("sys.process_list", {})
    assert pl_res["status"] == "ok"
    pids = [p["pid"] for p in pl_res["result"]["processes"]]
    assert 1144 in pids

    # Process signal
    sig_res = broker.execute("sys.process_signal", {"pid": 1144, "signal": "SIGTERM"})
    assert sig_res["status"] == "ok"
    assert sig_res["result"]["success"] is True
    # Process 1144 removed from active list
    pl2 = broker.execute("sys.process_list", {})
    assert 1144 not in [p["pid"] for p in pl2["result"]["processes"]]


# ==============================================================================
# 4. HW BROKER TESTS (INJECTABLE SYSFS ROOT)
# ==============================================================================

def test_hw_broker_injectable_sysfs_root(tmp_path: Path):
    """Test hw operations with an isolated injectable sysfs fixture."""
    fake_sysfs = tmp_path / "fake_sysfs"
    broker = HWBroker(fake_sysfs)

    # 1. Backlight
    bl_res = broker.execute("hw.backlight_set", {"brightness": 85})
    assert bl_res["status"] == "ok"
    assert bl_res["result"]["new_brightness"] == 85
    brightness_val = (fake_sysfs / "class" / "backlight" / "intel_backlight" / "brightness").read_text().strip()
    assert brightness_val == "85"

    # 2. Volume
    vol_res = broker.execute("hw.volume_set", {"volume": 70})
    assert vol_res["status"] == "ok"
    assert vol_res["result"]["new_volume"] == 70

    # 3. RFKill
    rf_res = broker.execute("hw.rfkill_set", {"subsystem": "wlan", "state": "block"})
    assert rf_res["status"] == "ok"
    wlan_state = (fake_sysfs / "class" / "rfkill" / "rfkill0" / "state").read_text().strip()
    assert wlan_state == "0"  # 0 = blocked

    # 4. Power Profile
    pw_res = broker.execute("hw.power_profile_set", {"profile": "low-power"})
    assert pw_res["status"] == "ok"
    profile_val = (fake_sysfs / "firmware" / "acpi" / "platform_profile").read_text().strip()
    assert profile_val == "low-power"

    # 5. Governor
    gov_res = broker.execute("hw.governor_set", {"governor": "powersave"})
    assert gov_res["status"] == "ok"
    gov_val = (fake_sysfs / "devices" / "system" / "cpu" / "cpu0" / "cpufreq" / "scaling_governor").read_text().strip()
    assert gov_val == "powersave"

    # 6. USB List & Authorize
    usb_res = broker.execute("hw.usb_list", {})
    assert usb_res["status"] == "ok"
    assert usb_res["result"]["count"] >= 1

    auth_res = broker.execute("hw.usb_authorize", {"device_id": "1-1"})
    assert auth_res["status"] == "ok"
    assert auth_res["result"]["authorized"] is True


def test_base_broker_unhandled_capability(tmp_path: Path):
    """Verify BaseBroker raises BrokerExecutionError on unregistered capabilities."""
    broker = FSBroker(tmp_path)
    with pytest.raises(BrokerExecutionError):
        broker.execute("telepathy.read_thoughts", {})
