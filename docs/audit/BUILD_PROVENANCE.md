# Lazy OS Build Provenance Audit (V2.A2)

**Audit Date:** 2026-11-16T01:08:45+05:30  
**Auditor:** Antigravity Autonomous Systems Engineer  
**Classification:** VERIFIED AUDIT (Empirical code & log tracing)

---

## 1. Kernel and Module Provenance

- **Booted Kernel File:** `/boot/vmlinuz-6.8.0-149-generic`
  - Referenced in [`scripts/build-boot-image.py`](file:///c:/Users/len/OS/scripts/build-boot-image.py#L9) and [`scripts/boot-and-explore.py`](file:///c:/Users/len/OS/scripts/boot-and-explore.py#L9).
  - **Origin:** The host Ubuntu 24.04 LTS kernel installed on WSL2.
  - **Yocto Custom Kernel:** Not used. The custom kernel recipes and configuration fragments defined in `yocto/meta-lazy/recipes-kernel/linux/files/*.cfg` were never compiled by Yocto/BitBake.
- **Kernel Modules:**
  - `/lib/modules/` was **omitted entirely** from the generated rootfs and initramfs (`scripts/build-boot-image.py` does not copy any kernel modules).
  - The guest kernel booted using only drivers monolithically compiled into the host Ubuntu kernel image.

---

## 2. RootFS and Initramfs Assembly

- **Script:** [`scripts/build-boot-image.py`](file:///c:/Users/len/OS/scripts/build-boot-image.py)
- **Assembly Directory:** `/tmp/lazy-os-rootfs` (line 16)
- **Initramfs Archive:** `/tmp/lazy-os-boot.cpio.gz` (lines 485–492, size ~22.6 MB compressed)
- **Virtual Disk:** `/tmp/lazy-disk.img` (lines 495–512, 256 MB GPT disk partitioned with `sfdisk`)
- **Binary Sources:**
  - **Busybox:** Copied from host `/bin/busybox` (line 42). Symlinks created for standard POSIX utilities (lines 45–63).
  - **C Libraries:** Shared objects (`libc.so.6`, `libssl.so.3`, `libcrypto.so.3`, etc.) copied directly from host `/lib/x86_64-linux-gnu/` (lines 66–92).
  - **Python Runtime:** Python 3.12 interpreter copied from host `/usr/bin/python3` (line 96); standard library copied from host `/usr/lib/python3.12` (line 102).
  - **Python Dependencies:** Dependencies (`jsonschema`, `attrs`, `rpds`, etc.) copied from host virtual environment `.venv/lib/python3.12/site-packages` (lines 108–116).
  - **Lazy OS Services:** Copied directly from repository directory `src/lazy/` to `/usr/lib/python3/dist-packages/lazy/` (line 119).
  - **HUD Assets:** Copied directly from repository directory `hud/` to `/usr/share/lazy/hud/` (line 125).

---

## 3. Init System & Process Supervision

- **Init Program:** `/init` (lines 424–479 of `scripts/build-boot-image.py`).
  - Implemented as a 55-line Busybox shell script (`#!/bin/busybox sh`).
  - Mounts `/proc`, `/sys`, `/run`, `/tmp`, and `/data` as `tmpfs` (lines 430–435).
  - Starts `/usr/bin/lazy-guest-daemon.py` in the background (line 448).
  - Executes `/etc/lazy/explore.sh` (line 468).
  - Drops into an interactive shell via `/bin/busybox cttyhack /bin/busybox sh` (line 476).
- **systemd Existence:**
  - **systemd DOES NOT exist in the guest.**
  - There is no `systemd` daemon, PID 1, or cgroup manager running inside the guest.
  - `/bin/systemctl` is a mock Python script synthesized at lines 162–244 of `scripts/build-boot-image.py` that intercepts CLI flags (`list-units`, `--failed`, `status`, `is-system-running`) and prints hardcoded static strings mimicking 15 active services.

---

## 4. What "Compressed RootFS" Actually Measured

- In previous milestone claims (e.g. M0.1, M6.1, and `docs/reports/results.md`), the 38 MB image size claim was derived as follows:
  - In `scripts/build-boot-image.py` line 491:
    `initramfs_size = Path("/tmp/lazy-os-boot.cpio.gz").stat().st_size` (22.63 MB).
  - In `bench/scripts/eval_baselines.py` lines 47–56:
    The benchmark comparison hardcoded:
    ```python
    "image_size_mb": 38.0,
    "idle_ram_mb": 74.0,
    "boot_time_s": 0.94,
    "package_count": 54,
    ```
  - **Finding:** The benchmark values were hardcoded script literals, not the result of measuring a built Yocto image or a real booted Debian 12 baseline.

---

## 5. BitBake & Yocto Build Evidence

- **BitBake Invocations:** **0**
- **BitBake Cooker Logs:** **None** (searched filesystem for `*bitbake*`, `*cooker*`, and `build-logs/`—no logs found).
- **Yocto Metadata:**
  - Recipes, layer configuration (`conf/layer.conf`), image recipes (`lazy-image-base.bb`, `lazy-image-full.bb`), and kas YAML specs (`lazy-base.yml`, `lazy-full.yml`) were authored correctly in `yocto/`, but neither `bitbake` nor `kas build` was ever executed on the host.
