"""Hardware control broker with injectable sysfs root for Lazy OS (lazy-broker-hw)."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from lazy.brokers.base import BaseBroker, BrokerExecutionError


class HWBroker(BaseBroker):
    """Controls laptop display, sound, rfkill, CPU power, and USB devices."""

    def __init__(self, sysfs_root: Optional[Path | str] = None):
        super().__init__("lazy-broker-hw")
        root = sysfs_root or os.environ.get("LAZY_SYSFS_ROOT", "/sys")
        self.sysfs_root = Path(root)
        self._init_sysfs_structure()
        self._register_handlers()

    def _init_sysfs_structure(self) -> None:
        """Ensure standard sysfs nodes exist if working in a fixture root."""
        if self.sysfs_root != Path("/sys"):
            # Create mock structure
            (self.sysfs_root / "class" / "backlight" / "intel_backlight").mkdir(parents=True, exist_ok=True)
            (self.sysfs_root / "class" / "backlight" / "intel_backlight" / "max_brightness").write_text("100\n")
            (self.sysfs_root / "class" / "backlight" / "intel_backlight" / "brightness").write_text("50\n")

            (self.sysfs_root / "class" / "sound" / "card0").mkdir(parents=True, exist_ok=True)
            (self.sysfs_root / "class" / "sound" / "card0" / "volume").write_text("50\n")

            (self.sysfs_root / "class" / "rfkill" / "rfkill0").mkdir(parents=True, exist_ok=True)
            (self.sysfs_root / "class" / "rfkill" / "rfkill0" / "type").write_text("wlan\n")
            (self.sysfs_root / "class" / "rfkill" / "rfkill0" / "state").write_text("1\n") # 1 = unblocked

            (self.sysfs_root / "class" / "rfkill" / "rfkill1").mkdir(parents=True, exist_ok=True)
            (self.sysfs_root / "class" / "rfkill" / "rfkill1" / "type").write_text("bluetooth\n")
            (self.sysfs_root / "class" / "rfkill" / "rfkill1" / "state").write_text("1\n")

            (self.sysfs_root / "firmware" / "acpi").mkdir(parents=True, exist_ok=True)
            (self.sysfs_root / "firmware" / "acpi" / "platform_profile").write_text("balanced\n")

            (self.sysfs_root / "devices" / "system" / "cpu" / "cpu0" / "cpufreq").mkdir(parents=True, exist_ok=True)
            (self.sysfs_root / "devices" / "system" / "cpu" / "cpu0" / "cpufreq" / "scaling_governor").write_text("schedutil\n")

            (self.sysfs_root / "bus" / "usb" / "devices" / "1-1").mkdir(parents=True, exist_ok=True)
            (self.sysfs_root / "bus" / "usb" / "devices" / "1-1" / "authorized").write_text("1\n")
            (self.sysfs_root / "bus" / "usb" / "devices" / "1-1" / "product").write_text("Integrated Webcam\n")

    def _register_handlers(self) -> None:
        self.register("hw.usb_list", self.handle_usb_list)
        self.register("hw.backlight_set", self.handle_backlight_set)
        self.register("hw.volume_set", self.handle_volume_set)
        self.register("hw.rfkill_set", self.handle_rfkill_set)
        self.register("hw.power_profile_set", self.handle_power_profile_set)
        self.register("hw.governor_set", self.handle_governor_set)
        self.register("hw.usb_authorize", self.handle_usb_authorize)

    def handle_usb_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        usb_dir = self.sysfs_root / "bus" / "usb" / "devices"
        devices = []
        if usb_dir.is_dir():
            for dev in sorted(usb_dir.iterdir()):
                auth_file = dev / "authorized"
                prod_file = dev / "product"
                auth = auth_file.read_text().strip() if auth_file.is_file() else "1"
                prod = prod_file.read_text().strip() if prod_file.is_file() else "Generic USB Device"
                devices.append({
                    "device_id": dev.name,
                    "product": prod,
                    "authorized": (auth == "1"),
                })
        return {"devices": devices, "count": len(devices)}

    def handle_backlight_set(self, params: Dict[str, Any]) -> Dict[str, Any]:
        brightness = params["brightness"]
        bl_dir = self.sysfs_root / "class" / "backlight"
        if not bl_dir.is_dir():
            return {"brightness": brightness, "device": "none", "applied": False}

        dev = next(bl_dir.iterdir(), None)
        if dev is None:
            return {"brightness": brightness, "device": "none", "applied": False}

        b_file = dev / "brightness"
        old_val = b_file.read_text().strip() if b_file.is_file() else "0"
        b_file.write_text(f"{brightness}\n")
        return {"device": dev.name, "old_brightness": int(old_val), "new_brightness": brightness, "applied": True}

    def handle_volume_set(self, params: Dict[str, Any]) -> Dict[str, Any]:
        vol = params["volume"]
        vol_file = self.sysfs_root / "class" / "sound" / "card0" / "volume"
        old_vol = 50
        if vol_file.is_file():
            try:
                old_vol = int(vol_file.read_text().strip())
            except Exception:
                pass
            vol_file.write_text(f"{vol}\n")
        return {"old_volume": old_vol, "new_volume": vol, "applied": True}

    def handle_rfkill_set(self, params: Dict[str, Any]) -> Dict[str, Any]:
        subsystem = params["subsystem"]
        state = params["state"] # "block" or "unblock"
        state_code = "0\n" if state == "block" else "1\n"

        rf_dir = self.sysfs_root / "class" / "rfkill"
        applied_to = []
        if rf_dir.is_dir():
            for dev in rf_dir.iterdir():
                type_file = dev / "type"
                if type_file.is_file():
                    dev_type = type_file.read_text().strip()
                    if subsystem == "all" or dev_type == subsystem:
                        s_file = dev / "state"
                        if s_file.is_file():
                            s_file.write_text(state_code)
                            applied_to.append(dev.name)
        return {"subsystem": subsystem, "state": state, "devices_affected": applied_to}

    def handle_power_profile_set(self, params: Dict[str, Any]) -> Dict[str, Any]:
        profile = params["profile"]
        p_file = self.sysfs_root / "firmware" / "acpi" / "platform_profile"
        old = "balanced"
        if p_file.is_file():
            old = p_file.read_text().strip()
            p_file.write_text(f"{profile}\n")
        return {"old_profile": old, "new_profile": profile, "applied": True}

    def handle_governor_set(self, params: Dict[str, Any]) -> Dict[str, Any]:
        gov = params["governor"]
        cpu_dir = self.sysfs_root / "devices" / "system" / "cpu"
        cpus_updated = 0
        if cpu_dir.is_dir():
            for cpu in cpu_dir.glob("cpu[0-9]*"):
                gov_file = cpu / "cpufreq" / "scaling_governor"
                if gov_file.is_file():
                    gov_file.write_text(f"{gov}\n")
                    cpus_updated += 1
        return {"governor": gov, "cpus_updated": cpus_updated}

    def handle_usb_authorize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dev_id = params["device_id"]
        auth_file = self.sysfs_root / "bus" / "usb" / "devices" / dev_id / "authorized"
        if not auth_file.is_file():
            raise FileNotFoundError(f"USB device '{dev_id}' not found.")
        auth_file.write_text("1\n")
        return {"device_id": dev_id, "authorized": True}
