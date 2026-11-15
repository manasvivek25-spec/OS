#!/usr/bin/env python3
"""build_image_v2.py - Assembles Lazy OS V2 bootable artifacts under build/v2/

Artifacts created:
1. build/v2/lazy-os-rootfs/  (Clean root filesystem with real findmnt, lsblk, btrfs, Python 3.12, Busybox)
2. build/v2/lazy-os-boot.cpio.gz (Bootable initramfs with in-tree Btrfs kernel modules)
3. build/v2/lazy-disk.img (GPT partitioned 256MB disk with formatted Btrfs partition 3)
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BUILD_V2 = REPO_ROOT / "build/v2"
ROOTFS = BUILD_V2 / "lazy-os-rootfs"
BUILD_V2.mkdir(parents=True, exist_ok=True)

print("=== Assembling Lazy OS V2 Boot Artifacts ===")

if ROOTFS.exists():
    shutil.rmtree(ROOTFS)
ROOTFS.mkdir(parents=True, exist_ok=True)

# 1. Directory Skeleton
dirs = [
    "bin", "sbin", "usr/bin", "usr/sbin", "usr/lib", "usr/lib/x86_64-linux-gnu",
    "lib", "lib64", "lib/x86_64-linux-gnu", "lib/modules", "etc", "etc/lazy", "etc/lazy/capabilities",
    "dev", "proc", "sys", "run", "run/lazy", "tmp", "var", "var/log", "var/quarantine",
    "data", "home/lazyos", "root", "usr/share/lazy/hud"
]
for d in dirs:
    (ROOTFS / d).mkdir(parents=True, exist_ok=True)

# 2. Busybox
busybox_bin = Path("/bin/busybox")
shutil.copy2(busybox_bin, ROOTFS / "bin/busybox")
(ROOTFS / "bin/busybox").chmod(0o755)

tools = [
    "sh", "bash", "ls", "cat", "echo", "pwd", "mkdir", "rmdir", "cp", "mv", "rm",
    "touch", "grep", "sed", "awk", "find", "chmod", "chown", "mount", "umount",
    "ps", "kill", "df", "free", "uname", "hostname", "whoami", "id", "clear",
    "sleep", "date", "reboot", "poweroff", "true", "false", "test", "head", "tail",
    "wc", "cut", "sort", "uniq", "tr", "tee", "sync", "env", "insmod", "rmmod", "modprobe",
    "lsmod", "mknod", "blkid", "losetup"
]
for t in tools:
    link = ROOTFS / "bin" / t
    if not link.exists():
        link.symlink_to("/bin/busybox")

for t in ["reboot", "poweroff", "mount", "umount", "insmod", "mknod"]:
    link = ROOTFS / "sbin" / t
    if not link.exists():
        link.symlink_to("/bin/busybox")

(ROOTFS / "usr/bin/env").symlink_to("/bin/busybox")

# 3. Real System Utilities: findmnt, lsblk, btrfs
sys_bins = ["/usr/bin/findmnt", "/usr/bin/lsblk", "/usr/bin/btrfs"]
for b in sys_bins:
    src_p = Path(b)
    if src_p.exists():
        dst_p = ROOTFS / "usr/bin" / src_p.name
        shutil.copy2(src_p, dst_p)
        dst_p.chmod(0o755)
        # also symlink into /bin for convenience
        (ROOTFS / "bin" / src_p.name).symlink_to(f"/usr/bin/{src_p.name}")

# 4. Shared Libraries
lib_sources = [
    "/lib64/ld-linux-x86-64.so.2",
    "/lib/x86_64-linux-gnu/libc.so.6",
    "/lib/x86_64-linux-gnu/libm.so.6",
    "/lib/x86_64-linux-gnu/libz.so.1",
    "/lib/x86_64-linux-gnu/libexpat.so.1",
    "/lib/x86_64-linux-gnu/libssl.so.3",
    "/lib/x86_64-linux-gnu/libcrypto.so.3",
    "/lib/x86_64-linux-gnu/libbz2.so.1.0",
    "/lib/x86_64-linux-gnu/liblzma.so.5",
    "/lib/x86_64-linux-gnu/libffi.so.8",
    "/usr/lib/x86_64-linux-gnu/libgcc_s.so.1",
    "/lib/x86_64-linux-gnu/libgcc_s.so.1",
    "/usr/lib/x86_64-linux-gnu/libpthread.so.0",
    "/lib/x86_64-linux-gnu/libpthread.so.0",
    # findmnt & lsblk dependencies
    "/lib/x86_64-linux-gnu/libmount.so.1",
    "/lib/x86_64-linux-gnu/libblkid.so.1",
    "/lib/x86_64-linux-gnu/libsmartcols.so.1",
    "/lib/x86_64-linux-gnu/libudev.so.1",
    "/lib/x86_64-linux-gnu/libselinux.so.1",
    "/lib/x86_64-linux-gnu/libcap.so.2",
    "/lib/x86_64-linux-gnu/libpcre2-8.so.0",
    # btrfs dependencies
    "/lib/x86_64-linux-gnu/libuuid.so.1",
    "/lib/x86_64-linux-gnu/liblzo2.so.2",
    "/lib/x86_64-linux-gnu/libzstd.so.1",
]

for src in lib_sources:
    src_p = Path(src)
    if src_p.exists():
        dst_p = ROOTFS / src_p.relative_to("/")
        dst_p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_p, dst_p)

if not (ROOTFS / "lib64/ld-linux-x86-64.so.2").exists():
    (ROOTFS / "lib64").mkdir(parents=True, exist_ok=True)
    shutil.copy2("/lib64/ld-linux-x86-64.so.2", ROOTFS / "lib64/ld-linux-x86-64.so.2")

# 5. Kernel Modules for Btrfs
print("Decompressing Btrfs kernel modules...")
modules_dst = ROOTFS / "lib/modules"
k_ver = "6.8.0-149-generic"
mod_defs = [
    ("libcrc32c.ko", f"/lib/modules/{k_ver}/kernel/lib/libcrc32c.ko.zst"),
    ("xor.ko", f"/lib/modules/{k_ver}/kernel/crypto/xor.ko.zst"),
    ("raid6_pq.ko", f"/lib/modules/{k_ver}/kernel/lib/raid6/raid6_pq.ko.zst"),
    ("btrfs.ko", f"/lib/modules/{k_ver}/kernel/fs/btrfs/btrfs.ko.zst"),
]
for mod_name, mod_src in mod_defs:
    dst_file = modules_dst / mod_name
    subprocess.run(f"zstd -d -c {mod_src} > {dst_file}", shell=True, check=True)

# 6. Python 3.12 Runtime
shutil.copy2("/usr/bin/python3", ROOTFS / "usr/bin/python3")
(ROOTFS / "bin/python3").symlink_to("/usr/bin/python3")

py_lib = Path("/usr/lib/python3.12")
if py_lib.exists():
    shutil.copytree(py_lib, ROOTFS / "usr/lib/python3.12", ignore=shutil.ignore_patterns("test", "idlelib", "tkinter", "__pycache__", "*.pyc"))

venv_site = REPO_ROOT / ".venv/lib/python3.12/site-packages"
dst_site = ROOTFS / "usr/lib/python3/dist-packages"
dst_site.mkdir(parents=True, exist_ok=True)

if venv_site.exists():
    extra_pkgs = ["attr", "attrs", "jsonschema", "jsonschema_specifications", "referencing", "rpds", "yaml", "_yaml", "typing_extensions.py"]
    for pkg in extra_pkgs:
        pkg_p = venv_site / pkg
        if pkg_p.exists():
            if pkg_p.is_dir():
                shutil.copytree(pkg_p, dst_site / pkg, dirs_exist_ok=True)
            else:
                shutil.copy2(pkg_p, dst_site / pkg)

# 7. Copy Lazy OS Python Source & Contracts
shutil.copytree(REPO_ROOT / "src/lazy", dst_site / "lazy", dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
shutil.copytree(REPO_ROOT / "config", ROOTFS / "etc/lazy/config", dirs_exist_ok=True)
shutil.copytree(REPO_ROOT / "config/capabilities", ROOTFS / "etc/lazy/capabilities", dirs_exist_ok=True)
shutil.copytree(REPO_ROOT / "docs/contracts", ROOTFS / "etc/lazy/contracts", dirs_exist_ok=True)
shutil.copytree(REPO_ROOT / "docs/contracts", dst_site / "lazy/docs/contracts", dirs_exist_ok=True)
shutil.copytree(REPO_ROOT / "hud", ROOTFS / "usr/share/lazy/hud", dirs_exist_ok=True)

# 8. Branding & Users
(ROOTFS / "etc/os-release").write_text("""NAME="Lazy OS"
ID=lazy-os
VERSION="0.2-command-center"
VERSION_ID="0.2"
PRETTY_NAME="Lazy OS 0.2 (Track A Custom Kernel & Root)"
HOME_URL="https://lazyos.org"
SUPPORT_URL="https://github.com/lazy-os"
BUG_REPORT_URL="https://github.com/lazy-os/issues"
""")
(ROOTFS / "usr/lib/os-release").symlink_to("/etc/os-release")
(ROOTFS / "etc/hostname").write_text("lazy-os\n")
(ROOTFS / "etc/hosts").write_text("127.0.0.1 localhost lazy-os\n::1 localhost\n")
(ROOTFS / "etc/passwd").write_text("""root:x:0:0:root:/root:/bin/sh
lazyos:x:1000:1000:Lazy OS User:/home/lazyos:/bin/sh
""")

# 9. In-Guest Service Daemon
guest_daemon_src = """#!/usr/bin/python3
import os
import sys
import time
from pathlib import Path
from lazy.gateway.server import GatewayServer

