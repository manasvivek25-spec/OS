# Hardware Control Architecture (lazy-broker-hw)

## Subsystem Interfaces
Lazy OS controls laptop hardware via kernel sysfs nodes and ALSA interfaces through an injectable root abstraction (`LAZY_SYSFS_ROOT`), enabling complete fixture testing in CI and development environments.

### 1. Display Backlight (`hw.backlight_set`)
- **Sysfs Path**: `/sys/class/backlight/<device>/brightness`, `max_brightness`
- **Tier**: L1
- **Undo Strategy**: Revert to recorded previous brightness level.

### 2. Audio Volume (`hw.volume_set`)
- **Control**: ALSA mixer controls (`amixer`) or `/sys/class/sound`
- **Tier**: L1
- **Undo Strategy**: Revert to recorded previous volume level.

### 3. RFKill (`hw.rfkill_set`)
- **Sysfs Path**: `/sys/class/rfkill/rfkill*/state` or `rfkill` utility
- **Tier**: L2
- **Parameters**: `subsystem` (wlan, bluetooth, all), `state` (block, unblock)
- **Undo Strategy**: Revert to previous rfkill mask.

### 4. CPU Power Profile & Governor (`hw.power_profile_set`, `hw.governor_set`)
- **Sysfs Path**: `/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor`, `/sys/firmware/acpi/platform_profile`
- **Tier**: L2
- **Parameters**: `governor` (performance, powersave, schedutil), `profile` (low-power, balanced, performance)
- **Undo Strategy**: Compensable restoration of prior governor.

### 5. USB Devices (`hw.usb_list`, `hw.usb_authorize`)
- **Sysfs Path**: `/sys/bus/usb/devices/*/authorized`
- **Tier**: L0 (`hw.usb_list`), L3 (`hw.usb_authorize`)
- **Security Policy**: USBGuard integration and per-device authorization toggle.
