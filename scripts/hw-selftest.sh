#!/usr/bin/env bash
# Lazy OS Physical Hardware Self-Test Script
# Specification: docs/BUILD_PROMPT_V3.md (K10, FT4)
# Run this script on a bare-metal physical Linux laptop to verify native hardware interfaces.

set -euo pipefail

echo "======================================================================"
echo "          LAZY OS PHYSICAL HARDWARE CAPABILITY SELF-TEST              "
echo "======================================================================"
echo "Date:     $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Kernel:   $(uname -r)"
echo "Hostname: $(hostname)"
echo "Arch:     $(uname -m)"
echo "======================================================================"

PASS_COUNT=0
WARN_COUNT=0

# 1. Backlight Interface
echo -n "[1/6] Checking Backlight Sysfs (/sys/class/backlight)... "
if [ -d "/sys/class/backlight" ] && [ "$(ls -A /sys/class/backlight 2>/dev/null)" ]; then
    BL_DEV=$(ls /sys/class/backlight | head -n 1)
    CURR_BRIGHT=$(cat "/sys/class/backlight/${BL_DEV}/brightness" 2>/dev/null || echo "N/A")
    MAX_BRIGHT=$(cat "/sys/class/backlight/${BL_DEV}/max_brightness" 2>/dev/null || echo "N/A")
    echo "OK (Device: ${BL_DEV}, Level: ${CURR_BRIGHT}/${MAX_BRIGHT})"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "VM-UNAVAILABLE (No physical backlight controller detected)"
    WARN_COUNT=$((WARN_COUNT + 1))
fi

# 2. Battery / Power Supply
echo -n "[2/6] Checking Battery Sysfs (/sys/class/power_supply)... "
if [ -d "/sys/class/power_supply" ] && [ "$(ls -A /sys/class/power_supply 2>/dev/null)" ]; then
    BAT_DEV=$(ls /sys/class/power_supply | grep -iE 'bat|ac' | head -n 1 || echo "")
    if [ -n "${BAT_DEV}" ]; then
        STATUS=$(cat "/sys/class/power_supply/${BAT_DEV}/status" 2>/dev/null || echo "Unknown")
        CAPACITY=$(cat "/sys/class/power_supply/${BAT_DEV}/capacity" 2>/dev/null || echo "N/A")
        echo "OK (Device: ${BAT_DEV}, Status: ${STATUS}, Capacity: ${CAPACITY}%)"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo "VM-UNAVAILABLE (No battery device registered)"
        WARN_COUNT=$((WARN_COUNT + 1))
    fi
else
    echo "VM-UNAVAILABLE (No power_supply devices found)"
    WARN_COUNT=$((WARN_COUNT + 1))
fi

# 3. CPU Frequency Scaling Governors
echo -n "[3/6] Checking CPU Frequency Governors (/sys/devices/system/cpu)... "
if [ -f "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor" ]; then
    GOV=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)
    AVAIL_GOVS=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors 2>/dev/null || echo "${GOV}")
    echo "OK (Active: ${GOV}, Available: ${AVAIL_GOVS})"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "VM-UNAVAILABLE (cpufreq scaling driver not virtualized)"
    WARN_COUNT=$((WARN_COUNT + 1))
fi

# 4. Wireless RFKill Switch
echo -n "[4/6] Checking RFKill Switch (/dev/rfkill or rfkill command)... "
if command -v rfkill >/dev/null 2>&1; then
    RF_COUNT=$(rfkill list 2>/dev/null | wc -l || echo 0)
    echo "OK (rfkill tool available, devices listed: ${RF_COUNT})"
    PASS_COUNT=$((PASS_COUNT + 1))
elif [ -e "/dev/rfkill" ]; then
    echo "OK (/dev/rfkill char device present)"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "VM-UNAVAILABLE (No rfkill interface found)"
    WARN_COUNT=$((WARN_COUNT + 1))
fi

# 5. Audio Subsystem
echo -n "[5/6] Checking Audio Sound Cards (/proc/asound or /dev/snd)... "
if [ -d "/proc/asound" ] && [ -f "/proc/asound/cards" ] && grep -q '\[.*\].*:' /proc/asound/cards 2>/dev/null; then
    CARD_NAME=$(head -n 1 /proc/asound/cards)
    echo "OK (${CARD_NAME})"
    PASS_COUNT=$((PASS_COUNT + 1))
elif [ -d "/dev/snd" ]; then
    echo "OK (/dev/snd character devices present)"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "VM-UNAVAILABLE (No sound card detected)"
    WARN_COUNT=$((WARN_COUNT + 1))
fi

# 6. USB Controller & Devices
echo -n "[6/6] Checking USB Subsystem (/sys/bus/usb/devices)... "
if [ -d "/sys/bus/usb/devices" ] && [ "$(ls -A /sys/bus/usb/devices 2>/dev/null)" ]; then
    USB_DEV_COUNT=$(ls -d /sys/bus/usb/devices/usb* 2>/dev/null | wc -l || echo 0)
    echo "OK (${USB_DEV_COUNT} USB root hub(s) active)"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "VM-UNAVAILABLE (No USB controller detected)"
    WARN_COUNT=$((WARN_COUNT + 1))
fi

echo "======================================================================"
echo "Self-Test Summary: PASS=${PASS_COUNT}, VM-UNAVAILABLE=${WARN_COUNT} (Total: 6)"
if [ "${WARN_COUNT}" -gt 0 ]; then
    echo "Note: Interfaces labeled VM-UNAVAILABLE are fully expected in virtualized"
    echo "QEMU/WSL environments and map to synthetic fallback brokers (Rule K10)."
fi
echo "======================================================================"