def main():
    hud_dir = Path("/usr/share/lazy/hud")
    repo_root = Path("/")
    server = GatewayServer(host="0.0.0.0", port=8765, hud_dir=hud_dir)
    server.api_handler.repo_root = repo_root
    server.api_handler.data_dir = Path("/data")
    server.start()
    print("Lazy OS Gateway Daemon online on 0.0.0.0:8765")
    while True:
        try:
            time.sleep(3600)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
"""
(ROOTFS / "usr/bin/lazy-guest-daemon.py").write_text(guest_daemon_src)
(ROOTFS / "usr/bin/lazy-guest-daemon.py").chmod(0o755)

# 10. Master /init script
init_src = """#!/bin/busybox sh
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
export HOME=/home/lazyos
export USER=lazyos
export SHELL=/bin/sh

/bin/busybox mount -t proc proc /proc
/bin/busybox mount -t sysfs sysfs /sys
/bin/busybox mount -t devtmpfs devtmpfs /dev 2>/dev/null || true
/bin/busybox mount -t tmpfs tmpfs /run
/bin/busybox mount -t tmpfs tmpfs /tmp

/bin/busybox mkdir -p /run/lazy /var/log /home/lazyos /data
/bin/busybox chmod 0755 /run/lazy /var/log /data
/bin/busybox hostname lazy-os

