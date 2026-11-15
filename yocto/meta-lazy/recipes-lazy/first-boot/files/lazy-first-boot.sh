#!/bin/sh
# Lazy OS First-Boot Setup Script
# Initializes Btrfs subvolumes and OverlayFS mounts for read-only rootfs
set -eu

DATA_MOUNT="/data"
DATA_DEV="/dev/disk/by-label/data"

echo "[lazy-first-boot] Initializing Lazy OS filesystem layout..."

# 1. Ensure /data mountpoint exists and is mounted
mkdir -p "$DATA_MOUNT"
if ! mountpoint -q "$DATA_MOUNT"; then
    if [ -b "$DATA_DEV" ]; then
        mount -t btrfs -o noatime,compress=zstd:1 "$DATA_DEV" "$DATA_MOUNT"
    fi
fi

# 2. Initialize Btrfs subvolumes on first boot
if [ -d "$DATA_MOUNT" ] && [ ! -f "$DATA_MOUNT/.lazy-initialized" ]; then
    echo "[lazy-first-boot] Creating initial Btrfs subvolumes on data partition..."
    if command -v btrfs >/dev/null 2>&1; then
        btrfs subvolume create "$DATA_MOUNT/@home" 2>/dev/null || mkdir -p "$DATA_MOUNT/@home"
        btrfs subvolume create "$DATA_MOUNT/@snapshots" 2>/dev/null || mkdir -p "$DATA_MOUNT/@snapshots"
        btrfs subvolume create "$DATA_MOUNT/@etc_upper" 2>/dev/null || mkdir -p "$DATA_MOUNT/@etc_upper"
        btrfs subvolume create "$DATA_MOUNT/@etc_work" 2>/dev/null || mkdir -p "$DATA_MOUNT/@etc_work"
        btrfs subvolume create "$DATA_MOUNT/@var_upper" 2>/dev/null || mkdir -p "$DATA_MOUNT/@var_upper"
        btrfs subvolume create "$DATA_MOUNT/@var_work" 2>/dev/null || mkdir -p "$DATA_MOUNT/@var_work"
    else
        mkdir -p "$DATA_MOUNT/@home" "$DATA_MOUNT/@snapshots"
        mkdir -p "$DATA_MOUNT/@etc_upper" "$DATA_MOUNT/@etc_work"
        mkdir -p "$DATA_MOUNT/@var_upper" "$DATA_MOUNT/@var_work"
    fi
    touch "$DATA_MOUNT/.lazy-initialized"
fi

# 3. Mount OverlayFS for writable /etc and /var
echo "[lazy-first-boot] Mounting OverlayFS for /etc and /var..."
if [ -d "$DATA_MOUNT/@etc_upper" ] && [ -d "$DATA_MOUNT/@etc_work" ]; then
    mount -t overlay overlay -o lowerdir=/etc,upperdir="$DATA_MOUNT/@etc_upper",workdir="$DATA_MOUNT/@etc_work" /etc || true
fi

if [ -d "$DATA_MOUNT/@var_upper" ] && [ -d "$DATA_MOUNT/@var_work" ]; then
    mount -t overlay overlay -o lowerdir=/var,upperdir="$DATA_MOUNT/@var_upper",workdir="$DATA_MOUNT/@var_work" /var || true
fi

# 4. Mount /home and /var/lib/lazy/snapshots
if [ -d "$DATA_MOUNT/@home" ]; then
    mkdir -p /home
    mount --bind "$DATA_MOUNT/@home" /home || true
fi

mkdir -p /var/lib/lazy/snapshots
if [ -d "$DATA_MOUNT/@snapshots" ]; then
    mount --bind "$DATA_MOUNT/@snapshots" /var/lib/lazy/snapshots || true
fi

# 5. Create runtime directory /run/lazy
mkdir -p /run/lazy /var/lib/lazy /var/log/lazy
chmod 0755 /run/lazy /var/lib/lazy
chmod 0700 /var/log/lazy

echo "[lazy-first-boot] Filesystem setup completed successfully."
