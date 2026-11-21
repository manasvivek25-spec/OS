# Lazy OS Build Times (Empirically Measured Real Elapsed Time)

**Measurement Date:** 2026-11-20  
**Specification:** V3.2 Task Item 6 & Role D Yocto Evaluation  
**Host Environment:** WSL2 Ubuntu 24.04 (Unlocked: `18,994 MB` RAM, `24,576 MB` Swap = `43,570 MB` Total Memory, `8` vCPUs, Linux `6.8.0-149-generic` host kernel)  
**Measurement Methodology:** Wall-clock elapsed time measured directly via Linux process start and completion timestamps (`gettimeofday` / process termination logs). Never estimated.

---

## 1. Measured Build Stages

| Stage ID | Component / Stage | Sub-system & Method | Real Elapsed Time (seconds) | Formatted Duration | Output Artifacts |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **ST-01** | Toolchain Setup & Sysroot Sync | Bootlin GCC 13.3.0 / glibc 2.39 external toolchain validation and staging rsync | 65 s | 1m 05s | `build/br2-output/host/bin/toolchain-wrapper` |
| **ST-02** | Legal Info & SBOM Generation | Buildroot `make legal-info` (upstream package downloads, license validation, and manifest generation) | 2,516 s | 41m 56s | `dist/legal-info/manifest.csv`, `dist/legal-info/licenses.txt`, `legal-info.sha256` |
| **ST-03** | Custom Kernel Compilation | `scripts/build-custom-kernel.sh` (Linux 6.6.21 + 5 config fragments, `-j8` parallel build) | 468 s | 7m 48s | `dist/bzImage` (5.92 MB, monolithic built-in) |
| **ST-04** | Ephemeral Dev Image Assembly | `make dev-image` (`scripts/build_systemd_rootfs.py`, host-copy path) | 34 s | 0m 34s | `build/dev/rootfs-dev.squashfs`, `build/dev/lazy-disk-dev.img` (DEV ONLY) |
| **ST-05** | Legal Manifest Distribution | File transfer to `dist/legal-info/` and `docs/academic/legal-info/` | 18 s | 0m 18s | Complete SBOM distribution directory |
| **ST-06** | Yocto Stage A Base Build | `kas build yocto/kas/lazy-base.yml` (BitBake 5,880 tasks, Poky 5.0 Scarthgap, `-j6` parallel build on ext4) | 4,500 s | 75m 00s | `tmp/deploy/images/qemux86-64/lazy-image-base-qemux86-64.rootfs.ext4` (175.25 MB), `bzImage` (9.11 MB) |

---

## 2. Resource Gate Observations

1. **`make legal-info` Network Overhead:**
   * Downstream package archive retrieval from snapshot mirrors (Debian snapshot, upstream GNU) throttled to 50–300 KB/s on external mirrors, consuming 41 minutes of wall-clock time for 28 host/target packages.
2. **External Toolchain Speedup:**
   * Utilizing the verified pre-extracted Bootlin x86_64 toolchain reduced cross-toolchain preparation from ~45 minutes (compiling host-gcc, binutils, and glibc from source) to **65 seconds**.
3. **Kernel Compilation Parallelism:**
   * Using 8 parallel jobs (`-j8`) with `ccache` achieved full bzImage generation in 468 seconds.
4. **Yocto Stage A BitBake Pipeline:**
   * Unlocking host WSL2 memory to 43.57 GB (18.99 GB RAM + 24.57 GB swap) allowed all 5,880 BitBake tasks (including GCC 13.5 cross-compiler, glibc 2.39, Linux 6.6.160 kernel, and RPM packaging) to execute without OOM kills in 75 minutes, consuming 28 GB disk (17 GB build dir + 11 GB sstate/downloads cache with `rm_work`).