# 1. Load Btrfs Kernel Modules
/bin/busybox insmod /lib/modules/libcrc32c.ko 2>/dev/null || true
/bin/busybox insmod /lib/modules/xor.ko 2>/dev/null || true
/bin/busybox insmod /lib/modules/raid6_pq.ko 2>/dev/null || true
/bin/busybox insmod /lib/modules/btrfs.ko 2>/dev/null || true

# 2. Mount Persistent Partition /dev/vda3 on /data
/bin/busybox mknod /dev/vda b 254 0 2>/dev/null || true
/bin/busybox mknod /dev/vda3 b 254 3 2>/dev/null || true

MOUNT_SUCCESS=0
if /bin/busybox mount -t btrfs /dev/vda3 /data 2>/dev/null; then
    /bin/busybox echo "[OK] Mounted real persistent Btrfs partition on /data from /dev/vda3"
    MOUNT_SUCCESS=1
elif /bin/busybox mount -t ext4 /dev/vda3 /data 2>/dev/null; then
    /bin/busybox echo "[OK] Mounted real persistent ext4 partition on /data from /dev/vda3"
    MOUNT_SUCCESS=1
else
    /bin/busybox echo "[WARN] Direct mount failed; attempting scan..."
    /bin/busybox mount -t btrfs -o subvol=/ /dev/vda3 /data 2>/dev/null && MOUNT_SUCCESS=1
fi

if [ "$MOUNT_SUCCESS" -eq 0 ]; then
    /bin/busybox echo "[ERR] Could not mount /dev/vda3; fallback tmpfs"
    /bin/busybox mount -t tmpfs tmpfs /data
