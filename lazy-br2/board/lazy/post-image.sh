#!/usr/bin/env bash
# Lazy OS Buildroot Post-Image Script
# Packages UEFI bootloader, kernel bzImage, SquashFS root, and Btrfs data partition via genimage

set -euo pipefail

BINARIES_DIR="$1"
BOARD_DIR="$(dirname "$0")"
HOST_DIR="${HOST_DIR:-$(dirname "${BINARIES_DIR}")/host}"
export PATH="${HOST_DIR}/sbin:${HOST_DIR}/bin:${PATH}"
GENIMAGE_CFG="${BOARD_DIR}/genimage.cfg"
ROOTPATH_TMP="$(mktemp -d)"
GENIMAGE_TMP="$(mktemp -d)"
trap 'rm -rf "${ROOTPATH_TMP}" "${GENIMAGE_TMP}"' EXIT

echo "=== Lazy OS Post-Image: Assembling UEFI Disk Image ==="

mkdir -p "${BINARIES_DIR}/efi-part/EFI/BOOT"

# Install kernel as default UEFI boot target or via systemd-boot
if [ -f "${BINARIES_DIR}/bzImage" ]; then
    cp "${BINARIES_DIR}/bzImage" "${BINARIES_DIR}/efi-part/EFI/BOOT/bootx64.efi"
fi

cat << 'EOF' > "${BINARIES_DIR}/efi-part/startup.nsh"
\EFI\BOOT\bootx64.efi console=ttyS0 console=tty0 root=/dev/vda2 ro rootwait quiet
EOF

# Create persistent Btrfs data partition image
truncate -s 256M "${BINARIES_DIR}/lazy-data.btrfs"
"${HOST_DIR}/bin/mkfs.btrfs" -f -L "LAZY_DATA" "${BINARIES_DIR}/lazy-data.btrfs"

genimage \
    --rootpath "${ROOTPATH_TMP}" \
    --tmppath "${GENIMAGE_TMP}" \
    --inputpath "${BINARIES_DIR}" \
    --outputpath "${BINARIES_DIR}" \
    --config "${GENIMAGE_CFG}"

echo "=== Disk image created at ${BINARIES_DIR}/lazy-os.img ==="
