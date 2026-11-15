# Lazy OS Hardware Control Architecture (`lazy-broker-hw`)

## 1. Overview
Lazy OS controls laptop hardware through direct Linux kernel sysfs interfaces and ALSA mixer APIs. To ensure 100% testability across CI, development containers, and QEMU, the hardware broker (`HWBroker`) uses an injectable root abstraction (`LAZY_SYSFS_ROOT`).

When `LAZY_SYSFS_ROOT` is unset, the broker interacts with the live `/sys` filesystem. During tests, the environment variable points to a synthetic mock tree (e.g. `tests/fixtures/fake_sysfs/`), enabling deterministic verification without modifying host hardware.

---

## 2. Supported Hardware Capabilities & Sysfs Mapping

### A. Display Backlight (`hw.backlight_set`)
- **Capability Tier**: Tier L1 (Automatic, Reversible)
- **Live Sysfs Paths**:
  - Current brightness: `/sys/class/backlight/<device>/brightness`
  - Maximum brightness: `/sys/class/backlight/<device>/max_brightness`
- **Parameter Validation**: Brightness percentage integer ($0 \le \text{percent} \le 100$).
- **Undo Strategy**: Automatically records previous brightness level and restores on rollback.

### B. Audio Volume & Mute (`hw.volume_set`)
- **Capability Tier**: Tier L1 (Automatic, Reversible)
- **Interface**: ALSA mixer controls (`amixer set Master <pct>%`) or sysfs audio driver state.
- **Parameter Validation**: Volume percentage integer ($0 \le \text{percent} \le 100$).
- **Undo Strategy**: Reverts to prior master volume level.

### C. Wireless Radio Control (`hw.rfkill_set`)
- **Capability Tier**: Tier L2 (Approval Required, Compensable)
- **Live Sysfs Paths**:
  - Device state: `/sys/class/rfkill/rfkill*/state`
  - Device type: `/sys/class/rfkill/rfkill*/type` (wlan, bluetooth)
- **Values**: `0` = blocked (soft-disabled), `1` = unblocked (active).
- **Undo Strategy**: Restores prior rfkill bitmask for specified subsystem.

### D. CPU Frequency Governors & Power Profiles (`hw.governor_set`, `hw.power_profile_set`)
- **Capability Tier**: Tier L2 (Approval Required, Compensable)
- **Live Sysfs Paths**:
  - Governor: `/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor`
  - Available governors: `/sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors`
  - ACPI profile: `/sys/firmware/acpi/platform_profile`
- **Supported Governors**: `performance`, `powersave`, `schedutil`, `ondemand`.
- **Supported Profiles**: `low-power`, `balanced`, `performance`.
- **Undo Strategy**: Restores prior governor string across all online CPU cores.

### E. USB Devices & Authorization (`hw.usb_list`, `hw.usb_authorize`)
- **Capability Tier**:
  - `hw.usb_list`: Tier L0 (Read-Only)
  - `hw.usb_authorize`: Tier L3 (Explicit User Confirmation & Diff Preview)
- **Live Sysfs Paths**:
  - Device enumeration: `/sys/bus/usb/devices/*/`
  - Authorization toggle: `/sys/bus/usb/devices/<dev>/authorized` (`0` = deauthorized, `1` = authorized)
- **Security Policy**: Prevents unauthorized USB BadUSB or Rubber Ducky attacks by requiring explicit physical authorization confirmation.

---

## 3. Systemd Sandboxing & Least Privilege
The hardware broker unit [`systemd/lazy-broker-hw.service`](file:///c:/Users/len/OS/systemd/lazy-broker-hw.service) enforces strict privilege boundaries:

```ini
[Service]
User=lazy-brk-hw
Group=lazy-brk-hw
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
ProtectKernelModules=yes
ProtectControlGroups=yes
RestrictRealtime=yes
RestrictSUIDSGID=yes
RestrictAddressFamilies=AF_UNIX
SystemCallFilter=@system-service ~@privileged ~@resources

# Specific writable kernel tunables
ProtectKernelTunables=yes
ReadWritePaths=/sys/class/backlight /sys/class/rfkill /sys/devices/system/cpu
```

---

## 4. Test Verification
All hardware broker capabilities are verified with deterministic mock fixtures in [`tests/unit/test_brokers.py`](file:///c:/Users/len/OS/tests/unit/test_brokers.py):
- Backlight setting, clamping, and error handling.
- Volume setting and mute toggles.
- RFKILL soft blocking and unblocking.
- CPU governor transitions.
- USB device listing and authorization enforcement.