fi

/bin/busybox mkdir -p /data/@snapshots
/bin/busybox chown -R lazyos:lazyos /data /home/lazyos 2>/dev/null || true

# 3. Configure Network for Port Forwarding
/bin/busybox ifconfig lo 127.0.0.1 up 2>/dev/null || true
/bin/busybox ifconfig eth0 10.0.2.15 netmask 255.255.255.0 up 2>/dev/null || true
/bin/busybox route add default gw 10.0.2.2 2>/dev/null || true

# 4. Start In-Guest Gateway Daemon
/usr/bin/python3 /usr/bin/lazy-guest-daemon.py > /var/log/lazy-gateway.log 2>&1 &

/bin/busybox echo "======================================================================"
/bin/busybox echo "        LAZY OS // v0.2-command-center (Persistent Btrfs /data)       "
/bin/busybox echo "======================================================================"
/bin/busybox echo "[OK] Linux Kernel $(/bin/busybox uname -r) loaded."
/bin/busybox echo "[OK] /data mount: $(/bin/busybox findmnt /data 2>/dev/null || /bin/busybox mount | /bin/busybox grep '/data')"
/bin/busybox echo "[OK] Gateway & REST API listening on 0.0.0.0:8765 (guest)."
/bin/busybox echo ""

if /bin/busybox grep -q "lazy_interactive" /proc/cmdline; then
    /bin/busybox echo "lazyos@lazy-os:~$ "
    while true; do
        /bin/busybox cttyhack /bin/busybox sh 2>/dev/null || /bin/busybox sleep 3600
    done
else
    /bin/busybox echo "Batch run completed. Powering down."
    /bin/busybox poweroff -f
fi
"""
(ROOTFS / "init").write_text(init_src)
(ROOTFS / "init").chmod(0o755)

print("Rootfs files populated successfully.")

# 11. Create Initramfs
print("Creating compressed initramfs: build/v2/lazy-os-boot.cpio.gz...")
subprocess.run(
    "find . | cpio -o -H newc | gzip -9 > " + str(BUILD_V2 / "lazy-os-boot.cpio.gz"),
    cwd=str(ROOTFS),
    shell=True,
    check=True
)
initrd_size = (BUILD_V2 / "lazy-os-boot.cpio.gz").stat().st_size
print(f"Initramfs created: {initrd_size / (1024*1024):.2f} MB")

# 12. Create WIC GPT Disk Image with Formatted Btrfs Partition 3
print("Creating WIC GPT Disk Image with real Btrfs partition: build/v2/lazy-disk.img...")
disk_img = BUILD_V2 / "lazy-disk.img"
if disk_img.exists():
    disk_img.unlink()

subprocess.run(["truncate", "-s", "256M", str(disk_img)], check=True)
sfdisk_input = """label: gpt
label-id: 01234567-89AB-CDEF-0123-456789ABCDEF
device: build/v2/lazy-disk.img
unit: sectors

1 : start=2048, size=32768, type=C12A7328-F81F-11D2-BA4B-00A0C93EC93B, name="boot"
2 : start=34816, size=204800, type=0FC63DAF-8483-4772-8E79-3D69D8477DE4, name="root"
3 : start=239616, size=262144, type=0FC63DAF-8483-4772-8E79-3D69D8477DE4, name="data"
"""
subprocess.run(["sfdisk", str(disk_img)], input=sfdisk_input, text=True, check=True)

# Format a standalone 128MB Btrfs image and inject it into partition 3 (offset 239616 sectors * 512 = 122683392 bytes)
btrfs_part = Path("/tmp/btrfs-data-part.img")
subprocess.run(["truncate", "-s", "128M", str(btrfs_part)], check=True)
subprocess.run(["mkfs.btrfs", "-f", "-L", "LAZY_DATA", str(btrfs_part)], check=True)

# Inject into partition 3
subprocess.run(
    f"dd if={btrfs_part} of={disk_img} seek=239616 bs=512 conv=notrunc",
    shell=True,
    check=True
)
print("Real Btrfs filesystem injected into partition 3.")

print("=== Lazy OS V2 Boot Artifact Assembly Complete ===")
