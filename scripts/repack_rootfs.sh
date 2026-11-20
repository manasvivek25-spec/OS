#!/bin/bash
set -euo pipefail

export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

echo "========================================================"
echo "Lazy OS Buildroot Incremental Repack (Role A Milestone)"
echo "========================================================"

echo "[1/5] Syncing workspace src, hud, systemd to lazy-os-src..."
rsync -av --delete --exclude=".git" --exclude="node_modules" --exclude="__pycache__" /mnt/c/Users/len/OS/src/ /home/manas/lazy-os-src/src/
rsync -av --delete /mnt/c/Users/len/OS/hud/ /home/manas/lazy-os-src/hud/
rsync -av /mnt/c/Users/len/OS/systemd/ /home/manas/lazy-os-src/systemd/
rsync -av /mnt/c/Users/len/OS/scripts/ /home/manas/lazy-os-src/scripts/

echo "[2/5] Updating target rootfs..."
PY_LIB_DIR=$(ls -d /home/manas/lazy-build/output/target/usr/lib/python3* | head -n 1)
echo "Python site-packages target: ${PY_LIB_DIR}/site-packages/lazy"
mkdir -p "${PY_LIB_DIR}/site-packages/lazy"
cp -r /home/manas/lazy-os-src/src/lazy/* "${PY_LIB_DIR}/site-packages/lazy/"

mkdir -p /home/manas/lazy-build/output/target/usr/share/lazy/hud
cp -r /home/manas/lazy-os-src/hud/* /home/manas/lazy-build/output/target/usr/share/lazy/hud/

mkdir -p /home/manas/lazy-build/output/target/etc/systemd/system/multi-user.target.wants
cp -r /home/manas/lazy-os-src/systemd/*.service /home/manas/lazy-build/output/target/etc/systemd/system/
cp -r /home/manas/lazy-os-src/systemd/*.slice /home/manas/lazy-build/output/target/etc/systemd/system/

if [ -f "/home/manas/lazy-os-src/scripts/run_ml_bench.sh" ]; then
    cp /home/manas/lazy-os-src/scripts/run_ml_bench.sh /home/manas/lazy-build/output/target/usr/bin/run_ml_bench.sh
    chmod 0755 /home/manas/lazy-build/output/target/usr/bin/run_ml_bench.sh
fi
chmod 0755 /home/manas/lazy-build/output/target/usr/bin/llama-* 2>/dev/null || true

# Verify model
echo "[3/5] Checking model in target..."
ls -lh /home/manas/lazy-build/output/target/usr/share/lazy/models/

echo "[4/5] Aligning Buildroot configs and executing make..."
cp /home/manas/lazy-build/output/.config /home/manas/lazy-build/.config
cd /home/manas/lazy-build
make BR2_CONFIG=/home/manas/lazy-build/output/.config BR2_EXTERNAL=/mnt/c/Users/len/OS/lazy-br2 O=/home/manas/lazy-build/output

echo "[5/5] Deploying artifacts to dist/..."
cp -v /home/manas/lazy-build/output/images/lazy-os.img /mnt/c/Users/len/OS/dist/lazy-os.img
cp -v /home/manas/lazy-build/output/images/rootfs.squashfs /mnt/c/Users/len/OS/dist/rootfs.squashfs
echo "========================================================"
echo "Incremental Repack Successfully Completed!"
echo "========================================================"
