# Task 2 Build System Comparison: Yocto Project vs. Buildroot (Lazy OS)

**Date**: 2026-11-20T23:35:00Z  
**Branch**: `feat/role-d-backup`  
**Reference Specification**: Track A Task 2 — Build System Selection & Comparative Evaluation  
**Hardware Profile**: x86_64 Edge ML Appliance (4 vCPUs AVX2, 4,096 MB RAM, QEMU KVM virtio-gpu)

---

## 1. Executive Summary & Build System Selection

For an edge appliance hosting a local 1.5B parameter neural language model (`Qwen2.5-1.5B-Instruct-Q4_K_M`), the operating system distribution must prioritize:
1. **Minimal Base Footprint**: Leaving maximum RAM available for model weights and KV-cache.
2. **Deterministic Immutability**: Read-only root filesystem with single-artifact deployment.
3. **Low Latency & High Isolation**: Zero background daemon overhead, deterministic systemd slices.
4. **Reproducible & Feasible Compilation**: Compiling cleanly on resource-constrained development machines without out-of-memory crashes.

Both **Yocto Project (Poky 5.0 Scarthgap)** and **Buildroot (2024.02.x)** were implemented, compiled, and benchmarked (`yocto/kas/lazy-base.yml`, `yocto/meta-lazy/` vs `lazy-br2/`). **Buildroot was selected as the operational distribution engine** for Lazy OS.

---

## 2. Empirical & Architectural Comparison Matrix

| Evaluation Dimension | Buildroot 2024.02 (Lazy OS) | Yocto Project (Poky 5.0 `scarthgap`) | Stock Debian 12 Minimal (Baseline) |
| :--- | :---: | :---: | :---: |
| **Build System Type** | Integrated Makefile-based rootfs builder | Layer-based BitBake task orchestrator | Pre-compiled binary package repository (`apt`) |
| **Layer / Config Definition** | `lazy-br2/` external tree + `lazy_defconfig` | `yocto/kas/lazy-base.yml` + `meta-lazy/` | `debootstrap` / `preseed.cfg` |
| **Clean Build Time** | **2,516 s (~42 min legal-info) + 468 s (kernel)** | **4,500 s (~75 min full source)** | N/A (pre-built binaries: ~6 min netinst) |
| **Incremental Repack Time** | **35–45 seconds** (`scripts/repack_rootfs.sh`) | **4–12 min** (sstate-cache replay) | N/A (`dpkg` unpack) |
| **Host Resource Requirement** | **$\le 12.0\text{ GB}$ RAM** (Runs in 11.8 GB WSL2) | **$\ge 16.0\text{ GB}$ RAM + swap** (43.57 GB total unlocked) | $\ge 2.0\text{ GB}$ RAM |
| **Disk Space Consumed by Build** | **14.2 GB** (`/home/manas/lazy-build/output`) | **28.0 GB** (17 GB build + 11 GB cache with `rm_work`) | ~2.5 GB (`/var/cache/apt`) |
| **Base OS Image Size (no weights)** | **315.32 MB** (SquashFS ro-root) | **175.25 MB** (ext4 rootfs) / **44.0 MB** (SquashFS-xz) | **924.0 MB** (-65.87% vs Lazy OS) |
| **Total Image Size (+1.5B GGUF)**| **1,379.32 MB** (1,064 MB Qwen2.5 weights) | **1,239.25 MB** (ext4 base + 1,064 MB weights) | **924.0 MB** (no model) |
| **Installed Package Count** | **40 packages** | **276 packages** (`lazy-image-base.rootfs.manifest`) | **281 packages** (-85.76% vs Lazy OS) |
| **Kernel Image (`bzImage`) Size** | **5.92 MB** (custom 6.6.21 monolithic) | **9.11 MB** (`6.6.160-yocto-standard`) | **7.87 MB** (stock generic 6.1.0-56) |
| **Kernel Modules Directory** | **0.0 MB** (monolithic built-in virtio/fs) | **178.0 MB** (`modules-qemux86-64.tgz`) | **396.0 MB** (`/lib/modules`) |
| **Cold Boot Time (10-run mean)** | **2.86 s** ($\sigma = 0.28\text{ s}$, Wayland GUI ready) | **3.15 s** ($\sigma = 0.72\text{ s}$, headless console to login) | **2.00 s** (headless text console only) |
| **Idle RAM Used (10-run mean)** | **324.30 MB** ($\sigma = 16.3\text{ MB}$, Wayland+15 units) | **233.74 MB** ($\sigma = 3.57\text{ MB}$, systemd multi-user base) | **115.27 MB** (headless, 0 security units) |
| **License / SBOM Tooling** | `make legal-info` $\implies$ `manifest.csv` | `INHERIT += "create-spdx"` $\implies$ SPDX 2.2 tarball | `dpkg-query` / `copyright` |
| **Package Management** | None (Single immutable squashfs image) | RPM package feeds (`dnf-native` / `smart`) | Debian `apt` / `dpkg` |
| **Update Mechanism** | A/B Rootfs atomic swap (`rauc` ready) | Atomic image or package-level delta feed | Mutable package-by-package upgrades |

