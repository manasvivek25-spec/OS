# V3.2 Build Paths and Provenance Audit

**Audit Date:** 2026-11-19  
**Status:** COMPLETE & VERIFIED  
**Auditor:** Lazy OS V3.2 Automated Audit  
**Contract Requirement:** V3.2 Task Item 1

---

## 1. Executive Summary & Provenance Classification

Under Truth Rules T1–T9 and V3.2 Build Provenance criteria, every artifact in `dist/` and `build/` has been traced to its producing script, Makefile target, and provenance origin:
- **Class (a)**: A clean build system compiling from source (Buildroot `lazy-br2/` or Yocto `yocto/meta-lazy/`).
- **Class (b)**: The custom kernel compiled from source by `scripts/build-custom-kernel.sh` using in-tree fragments.
- **Class (c)**: Binaries copied directly from the host system (`ldd`, `/usr`, `/lib`, `dpkg`).

Prior to V3.2, `make dist` attempted to invoke Buildroot via `build.sh`, but previous releases populated `dist/` using fallback Python scripts (`scripts/build_systemd_rootfs.py`, `scripts/build_image_v2.py`, and `scripts/build-boot-image.py`) that copied **375 ELF binaries and shared libraries across 77 host Ubuntu packages** directly into the guest image.

---

## 2. Artifact Provenance Matrix

| Artifact | Size | SHA-256 Checksum | Producing Script / Target | Origin Classification | Description / Origin Details |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `dist/bzImage` | 6,202,368 bytes (5.91 MB) | `4670163dd5e4bb5b657aead85417c8a840e3018e1604b266130c3f231798a48f` | `scripts/build-custom-kernel.sh` (or `lazy_x86_64_defconfig`) | **(b) Custom Kernel from Source** | Linux 6.6.21 compiled against `lazy-br2/board/lazy/linux/` configuration fragments. Zero Ubuntu host kernel code. |
| `dist/rootfs.squashfs` | 49,852,416 bytes (47.54 MB) | `d72a28e2cf3f8a6ed9acbbf516c68fc05d3fe57138ca415967ec14fd1ddb80b6` | `scripts/build_systemd_rootfs.py` | **(c) Host Binaries Copy** | SquashFS image containing systemd v255, Python 3.12, and 77 packages copied from host via `ldd` transitive closure. |
| `dist/lazy-initramfs.cpio.gz` | 2,277,866 bytes (2.17 MB) | `6a31a1211e3cd5ad5ad790d26f15f7934f2d8cb55aed7782d4445a93e5961b99` | `scripts/build_systemd_rootfs.py` | **(c) Host Binaries Copy** | Switch-root CPIO initramfs using host-copied BusyBox static binary and switch_root utilities. |
| `dist/rootfs.cpio.gz` | 38,979,362 bytes (37.17 MB) | `40e24d8a6dac71a639dce7cf266eef2510e9737a73b5273a0dbe2fc0b4e2eeeb` | `scripts/build_image_v2.py` / `scripts/build-boot-image.py` | **(c) Host Binaries Copy** | Legacy monolithic RAM initramfs root containing host binaries. Deprecated in V3.1 / V3.2. |
| `build/v2/lazy-disk.img` | 1,073,741,824 bytes (1.00 GB) | `30da21666024d73beac750ab40c616fe6f51878faa49b8fd77d8644d48fb436f` | `scripts/build_systemd_rootfs.py` | **(c) Hybrid Container** | GPT disk image containing EFI (FAT32), SquashFS root (`/dev/vda2`, Class c), and persistent Btrfs (`/dev/vda3`). |
| `dist/lazy-os.qcow2` | 267,976,704 bytes (255.56 MB) | `aa25b5ff9cb5666938864fe371e5866635c607eba8a26f688ac9e9b8d640f321` | `scripts/build_image_v2.py` (`qemu-img convert`) | **(c) Converted Host Image** | QCOW2 sparse format converted from legacy host-copied raw image. |
| `dist/lazy-os.vdi` | 282,071,552 bytes (269.00 MB) | `d241b7030beef3bf7d004ee6c5c180843a4912642baa4fa890f8406c32d090e5` | `scripts/build_image_v2.py` (`qemu-img convert`) | **(c) Converted Host Image** | VirtualBox VDI format converted from legacy host-copied raw image. |
| `dist/lazy-os.vmdk` | 272,957,440 bytes (260.31 MB) | `0c6a590e52a01a77adf96ee599a308e7b64f03565d1d5ed792d2a681f0d76d75` | `scripts/build_image_v2.py` (`qemu-img convert`) | **(c) Converted Host Image** | VMware VMDK format converted from legacy host-copied raw image. |
| `dist/run-lazy-os.sh` | 2,057 bytes | `554bf9a164daaefb01e8c307596648dbba6b7be9e37aca06d70d1a08a849ad94` | Repository source / launcher | Source Script | Shell launcher for Linux / WSL2 QEMU VM. |
| `dist/run-windows.ps1` | 907 bytes | `4bc646f49f29a9f505348e823b2cdb2a208fe0ea63b62f64268df5974828df44` | Repository source / launcher | Source Script | PowerShell launcher for Windows native QEMU. |
| `dist/run-wsl.sh` | 221 bytes | `cfa356877b7ab119f10c3356991fead6684547e6f569404373714d81deb2342b` | Repository source / launcher | Source Script | WSL2 helper invoker. |

