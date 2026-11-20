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
tmpfs           /var/log        tmpfs   defaults,nosuid,nodev,mode=0755 0 0
EOF

# 3. Mount points & runtime directories
mkdir -p "${TARGET_DIR}/data/system/lazy/audit"
mkdir -p "${TARGET_DIR}/data/system/dovecot"
mkdir -p "${TARGET_DIR}/home/lazy"
mkdir -p "${TARGET_DIR}/run/lazy"
mkdir -p "${TARGET_DIR}/run/dovecot"
mkdir -p "${TARGET_DIR}/etc/lazy/capabilities"
mkdir -p "${TARGET_DIR}/var/log/lazy"
mkdir -p "${TARGET_DIR}/var/quarantine"
mkdir -p "${TARGET_DIR}/var/lib"
mkdir -p "${TARGET_DIR}/usr/share/lazy/hud"

# Link /var/lib/lazy and /var/lib/dovecot to persistent data (use relative symlinks so host mkusers can resolve it)
ln -sfn ../../data/system/lazy "${TARGET_DIR}/var/lib/lazy"
ln -sfn ../../data/system/dovecot "${TARGET_DIR}/var/lib/dovecot"

# tmpfiles configuration for runtime sockets
mkdir -p "${TARGET_DIR}/usr/lib/tmpfiles.d"
cat << 'EOF' > "${TARGET_DIR}/usr/lib/tmpfiles.d/lazy.conf"
d /run/lazy 1777 root root -
d /run/lazy/sockets 1777 root root -
d /run/dovecot 0755 root root -
d /var/empty 0755 root root -
d /var/log/lazy 0755 root root -
EOF

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
mkdir -p /data/system/lazy /data/system/dovecot /data/audit /data/.audit /data/tasks /data/snapshots /data/.snapshots /data/mail /data/chat /data/home/lazy /data/quarantine
chmod 1777 /data
chmod 755 /data/system
chmod 777 /data/system/lazy
chmod 750 /data/system/dovecot
chmod 777 /data/audit /data/.audit
touch /data/.audit/lazy-audit.log 2>/dev/null || true
chmod 666 /data/.audit/lazy-audit.log 2>/dev/null || true
chmod 700 /data/quarantine
chmod 755 /data/home/lazy
chmod 1777 /data/mail /data/chat /data/tasks /data/snapshots /data/.snapshots

chown -R lazy:lazy /data/home/lazy 2>/dev/null || true
chown -R lazy-gw:lazy-gw /data/system/lazy 2>/dev/null || true
chown -R lazy-audit:lazy-audit /data/audit /data/.audit 2>/dev/null || true
chown -R dovecot:dovecot /data/system/dovecot 2>/dev/null || true
touch /data/.initialized
echo "Lazy OS persistent storage initialized."
EOF
chmod +x "${TARGET_DIR}/usr/bin/lazy-firstboot.sh"

mkdir -p "${TARGET_DIR}/usr/sbin"
ln -sf /usr/bin/lazy-firstboot.sh "${TARGET_DIR}/usr/sbin/lazy-first-boot"

# Enable first-boot service
mkdir -p "${TARGET_DIR}/etc/systemd/system/sysinit.target.wants"
ln -sf "/etc/systemd/system/lazy-firstboot.service" "${TARGET_DIR}/etc/systemd/system/sysinit.target.wants/lazy-firstboot.service"

# Configure wired network with DHCP and enable systemd-networkd
mkdir -p "${TARGET_DIR}/etc/systemd/network"
cat << 'EOF' > "${TARGET_DIR}/etc/systemd/network/80-wired.network"
[Match]
Name=eth* en*

[Network]
DHCP=yes
EOF
mkdir -p "${TARGET_DIR}/etc/systemd/system/multi-user.target.wants"
ln -sf /usr/lib/systemd/system/systemd-networkd.service "${TARGET_DIR}/etc/systemd/system/multi-user.target.wants/systemd-networkd.service"

# 6. Serial Console Autologin for QEMU Automated Testing
mkdir -p "${TARGET_DIR}/etc/systemd/system/serial-getty@ttyS0.service.d"
cat << 'EOF' > "${TARGET_DIR}/etc/systemd/system/serial-getty@ttyS0.service.d/autologin.conf"
[Service]
ExecStart=
ExecStart=-/sbin/agetty -o '-p -- \\u' --noclear --autologin root %I $TERM
EOF

# 7. Local Mail (Dovecot) Configuration
mkdir -p "${TARGET_DIR}/etc/dovecot"
cat << 'EOF' > "${TARGET_DIR}/etc/dovecot/dovecot.conf"
protocols = imap pop3 lmtp
listen = 127.0.0.1
ssl = no
disable_plaintext_auth = no
mail_location = maildir:/data/mail/%u
auth_mechanisms = plain
passdb {
  driver = passwd
}
userdb {
  driver = passwd
}
EOF

mkdir -p "${TARGET_DIR}/etc/systemd/system/dovecot.service.d"
cat << 'EOF' > "${TARGET_DIR}/etc/systemd/system/dovecot.service.d/override.conf"
[Service]
RuntimeDirectory=dovecot
RuntimeDirectoryMode=0755
EOF

# 8. Clean up any invalid multi-user.target symlinks
rm -f "${TARGET_DIR}/etc/systemd/system/multi-user.target.wants/lazy-code-sandbox@.service"
rm -f "${TARGET_DIR}/etc/systemd/system/multi-user.target.wants/lazy-first-boot.service"
rm -f "${TARGET_DIR}/etc/systemd/system/lazy-first-boot.service"
ln -sfn /dev/null "${TARGET_DIR}/etc/systemd/system/dovecot.socket"
rm -f "${TARGET_DIR}/usr/lib/systemd/system/sockets.target.wants/dovecot.socket"
rm -f "${TARGET_DIR}/etc/systemd/system/sockets.target.wants/dovecot.socket"

# 9. Set root password
echo "root:lazy" | chpasswd -R "${TARGET_DIR}" 2>/dev/null || true

echo "=== Lazy OS Post-Build Configuration Complete ==="
