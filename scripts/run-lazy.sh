#!/usr/bin/env bash
# Lazy OS v2 Boot Script
# Boots Lazy OS guest in QEMU with GTK (if WSLg/X11 available) or headless,
# forwards HUD port (guest 8765 -> host 8766), and writes PID and logs.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_DIR}"

PID_FILE="/tmp/lazy-os.pid"
LOG_FILE="${REPO_DIR}/build-logs/qemu.log"
MONITOR_SOCK="/tmp/lazy-qemu-monitor.sock"

mkdir -p "${REPO_DIR}/build-logs"

# Check if already running
if [ -f "${PID_FILE}" ]; then
    OLD_PID=$(cat "${PID_FILE}" 2>/dev/null || true)
    if [ -n "${OLD_PID}" ] && kill -0 "${OLD_PID}" 2>/dev/null; then
        echo "Lazy OS is already running (PID: ${OLD_PID})."
        echo "URL: http://127.0.0.1:8766/"
        exit 0
    else
        rm -f "${PID_FILE}"
    fi
fi

# Locate kernel and boot images
KERNEL="${REPO_DIR}/dist/bzImage"
if [ ! -f "${KERNEL}" ]; then
    KERNEL="${REPO_DIR}/build/br2-output/images/bzImage"
fi
if [ ! -f "${KERNEL}" ]; then
    KERNEL="/boot/vmlinuz-6.8.0-149-generic"
    if [ ! -f "${KERNEL}" ]; then
        # Fallback to any installed generic kernel
        KERNEL=$(ls -1 /boot/vmlinuz-*-generic 2>/dev/null | sort -V | tail -n 1)
    fi
fi

INITRD="${REPO_DIR}/build/v2/lazy-os-boot.cpio.gz"
DISK="${REPO_DIR}/build/v2/lazy-disk.img"

if [ ! -f "${KERNEL}" ]; then
    echo "ERROR: Kernel image not found: ${KERNEL}" >&2
    exit 1
fi
if [ ! -f "${INITRD}" ]; then
    echo "ERROR: Initrd image not found: ${INITRD}" >&2
    exit 1
fi
if [ ! -f "${DISK}" ]; then
    echo "ERROR: Disk image not found: ${DISK}" >&2
    exit 1
fi

# Check memory requirements (minimum 1024MB required, max half of free RAM)
FREE_MEM_KB=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
if [ "${FREE_MEM_KB}" -lt 1048576 ]; then
    echo "WARNING: Less than 1GB free memory available (${FREE_MEM_KB} kB)." >&2
fi
VM_MEM_MB=1024

# Parse optional command-line arguments
USER_DISPLAY=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --headless|-n)
            USER_DISPLAY="none"
            shift
            ;;
        --display|-d)
            USER_DISPLAY="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Check display: GTK if WSLg / X11 / Wayland is available, else nographic/none
if [ -n "${USER_DISPLAY}" ]; then
    DISPLAY_OPT="-display ${USER_DISPLAY}"
elif [ -n "${WAYLAND_DISPLAY:-}" ] || [ -n "${DISPLAY:-}" ]; then
    DISPLAY_OPT="-display gtk"
else
    DISPLAY_OPT="-display none"
fi

# Check KVM acceleration
KVM_OPT=""
if [ -w /dev/kvm ]; then
    KVM_OPT="-enable-kvm"
fi

echo "=================================================="
echo "          Starting Lazy OS v2 Virtual Machine     "
echo "=================================================="
echo "Kernel:      ${KERNEL}"
echo "Initrd:      ${INITRD}"
echo "Disk:        ${DISK}"
echo "Memory:      ${VM_MEM_MB} MB"
echo "KVM:         ${KVM_OPT:-disabled}"
echo "Display:     ${DISPLAY_OPT}"
echo "HUD Port:    8766 -> 8765 (guest)"
echo "Log File:    ${LOG_FILE}"
echo "=================================================="

# Remove old monitor socket if exists
rm -f "${MONITOR_SOCK}"

# Launch QEMU detached in background
setsid nohup qemu-system-x86_64 \
    ${KVM_OPT} \
    -m "${VM_MEM_MB}" \
    -smp 2 \
    -kernel "${KERNEL}" \
    -initrd "${INITRD}" \
    -drive file="${DISK}",format=raw,if=virtio \
    -append "console=ttyS0 console=tty0 quiet panic=1 lazy_interactive=1" \
    ${DISPLAY_OPT} \
    -serial file:"${REPO_DIR}/build-logs/serial.log" \
    -monitor unix:"${MONITOR_SOCK}",server,nowait \
    -net user,hostfwd=tcp::8766-:8765 -net nic,model=virtio \
    < /dev/null > "${LOG_FILE}" 2>&1 &

QEMU_PID=$!
disown -h ${QEMU_PID} 2>/dev/null || true
echo "${QEMU_PID}" > "${PID_FILE}"

echo "Lazy OS started with PID: ${QEMU_PID}"

# Wait up to 10 seconds for port 8766 to become ready
echo -n "Waiting for Lazy OS Command Center..."
READY=0
for i in $(seq 1 30); do
    if curl -s -f http://127.0.0.1:8766/api/identity >/dev/null 2>&1; then
        READY=1
        break
    fi
    # Check if QEMU died
    if ! kill -0 "${QEMU_PID}" 2>/dev/null; then
        echo " FAILED."
        echo "QEMU terminated unexpectedly. See logs at ${LOG_FILE}:"
        tail -n 20 "${LOG_FILE}"
        rm -f "${PID_FILE}"
        exit 1
    fi
    echo -n "."
    sleep 0.5
done

if [ "${READY}" -eq 1 ]; then
    echo " READY!"
    echo ""
    echo "=================================================="
    echo " Lazy OS v2 Command Center is online:"
    echo "   URL: http://127.0.0.1:8766/"
    echo "=================================================="
else
    echo " VM booted (port check timed out, gateway still initializing)."
    echo "   Check: http://127.0.0.1:8766/"
fi
