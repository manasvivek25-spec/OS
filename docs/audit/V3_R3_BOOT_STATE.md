# Milestone R3: Real Boot State Audit & Reality Check

**Date**: 2026-11-19T06:58:00Z  
**Log Path**: [`tests/results/acceptance/R3_boot_state.log`](file:///c:/Users/len/OS/tests/results/acceptance/R3_boot_state.log)  
**Kernel Booted**: `dist/bzImage` (Linux `6.6.21-lazy-os`)  
**Initramfs Booted**: `build/v2/lazy-os-boot.cpio.gz`  
**Disk Image**: `build/v2/lazy-disk.img` (Partition 3: Btrfs `/data`)

---

## 1. Raw Execution Results Summary

| Target Check / Command | Actual Output from Booted Guest | Contract Compliance Status | Violation / Root Cause |
| :--- | :--- | :---: | :--- |
| **`uname -a`** | `Linux lazy-os 6.6.21-lazy-os #3 SMP PREEMPT_DYNAMIC x86_64` | **PASS (O2)** | Genuine custom kernel compiled from fragments. |
| **`cat /proc/version`** | `Linux version 6.6.21-lazy-os ... gcc 13.3.0` | **PASS (O2)** | Confirms custom Buildroot kernel source build. |
| **`ps -p 1` / `ps`** | `PID 1 root {init} /bin/busybox sh /init` | **VIOLATION (K2 / O3)** | PID 1 is BusyBox ash shell, NOT `systemd`. |
| **`systemctl list-units 'lazy-*'`** | `sh: systemctl: not found` | **VIOLATION (K3 / O3)** | `systemd` userland is absent from rootfs; no unit manager installed. |
| **`ps -eo user,pid,rss,comm`** | Only `PID 78 root /usr/bin/python3 /usr/bin/lazy-guest-daemon.py` | **VIOLATION (K3 / O3 / S3)** | Monolithic Python daemon running as `root`. Zero process separation for the 15 microservices. |
| **`findmnt` / `mount`** | `rootfs on / type rootfs (rw,size=485248k,nr_inodes=121312)` | **VIOLATION (K2 / O4)** | Root is an in-memory CPIO RAM filesystem mounted `rw`. |
| **`touch /testfile`** | File created successfully (`-rw-r--r-- 1 root 0 0 /testfile`) | **VIOLATION (O4 / O5)** | Root filesystem is writable in RAM; write to `/` was NOT refused. |
| **`df -h`** | `/dev/vda3 512.0M 264.4M 172.9M 60% /data` | **PASS (O4)** | Genuine Btrfs partition on `/dev/vda3` mounted at `/data`. |
| **`free -m`** | `Mem: 988 total, 46 used, 828 free, 754 available` | **MEASURED** | Actual cold idle RAM under 1024 MB VM is 46 MB used, 234 MB (MemTotal - MemAvailable). |
| **`/proc/meminfo`** | `MemTotal: 1011672 kB, MemFree: 847676 kB, MemAvailable: 772420 kB` | **MEASURED** | Raw kernel memory statistics recorded. |

---

## 2. Comparison with Architecture Constraints (K2, K3, O3, O4)

1. **K2 & O4 (Filesystem Architecture)**:
   - **Requirement**: Root must be a read-only SquashFS or EROFS image where `touch /testfile` fails with `Read-only file system`, with a volatile overlay for writable paths (`/etc`, `/run`), and persistent Btrfs on `/data`.
   - **Current Reality**: Root is a 38 MB compressed CPIO archive unpacked directly into RAM as a `rootfs` tmpfs. It accepts writes anywhere.
2. **K3 & O3 (Systemd & Microservices)**:
   - **Requirement**: `systemd` must run as PID 1, managing at least 15 separate `lazy-*` services under separate unprivileged system users in dependency order.
   - **Current Reality**: BusyBox `/init` starts a single monolithic script `/usr/bin/lazy-guest-daemon.py` as root.
3. **K4 & P1 (In-Guest Graphical Session)**:
   - **Requirement**: The guest must boot directly to a full-screen graphical session on its own display, with no host browser involvement.
   - **Current Reality**: The guest runs headless or drops to a serial terminal shell. The Command Center is served over TCP port forward to the host browser.

---

## 3. Plan for Milestones R4, R5, R6

- **R4**: Build a true read-only SquashFS root filesystem (`rootfs.squashfs`), create an initramfs that sets up the read-only squashfs root with a tmpfs overlay (`/etc`, `/var`, `/run`) and mounts `/dev/vda3` (Btrfs) on `/data`. Verify `touch /testfile` fails with `Read-only file system` and `/data` persists.
- **R5**: Implement graphical kiosk inside the guest using direct DRM/KMS or Wayland compositor displaying the Command Center UI on the guest virtio display, captured via QEMU screendump.
- **R6**: Implement real process isolation for the 15 microservices under unprivileged users with sandboxing.
