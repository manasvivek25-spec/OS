#!/usr/bin/env bash
# Lazy OS Standalone Run Script (Linux & WSL2)
# Specification: docs/acceptance/ACCEPTANCE.md (P1, P7)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DISK="${SCRIPT_DIR}/lazy-os.img"
if [ ! -f "${DISK}" ]; then
    DISK="${REPO_ROOT}/build/v2/lazy-disk.img"
fi

KERNEL="${REPO_ROOT}/build/br2-output/images/bzImage"
if [ ! -f "${KERNEL}" ]; then
    KERNEL="/boot/vmlinuz-6.8.0-149-generic"
    if [ ! -f "${KERNEL}" ]; then
        KERNEL=$(ls -1 /boot/vmlinuz-*-generic 2>/dev/null | sort -V | tail -n 1)
    fi
fi

INITRD="${REPO_ROOT}/build/br2-output/images/rootfs.cpio.gz"
if [ ! -f "${INITRD}" ]; then
    INITRD="${REPO_ROOT}/build/v2/lazy-os-boot.cpio.gz"
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
    -initrd "${INITRD}" \
    -drive file="${DISK}",format=raw,if=virtio \
    -append "console=ttyS0 console=tty0 quiet lazy_interactive=1" \
    ${DISPLAY_OPT} \
    -device virtio-gpu-pci \
    -device virtio-keyboard-pci \
    -device virtio-tablet-pci \
    -net user,hostfwd=tcp::8766-:8765 -net nic,model=virtio
