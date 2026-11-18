#!/usr/bin/env bash
# Lazy OS Buildroot Post-Image Script
# Packages UEFI bootloader, kernel bzImage, SquashFS root, and Btrfs data partition via genimage

set -euo pipefail

BINARIES_DIR="$1"
BOARD_DIR="$(dirname "$0")"
GENIMAGE_CFG="${BOARD_DIR}/genimage.cfg"
GENIMAGE_TMP="${BINARIES_DIR}/genimage.tmp"

echo "=== Lazy OS Post-Image: Assembling UEFI Disk Image ==="

mkdir -p "${BINARIES_DIR}/efi-part/EFI/BOOT"

# Install kernel as default UEFI boot target or via systemd-boot
if [ -f "${BINARIES_DIR}/bzImage" ]; then
    cp "${BINARIES_DIR}/bzImage" "${BINARIES_DIR}/efi-part/EFI/BOOT/bootx64.efi"
fi

cat << 'EOF' > "${BINARIES_DIR}/efi-part/startup.nsh"
\EFI\BOOT\bootx64.efi console=ttyS0 console=tty0 root=/dev/vda2 ro rootwait quiet
EOF

rm -rf "${GENIMAGE_TMP}"

genimage \
    --rootpath "${BINARIES_DIR}" \
    --tmppath "${GENIMAGE_TMP}" \
    --inputpath "${BINARIES_DIR}" \
    --outputpath "${BINARIES_DIR}" \
    --config "${GENIMAGE_CFG}"

echo "=== Disk image created at ${BINARIES_DIR}/lazy-os.img ==="