---

## 3. Call Chain from `make dist`

The call chain from the repo root Makefile target `dist` is structured as follows:

```mermaid
flowchart TD
    A["make dist (Makefile:82)"] --> B["./build.sh base"]
    B --> C{"Check BUILD_SYSTEM"}
    C -->|yocto| D["./scripts/build-yocto.sh base"]
    C -->|buildroot (default)| E["Buildroot 2024.02 Entrypoint"]
    E --> F["make -C build/buildroot-2024.02 BR2_EXTERNAL=lazy-br2 O=build/br2-output lazy_x86_64_defconfig"]
    F --> G["make -C build/br2-output (Class a)"]
    G --> H["build/br2-output/images/lazy-os.img -> dist/"]

    subgraph "Legacy / Dev-Only Divergence (Class c)"
        DEV["make dev-image"] --> DEV_SCRIPT["scripts/build_systemd_rootfs.py"]
        DEV_SCRIPT --> HOST_CP["Copy 375 host binaries via ldd (libc, python3, systemd)"]
        HOST_CP --> DEV_ROOTFS["build/v2/rootfs.squashfs (Class c)"]
        DEV_SCRIPT --> DEV_IMG["build/v2/lazy-disk.img (Class c)"]
    end
```

### Detailed Trace of `make dist`:
1. **Target**: `make dist` invokes `build.sh base`.
2. **Execution in `build.sh`**:
   - `BUILD_SYSTEM=buildroot` by default.
   - Sets `BR_VERSION="2024.02"`, `BR_DIR="${REPO_ROOT}/build/buildroot-2024.02"`, `OUTPUT_DIR="${REPO_ROOT}/build/br2-output"`.
   - Downloads official Buildroot source tarball if missing.
   - Configures Buildroot using `lazy_x86_64_defconfig` with `BR2_EXTERNAL="${REPO_ROOT}/lazy-br2"`.
   - Invokes `make -C "${OUTPUT_DIR}"` to compile userland packages, systemd, btrfs-progs, python runtime, and kernel bzImage from source.
   - Copies generated images (`lazy-os.img` or `bzImage`) into `dist/`.

### Host-Copy Path Divergence (`scripts/build_systemd_rootfs.py`):
- When Buildroot was interrupted or bypassed during earlier rapid-iteration tasks, developers executed `python3 scripts/build_systemd_rootfs.py`.
- That script enumerated host paths (`/sbin/init`, `/usr/bin/python3`, `/usr/bin/btrfs`, `/lib/systemd/*`), executed `ldd` to find transitive shared libraries, and copied host Ubuntu 24.04 ELF binaries directly into `build/v2/lazy-os-rootfs`.
- Under V3.2 Task Rule 3, this path is strictly isolated as `make dev-image (DEV ONLY)`. It is forbidden from populating `dist/` and will never be used for benchmarks or official acceptance checks.