*All Yocto metrics empirically measured from 10 consecutive cold-boot runs in QEMU (`bench/results/yocto_runs/run_*.log`) and recorded in `bench/results/yocto_metrics.json`.*

---

## 3. Deep Architectural Trade-Off Analysis

### 3.1 Build Complexity & Toolchain Mechanics
- **Buildroot**: Operates as a coherent, sequential Makefile engine. It builds a cross-toolchain (or wraps a pre-built Bootlin toolchain in 65s), compiles target packages directly into a single staging/target sysroot, and packs the final SquashFS. There is no intermediate package management metadata. This streamlined model enabled incremental rootfs updates in **35 seconds**.
- **Yocto Project**: Implements a distributed task executor (BitBake) where every recipe produces discrete packages (RPM/IPK) that are subsequently installed into a rootfs by a package manager backend (`dnf-native`). This architecture provides unmatched modularity and fine-grained sstate caching, but introduces Python parsing overhead and requires substantial host memory ($\ge 16\text{ GB}$). Following WSL2 memory allocation to 43.57 GB total memory, all 5,880 tasks compiled cleanly.

### 3.2 License Tracking & Software Bill of Materials (SBOM)
- **Buildroot (`make legal-info`)**: Out of the box, Buildroot downloads upstream tarballs, verifies hashes, extracts license texts to `dist/legal-info/licenses/`, and produces a machine-readable `manifest.csv` listing package name, version, license identifier, and source URL. Every one of the 40 target packages in Lazy OS was verified as strictly open source (Apache-2.0, MIT, GPLv2/v3, BSD, LGPL), with **0 proprietary or unverified blobs**.
- **Yocto Project (`create-spdx`)**: Yocto offers industry-leading SPDX 2.2 / 3.0 document generation directly integrated with National Vulnerability Database (NVD) CVE tracking via `INHERIT += "create-spdx"`, generating `lazy-image-base-qemux86-64.rootfs.spdx.tar.zst` alongside image manifests.

### 3.3 Appliance Deployment & Attack Surface
- **Edge Appliance Security**: Debian's open package manager (`apt install`) violates edge appliance immutability by allowing runtime package drift, arbitrary dependency resolution, and writable root compromises.
- **Buildroot Immutability**: Generates a read-only SquashFS partition (`/dev/root`) mounted directly by the custom kernel. State mutations are confined strictly to the Btrfs `/data` volume, enabling instant transactional rollback via Btrfs subvolume snapshots (`POST /api/tasks/undo`).
- **Yocto Modularity vs Appliance Leanliness**: While Yocto's base Stage A ext4 image is 175.25 MB (and SquashFS-xz is 44 MB), its package manifest contains 276 discrete packages and pulls in 178 MB of kernel modules, compared to Buildroot's monolithic 40-package appliance with 0 external `.ko` files.

---

## 4. Selection Justification Summary

Buildroot was chosen as the primary distribution engineering platform for Lazy OS because:
1. **Developer Velocity**: Incremental code updates and repack take under 1 minute (**35 seconds** via `repack_rootfs.sh`), essential for rapid development, testing, and continuous integration cycles.
2. **Minimal Attack Surface**: Exactly 40 packages vs Yocto's 276 packages and Debian's 281 packages (-85.8%), zero package manager binaries on the production guest image, and a monolithic kernel with 0 external `.ko` module overhead.
3. **Appliance Simplicity**: Eliminating intermediate package management databases and complex multi-layer BitBake configurations provided a robust, single-artifact immutable image ideal for edge appliance deployment.
