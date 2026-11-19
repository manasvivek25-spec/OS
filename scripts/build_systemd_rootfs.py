#!/usr/bin/env python3
"""
DEV ONLY: Build an ephemeral development image by copying host binaries via ldd.
WARNING: THIS SCRIPT IS DEV ONLY. IT CANNOT BE USED FOR DIST, BENCHMARKS,
ACCEPTANCE CHECKS, OR ANY REPORTED FIGURES. (V3.2 Rule 3)
"""

import os
import sys
import shutil
import subprocess
import glob
from pathlib import Path

print("=" * 70)
print("  WARNING: BUILDING DEVELOPMENT IMAGE USING HOST BINARIES (DEV ONLY)")
print("  THIS IMAGE IS NOT A PRODUCTION BUILD AND CANNOT BE USED FOR DIST,")
print("  BENCHMARKS, ACCEPTANCE CHECKS, OR ANY REPORTED FIGURES.")
print("=" * 70)

REPO_ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = REPO_ROOT / "build/dev"
ROOTFS = BUILD_DIR / "lazy-os-rootfs"
SYSTEMD_SRC = REPO_ROOT / "systemd"
DISK_IMG = BUILD_DIR / "lazy-disk-dev.img"
SQUASHFS_IMG = BUILD_DIR / "rootfs-dev.squashfs"
INITRAMFS_IMG = BUILD_DIR / "lazy-initramfs-dev.cpio.gz"

def log(msg):
    print(f"[build-systemd] {msg}")

def run_cmd(cmd, check=True):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and res.returncode != 0:
        print(f"FAILED: {cmd}\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}", file=sys.stderr)
        sys.exit(res.returncode)
    return res

def copy_file(src, dst):
    src = Path(src)
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_symlink():
        link_target = os.readlink(src)
        if dst.exists() or dst.is_symlink():
            dst.unlink()
        os.symlink(link_target, dst)
    else:
        shutil.copy2(src, dst)

def resolve_all_deps(initial_paths, rootfs_dir):
    """Recursively discover and copy all ELF dependencies into rootfs."""
    queue = [Path(p) for p in initial_paths if Path(p).exists()]
    visited = set()
    
    while queue:
        item = queue.pop(0)
        try:
            real_item = item.resolve()
        except Exception:
            continue
            
        if real_item in visited:
            continue
        visited.add(real_item)
        
        # Copy file into rootfs
        try:
            rel_path = real_item.relative_to("/")
            dst = rootfs_dir / rel_path
            copy_file(real_item, dst)
        except Exception as e:
            log(f"Error copying {real_item}: {e}")
            continue

        # If original was a symlink at a different path, copy symlink too
        if item != real_item:
            try:
                rel_sym = item.relative_to("/")
                sym_dst = rootfs_dir / rel_sym
                copy_file(item, sym_dst)
            except Exception:
                pass
        
        # Run ldd to discover next layer of dependencies
        res = subprocess.run(["ldd", str(real_item)], capture_output=True, text=True)
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                line = line.strip()
                target_str = None
                if "=>" in line:
                    parts = line.split("=>")
                    target_str = parts[1].split()[0]
                elif line.startswith("/"):
                    target_str = line.split()[0]
                
                if target_str and target_str.startswith("/"):
                    dep_p = Path(target_str)
                    if dep_p.exists() and dep_p not in visited:
                        queue.append(dep_p)

