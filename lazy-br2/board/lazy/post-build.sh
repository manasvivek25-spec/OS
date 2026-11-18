#!/usr/bin/env bash
# Lazy OS Buildroot Post-Build Script
# Configures systemd, mount targets, users, and service permissions in ${TARGET_DIR}

set -euo pipefail

TARGET_DIR="$1"
BOARD_DIR="$(dirname "$0")"

echo "=== Lazy OS Post-Build: Configuring Rootfs ==="

# 1. Hostname & Machine Identity
echo "lazy-os" > "${TARGET_DIR}/etc/hostname"

# 2. Filesystem Mount Table (/etc/fstab)
cat << 'EOF' > "${TARGET_DIR}/etc/fstab"
# /etc/fstab: static file system information
# <file system> <mount point>   <type>  <options>       <dump>  <pass>
/dev/root       /               squashfs defaults,ro    0       0
/dev/vda3       /data           btrfs   defaults,noatime,compress=zstd,discard=async 0 2
tmpfs           /tmp            tmpfs   defaults,nosuid,nodev 0 0
tmpfs           /run            tmpfs   defaults,nosuid,nodev,mode=0755 0 0
EOF

# 3. Mount points & runtime directories
mkdir -p "${TARGET_DIR}/data"
mkdir -p "${TARGET_DIR}/run/lazy"
mkdir -p "${TARGET_DIR}/etc/lazy/capabilities"
mkdir -p "${TARGET_DIR}/var/log/lazy"
mkdir -p "${TARGET_DIR}/var/quarantine"
mkdir -p "${TARGET_DIR}/usr/share/lazy/hud"

# 4. First-boot initialization service
mkdir -p "${TARGET_DIR}/etc/systemd/system"
cat << 'EOF' > "${TARGET_DIR}/etc/systemd/system/lazy-firstboot.service"
[Unit]
Description=Lazy OS First-Boot Storage & User Initialization
DefaultDependencies=no
After=local-fs.target
Before=sysinit.target
ConditionPathExists=!/data/.initialized

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/lazy-firstboot.sh

[Install]
WantedBy=sysinit.target
EOF

# 5. First-boot script
cat << 'EOF' > "${TARGET_DIR}/usr/bin/lazy-firstboot.sh"
#!/bin/sh
set -e
echo "Initializing Lazy OS persistent storage..."
mkdir -p /data/system /data/audit /data/tasks /data/snapshots /data/mail /data/chat /data/home/lazy
chmod 700 /data/system
chmod 750 /data/audit
chmod 755 /data/home/lazy
touch /data/.initialized
echo "Lazy OS persistent storage initialized."
EOF
chmod +x "${TARGET_DIR}/usr/bin/lazy-firstboot.sh"

# Enable first-boot service
mkdir -p "${TARGET_DIR}/etc/systemd/system/sysinit.target.wants"
ln -sf "/etc/systemd/system/lazy-firstboot.service" "${TARGET_DIR}/etc/systemd/system/sysinit.target.wants/lazy-firstboot.service"

echo "=== Lazy OS Post-Build Configuration Complete ==="
