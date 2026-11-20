#!/usr/bin/env bash
# Lazy OS Standalone Run Script (Linux & WSL2)
# Specification: docs/acceptance/ACCEPTANCE.md (P1, P7)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DISK="${SCRIPT_DIR}/lazy-os.img"
if [ ! -f "${DISK}" ]; then
    DISK="${REPO_ROOT}/dist/lazy-os.img"
fi

KERNEL="${SCRIPT_DIR}/bzImage"
if [ ! -f "${KERNEL}" ]; then
    KERNEL="${REPO_ROOT}/dist/bzImage"
fi

USER_DISPLAY=""
FULLSCREEN_REQ=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --headless|-n)
            USER_DISPLAY="none"
            shift
            ;;
        --fullscreen|-f)
            FULLSCREEN_REQ=1
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

# Auto-detect WSLg display if not explicitly exported in subshell
if [ -z "${DISPLAY:-}" ] && [ -e /tmp/.X11-unix/X0 ]; then
    export DISPLAY=:0
fi
if [ -z "${WAYLAND_DISPLAY:-}" ] && [ -e /mnt/wslg/runtime-dir/wayland-0 ]; then
    export WAYLAND_DISPLAY=wayland-0
    export XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir
fi

# Prefer X11 backend for GTK under WSLg to avoid Wayland seat grab assertion failures
# and ensure the host window receives mouse selection, focus, and titlebar controls cleanly
export GDK_BACKEND=x11

if [ -n "${USER_DISPLAY}" ]; then
    DISPLAY_OPT="-display ${USER_DISPLAY}"
elif [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]; then
    DISPLAY_OPT="-display gtk,zoom-to-fit=on,show-menubar=on"
    if [ "${FULLSCREEN_REQ}" -eq 1 ]; then
        DISPLAY_OPT="${DISPLAY_OPT},full-screen=on"
    fi
else
    DISPLAY_OPT="-display none"
fi

KVM_OPT=""
if [ -w /dev/kvm ]; then
    KVM_OPT="-enable-kvm"
fi

echo "=================================================="
echo "          Starting Lazy OS v3 Product             "
echo "=================================================="
echo "Disk:        ${DISK}"
echo "Display:     ${DISPLAY_OPT}"
echo "HUD Gateway: http://127.0.0.1:8766/"
echo "=================================================="

exec qemu-system-x86_64 \
    ${KVM_OPT} \
    -m 2048 \
    -smp 2 \
    -kernel "${KERNEL}" \
    -drive file="${DISK}",format=raw,if=virtio \
    -append "console=ttyS0 console=tty0 root=/dev/vda2 ro rootwait quiet lazy_interactive=1 video=1920x1080" \
    ${DISPLAY_OPT} \
    -vga none \
    -device virtio-gpu-pci,id=gpu0,xres=1920,yres=1080 \
    -device virtio-keyboard-pci \
    -device virtio-tablet-pci \
    -monitor unix:/tmp/qemu-monitor.sock,server,nowait \
    -serial unix:/tmp/qemu-serial.sock,server,nowait \
    -netdev user,id=net0,hostfwd=tcp::8766-:8765 -device virtio-net-pci,netdev=net0