def main():
    log(f"Preparing systemd rootfs in {ROOTFS}...")
    
    # 1. Essential directories
    for d in [
        "bin", "sbin", "usr/bin", "usr/sbin", "lib", "usr/lib", "lib64",
        "lib/x86_64-linux-gnu", "usr/lib/x86_64-linux-gnu",
        "lib/systemd/system", "usr/lib/systemd", "etc/systemd/system",
        "etc/systemd/system/multi-user.target.wants",
        "proc", "sys", "dev", "run", "tmp", "data", "home/lazyos",
        "var/log", "var/lib/lazy", "var/lib/lazy/secrets"
    ]:
        (ROOTFS / d).mkdir(parents=True, exist_ok=True)
    
    # Configure ld.so.conf
    ld_conf = ROOTFS / "etc/ld.so.conf"
    ld_conf.write_text("/lib\n/lib64\n/usr/lib\n/usr/lib64\n/lib/x86_64-linux-gnu\n/usr/lib/x86_64-linux-gnu\n")

    # 2. Collect all host systemd binaries & support libraries
    bins = [
        "/usr/lib/systemd/systemd",
        "/usr/lib/systemd/systemd-executor",
        "/usr/lib/systemd/systemd-journald",
        "/usr/lib/systemd/systemd-remount-fs",
        "/usr/lib/systemd/systemd-modules-load",
        "/usr/lib/systemd/systemd-sysctl",
        "/usr/bin/systemctl",
        "/usr/bin/systemd-analyze",
        "/usr/bin/python3",
        "/usr/bin/btrfs",
        "/usr/bin/lsblk",
        "/usr/bin/findmnt",
        "/usr/bin/free",
        "/usr/bin/touch",
        "/usr/bin/mkdir",
        "/usr/bin/cat",
        "/usr/bin/uname",
        "/usr/bin/ps",
        "/sbin/agetty",
        "/bin/login",
        "/bin/bash"
    ]
    # Add all systemd helpers & generators
    bins.extend([p for p in glob.glob("/usr/lib/systemd/*") if os.path.isfile(p)])
    bins.extend([p for p in glob.glob("/usr/lib/systemd/system-generators/*") if os.path.isfile(p)])
    # Add all systemd support libraries
    bins.extend(glob.glob("/usr/lib/x86_64-linux-gnu/systemd/*.so*"))
    bins.extend(glob.glob("/lib/x86_64-linux-gnu/libapparmor*.so*"))
    bins.extend(glob.glob("/lib/x86_64-linux-gnu/libaudit*.so*"))
    bins.extend(glob.glob("/lib/x86_64-linux-gnu/libkmod*.so*"))
    bins.extend(glob.glob("/lib/x86_64-linux-gnu/libseccomp*.so*"))
    bins.extend(glob.glob("/lib/x86_64-linux-gnu/libcap*.so*"))

    log(f"Recursively resolving all dependencies for {len(bins)} binaries and core libraries...")
    resolve_all_deps(bins, ROOTFS)
    log("All ELF dependencies resolved.")

    # Setup /lib64 symlink to dynamic linker
    (ROOTFS / "lib64").mkdir(parents=True, exist_ok=True)
    ld_link = ROOTFS / "lib64/ld-linux-x86-64.so.2"
    if ld_link.exists() or ld_link.is_symlink():
        ld_link.unlink()
    host_ld = Path("/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2")
    if not host_ld.exists():
        host_ld = Path("/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2")
    copy_file(host_ld, ROOTFS / "usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2")
    os.symlink("/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2", ld_link)

    # Link /lib/x86_64-linux-gnu to /usr/lib/x86_64-linux-gnu libraries
    lib_x86 = ROOTFS / "lib/x86_64-linux-gnu"
    lib_x86.mkdir(parents=True, exist_ok=True)
    for f in (ROOTFS / "usr/lib/x86_64-linux-gnu").glob("*"):
        dst_f = lib_x86 / f.name
        if not dst_f.exists() and not dst_f.is_symlink():
            try:
                os.symlink(f"/usr/lib/x86_64-linux-gnu/{f.name}", dst_f)
            except Exception:
                pass

    # Run ldconfig inside rootfs
    subprocess.run(["/sbin/ldconfig", "-r", str(ROOTFS)], capture_output=True)
    
    # Symlink init to systemd
    sbin_init = ROOTFS / "sbin/init"
    if sbin_init.exists() or sbin_init.is_symlink():
        sbin_init.unlink()
    os.symlink("/usr/lib/systemd/systemd", sbin_init)
    
    bin_init = ROOTFS / "init"
    if bin_init.exists() or bin_init.is_symlink():
        bin_init.unlink()
    os.symlink("/usr/lib/systemd/systemd", bin_init)
    
    # Ensure systemctl is available in both /bin and /usr/bin
    if not (ROOTFS / "bin/systemctl").exists():
        os.symlink("/usr/bin/systemctl", ROOTFS / "bin/systemctl")

    # 3. Copy systemd internal shared libraries
    for p in glob.glob("/usr/lib/x86_64-linux-gnu/systemd/*.so*"):
        copy_file(p, ROOTFS / Path(p).relative_to("/"))

    # 4. Copy core systemd units from host
    sys_unit_dir = ROOTFS / "lib/systemd/system"
    sys_unit_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy all system targets, core services and sockets
    for pattern in ["*.target", "systemd-*.service", "systemd-*.socket", "*.slice"]:
        for u in glob.glob(f"/lib/systemd/system/{pattern}"):
            copy_file(u, sys_unit_dir / os.path.basename(u))
    for extra in ["serial-getty@.service", "getty@.service", "console-getty.service"]:
        p = Path("/lib/systemd/system") / extra
        if p.exists():
            copy_file(p, sys_unit_dir / extra)
    
    # Ensure /usr/lib/systemd/system points to /lib/systemd/system
    usr_sys_dir = ROOTFS / "usr/lib/systemd/system"
    if usr_sys_dir.exists() and not usr_sys_dir.is_symlink():
        shutil.rmtree(usr_sys_dir)
    elif usr_sys_dir.is_symlink():
        usr_sys_dir.unlink()
    os.symlink("/lib/systemd/system", usr_sys_dir)

    # Clean extraneous generators
    gen_dir = ROOTFS / "usr/lib/systemd/system-generators"
    if gen_dir.exists():
        for f in gen_dir.glob("*"):
            if f.name not in ["systemd-fstab-generator", "systemd-getty-generator"]:
                try:
                    if f.is_file() or f.is_symlink():
                        f.unlink()
                except Exception:
                    pass

    # Set default target to multi-user.target
    def_target = ROOTFS / "etc/systemd/system/default.target"
    if def_target.exists() or def_target.is_symlink():
        def_target.unlink()
    os.symlink("/lib/systemd/system/multi-user.target", def_target)

    # 5. Copy all 15 Lazy OS units from repo
    unit_files = [
        "lazy-gateway.service", "lazy-planner.service", "lazy-llm.service",
        "lazy-policy.service", "lazy-tasks.service", "lazy-broker-fs.service",
        "lazy-broker-sys.service", "lazy-broker-hw.service", "lazy-broker-web.service",
        "lazy-broker-comms.service", "lazy-secrets.service", "lazy-outbox.service",
        "lazy-fetcher.service", "lazy-routines.service", "lazy-audit.service",
        "lazy-first-boot.service", "lazy-warmup.service",
        "lazy-interactive.slice", "lazy-background.slice", "lazy-code-sandbox.slice"
    ]
    for u in unit_files:
        src_u = SYSTEMD_SRC / u
        if src_u.exists():
            dst_u = ROOTFS / "etc/systemd/system" / u
            copy_file(src_u, dst_u)
            # Enable services in multi-user.target.wants
            if u.endswith(".service") and not u.startswith("lazy-code-sandbox@"):
                want_link = ROOTFS / "etc/systemd/system/multi-user.target.wants" / u
                if want_link.exists() or want_link.is_symlink():
                    want_link.unlink()
                os.symlink(f"/etc/systemd/system/{u}", want_link)
    
    log("Copied and enabled 15 Lazy OS microservice units in multi-user.target.wants")

    # 6. Configure /etc/passwd and /etc/group with dedicated system users
    passwd_content = """root:x:0:0:root:/root:/bin/sh
lazyos:x:1000:1000:Lazy OS User:/home/lazyos:/bin/sh
lazy-gw:x:1001:1001:Lazy Gateway:/var/lib/lazy:/bin/false
lazy-plan:x:1002:1002:Lazy Planner:/var/lib/lazy:/bin/false
lazy-llm:x:1003:1003:Lazy LLM:/var/lib/lazy:/bin/false
lazy-policy:x:1004:1004:Lazy Policy:/var/lib/lazy:/bin/false
lazy-tasks:x:1005:1005:Lazy Tasks:/var/lib/lazy:/bin/false
lazy-fs:x:1006:1006:Lazy FS Broker:/var/lib/lazy:/bin/false
lazy-sys:x:1007:1007:Lazy Sys Broker:/var/lib/lazy:/bin/false
lazy-hw:x:1008:1008:Lazy HW Broker:/var/lib/lazy:/bin/false
lazy-web:x:1009:1009:Lazy Web Broker:/var/lib/lazy:/bin/false
lazy-comms:x:1010:1010:Lazy Comms Broker:/var/lib/lazy:/bin/false
lazy-secrets:x:1011:1011:Lazy Secrets Vault:/var/lib/lazy/secrets:/bin/false
lazy-outbox:x:1012:1012:Lazy Outbox:/var/lib/lazy:/bin/false
lazy-fetch:x:1013:1013:Lazy Fetcher:/var/lib/lazy:/bin/false
lazy-routines:x:1014:1014:Lazy Routines:/var/lib/lazy:/bin/false
lazy-audit:x:1015:1015:Lazy Audit:/var/lib/lazy:/bin/false
"""
    group_content = """root:x:0:
lazyos:x:1000:
lazy-gw:x:1001:
lazy-plan:x:1002:
lazy-llm:x:1003:
lazy-policy:x:1004:
lazy-tasks:x:1005:
lazy-fs:x:1006:
lazy-sys:x:1007:
lazy-hw:x:1008:
lazy-web:x:1009:
lazy-comms:x:1010:
lazy-secrets:x:1011:
lazy-outbox:x:1012:
lazy-fetch:x:1013:
lazy-routines:x:1014:
lazy-audit:x:1015:
"""
    (ROOTFS / "etc/passwd").write_text(passwd_content)
    (ROOTFS / "etc/group").write_text(group_content)
    (ROOTFS / "etc/hostname").write_text("lazy-os\n")
    (ROOTFS / "etc/machine-id").write_text("b0070000000000000000000000000001\n")
    (ROOTFS / "etc/fstab").write_text(
        "/dev/vda2 / squashfs ro,defaults 0 0\n"
        "/dev/vda3 /data btrfs rw,defaults 0 2\n"
        "tmpfs /run tmpfs mode=755,nosuid,nodev 0 0\n"
        "tmpfs /tmp tmpfs nosuid,nodev 0 0\n"
    )

    # Configure autologin for serial console
    autologin_dir = ROOTFS / "etc/systemd/system/serial-getty@ttyS0.service.d"
    autologin_dir.mkdir(parents=True, exist_ok=True)
    (autologin_dir / "autologin.conf").write_text(
        "[Service]\n"
        "ExecStart=\n"
        "ExecStart=-/sbin/agetty -o '-p -- \\\\u' --noclear --autologin root %I $TERM\n"
    )
    getty_wants = ROOTFS / "etc/systemd/system/getty.target.wants"
    getty_wants.mkdir(parents=True, exist_ok=True)
    sg_link = getty_wants / "serial-getty@ttyS0.service"
    if sg_link.exists() or sg_link.is_symlink():
        sg_link.unlink()
    os.symlink("/lib/systemd/system/serial-getty@.service", sg_link)

    # 7. Copy Python src tree into /usr/lib/python3/dist-packages/lazy
    src_lazy = REPO_ROOT / "src/lazy"
    dst_lazy = ROOTFS / "usr/lib/python3/dist-packages/lazy"
    if dst_lazy.exists():
        shutil.rmtree(dst_lazy)
    shutil.copytree(src_lazy, dst_lazy)
    log("Installed lazy Python package to /usr/lib/python3/dist-packages/lazy")

    # 8. Create SquashFS image
    log(f"Building {SQUASHFS_IMG} from {ROOTFS}...")
    if SQUASHFS_IMG.exists():
        SQUASHFS_IMG.unlink()
    run_cmd(f"mksquashfs {ROOTFS} {SQUASHFS_IMG} -comp gzip -noappend")
    sq_size_mb = SQUASHFS_IMG.stat().st_size / (1024 * 1024)
    log(f"SquashFS image built successfully: {sq_size_mb:.2f} MB")

    # 9. Write SquashFS image into Partition 2 of lazy-disk.img (/dev/vda2)
    log(f"Writing {SQUASHFS_IMG} into Partition 2 of {DISK_IMG}...")
    part2_offset = 34816 * 512 # sector 34816
    with open(DISK_IMG, "r+b") as disk_f:
        disk_f.seek(part2_offset)
        with open(SQUASHFS_IMG, "rb") as sq_f:
            shutil.copyfileobj(sq_f, disk_f)
    log("Partition 2 flashed with rootfs.squashfs")

    # 10. Build switch-root initramfs
    log("Building switch-root initramfs...")
    initramfs_staging = BUILD_DIR / "initramfs-staging"
    if initramfs_staging.exists():
        shutil.rmtree(initramfs_staging)
    
    for d in ["bin", "sbin", "dev", "proc", "sys", "sysroot", "mnt/overlay"]:
        (initramfs_staging / d).mkdir(parents=True, exist_ok=True)
    
    # Busybox for initramfs
    shutil.copy2(ROOTFS / "bin/busybox", initramfs_staging / "bin/busybox")
    for app in ["sh", "mount", "umount", "mkdir", "mknod", "switch_root", "echo", "cat", "sleep", "insmod"]:
        app_link = initramfs_staging / "bin" / app
        if not app_link.exists():
            os.symlink("/bin/busybox", app_link)
    
    # Kernel modules for btrfs, squashfs, overlay
    (initramfs_staging / "lib/modules").mkdir(parents=True, exist_ok=True)
    for m in ["libcrc32c.ko", "xor.ko", "raid6_pq.ko", "btrfs.ko"]:
        src_mod = ROOTFS / "lib/modules" / m
        if src_mod.exists():
            shutil.copy2(src_mod, initramfs_staging / "lib/modules" / m)

    # Initramfs /init script
    init_script = """#!/bin/busybox sh
export PATH=/bin:/sbin

/bin/busybox mount -t proc proc /proc
/bin/busybox mount -t sysfs sysfs /sys
/bin/busybox mount -t devtmpfs devtmpfs /dev 2>/dev/null || true

# Insert required modules
/bin/busybox insmod /lib/modules/libcrc32c.ko 2>/dev/null || true
/bin/busybox insmod /lib/modules/xor.ko 2>/dev/null || true
/bin/busybox insmod /lib/modules/raid6_pq.ko 2>/dev/null || true
/bin/busybox insmod /lib/modules/btrfs.ko 2>/dev/null || true

# Create block devices
/bin/busybox mknod /dev/vda b 254 0 2>/dev/null || true
/bin/busybox mknod /dev/vda1 b 254 1 2>/dev/null || true
/bin/busybox mknod /dev/vda2 b 254 2 2>/dev/null || true
/bin/busybox mknod /dev/vda3 b 254 3 2>/dev/null || true

/bin/busybox echo "=== LAZY OS BOOT: MOUNTING SQUASHFS ROOTFS ==="

# 1. Mount read-only root from /dev/vda2 (SquashFS)
/bin/busybox mkdir -p /sysroot
if /bin/busybox mount -t squashfs -o ro /dev/vda2 /sysroot 2>/dev/null; then
    /bin/busybox echo "[OK] Mounted read-only SquashFS root on /sysroot from /dev/vda2"
else
    /bin/busybox echo "[ERR] Failed to mount /dev/vda2 as squashfs!"
    /bin/busybox sleep 5
fi

# 2. Setup volatile tmpfs mounts for /run, /tmp, /var/log
/bin/busybox mount -t tmpfs -o mode=755 tmpfs /sysroot/run
/bin/busybox mount -t tmpfs tmpfs /sysroot/tmp
/bin/busybox mkdir -p /sysroot/var/log /sysroot/var/lib/lazy
/bin/busybox mount -t tmpfs tmpfs /sysroot/var/log

# 3. Setup volatile overlay for /etc
/bin/busybox mkdir -p /mnt/overlay
/bin/busybox mount -t tmpfs tmpfs /mnt/overlay
/bin/busybox mkdir -p /mnt/overlay/etc-upper /mnt/overlay/etc-work
/bin/busybox mount -t overlay overlay -o lowerdir=/sysroot/etc,upperdir=/mnt/overlay/etc-upper,workdir=/mnt/overlay/etc-work /sysroot/etc 2>/dev/null || true

# 4. Mount persistent Btrfs /data partition on /dev/vda3
/bin/busybox mkdir -p /sysroot/data
if /bin/busybox mount -t btrfs /dev/vda3 /sysroot/data 2>/dev/null; then
    /bin/busybox echo "[OK] Mounted persistent Btrfs partition on /sysroot/data from /dev/vda3"
elif /bin/busybox mount -t btrfs -o subvol=/ /dev/vda3 /sysroot/data 2>/dev/null; then
    /bin/busybox echo "[OK] Mounted persistent Btrfs partition (subvol=/) on /sysroot/data"
else
    /bin/busybox echo "[WARN] Could not mount Btrfs /dev/vda3; fallback tmpfs"
    /bin/busybox mount -t tmpfs tmpfs /sysroot/data
fi

/bin/busybox echo "=== SWITCHING ROOT TO SYSTEMD PID 1 ==="
exec /bin/busybox switch_root /sysroot /usr/lib/systemd/systemd
"""
    init_path = initramfs_staging / "init"
    init_path.write_text(init_script)
    init_path.chmod(0o755)

    # Pack initramfs
    run_cmd(f"cd {initramfs_staging} && find . | cpio -H newc -o | gzip -9 > {INITRAMFS_IMG}")
    init_size_mb = INITRAMFS_IMG.stat().st_size / (1024 * 1024)
    log(f"Switch-root dev initramfs generated: {init_size_mb:.2f} MB at {INITRAMFS_IMG}")
    log("DEV ONLY: Artifacts saved exclusively under build/dev/ (never copied to dist/).")
    log("Development image build complete!")

if __name__ == "__main__":
    main()
