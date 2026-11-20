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

# Auto-detect WSLg display if not explicitly exported in subshell
if [ -z "${DISPLAY:-}" ] && [ -e /tmp/.X11-unix/X0 ]; then
    export DISPLAY=:0
fi
if [ -z "${WAYLAND_DISPLAY:-}" ] && [ -e /mnt/wslg/runtime-dir/wayland-0 ]; then
    export WAYLAND_DISPLAY=wayland-0
    export XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir
fi

if [ -n "${USER_DISPLAY}" ]; then
    DISPLAY_OPT="-display ${USER_DISPLAY}"
elif [ -n "${WAYLAND_DISPLAY:-}" ] || [ -n "${DISPLAY:-}" ]; then
    DISPLAY_OPT="-display gtk,zoom-to-fit=on"
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
    -append "console=ttyS0 console=tty0 root=/dev/vda2 ro rootwait quiet lazy_interactive=1" \
    ${DISPLAY_OPT} \
    -vga none \
    -device virtio-gpu-pci,id=gpu0 \
    -device virtio-keyboard-pci \
    -device virtio-tablet-pci \
    -monitor unix:/tmp/qemu-monitor.sock,server,nowait \
    -serial unix:/tmp/qemu-serial.sock,server,nowait \
    -netdev user,id=net0,hostfwd=tcp::8766-:8765 -device virtio-net-pci,netdev=net0
