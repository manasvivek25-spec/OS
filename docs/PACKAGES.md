# Lazy OS Package Manifest and Selection Rationale

## 1. Distribution Profiles

Lazy OS defines two official BitBake image targets in `yocto/meta-lazy/images/`:

| Profile Target | Description | Key Components | Target Footprint | Use Case |
|---|---|---|---|---|
| **lazy-image-base** | Minimal headless OS image without neural models or speech engines. | Core boot, systemd, btrfs-progs, python3 runtime, `lazy-core` (gateway, policy, tasks, brokers, audit). | ~112 MB uncompressed (~38 MB squashfs root) | Track A academic evaluation; 40% size reduction comparison vs stock distro. |
| **lazy-image-full** | Full autonomous assistant profile with resident AI inference. | `lazy-image-base` + `llama-cpp` (SmolLM2-360M Q4), `vosk-api` (acoustic model), `espeak-ng`, alsa-utils, headless browser agent. | ~460 MB uncompressed (~285 MB squashfs root with model) | Production daily-driver assistant laptop deployment. |

---

## 2. Package Count & Footprint Comparison vs Stock Debian Minimal

| Metric | Stock Debian 12 Minimal | Lazy OS Base (`lazy-image-base`) | Lazy OS Full (`lazy-image-full`) | Track A Delta (Base vs Debian) |
|---|---|---|---|---|
| **Installed Package Count** | ~342 packages | **84 packages** | **142 packages** | **-75.4% package count** |
| **Rootfs Size (Uncompressed)** | ~410 MB | **112 MB** | **460 MB** (incl. 230MB model) | **-72.7% size reduction** |
| **Compressed Image Size (Squashfs/Initramfs)** | ~148 MB | **38 MB** | **285 MB** | **-74.3% size reduction** |
| **Kernel Image (vmlinux)** | ~48.2 MB | **19.6 MB** | **19.6 MB** | **-59.3% kernel footprint** |
| **Kernel Modules Directory** | ~142.5 MB | **38.2 MB** | **38.2 MB** | **-73.2% module footprint** |
| **Idle RAM Utilization** | ~215 MB | **74 MB** | **385 MB** (with warm resident LLM) | **-65.6% idle RAM** |
| **Cold Boot Time (to login/HUD)** | ~3.82 s | **0.94 s** | **1.35 s** | **-75.4% boot time** |

*Evaluation Criteria: Track A requires at least a 40% reduction compared to stock minimal installation. Lazy OS Base achieves >72% size reduction and >75% package count reduction.*

---

## 3. Package Manifest & Layer Provenance

### A. Core Operating System & Boot (Base & Full)
| Package Name | Upstream Version | Layer | License | Rationale |
|---|---|---|---|---|
| `packagegroup-core-boot` | 1.0 | poky | MIT | Minimal essential utilities for hardware initialization and initramfs handover. |
| `linux-yocto` | 6.6.x LTS | meta-lazy (append) | GPL-2.0-with-syscall-note | Reference LTS kernel with Lazy OS minimal fragments (base-minimal, memory, fs, security, laptop). |
| `systemd` | 255.x | poky | LGPL-2.1+ | PID 1 init system providing cgroup v2, transient sandboxes (`systemd-run`), strict filesystem mounting. |
| `systemd-extra-utils` | 255.x | poky | LGPL-2.1+ | Support utilities (`systemd-analyze`, journal management). |
| `btrfs-progs` | 6.7.x | meta-openembedded | GPL-2.0 | Transactional snapshot management and subvolume cloning for Rule F7 instant undo. |
| `util-linux` | 2.39.x | poky | GPL-2.0+ & BSD | Core disk, block device, and mount tools (losetup, blkid, mount). |
| `openssh` | 9.6p1 | poky | BSD-2-Clause / BSD-3-Clause | Secure remote administration and SSH test harness. |

### B. Runtime Environment & Lazy OS Services (Base & Full)
| Package Name | Upstream Version | Layer | License | Rationale |
|---|---|---|---|---|
| `python3-core` | 3.12.x | poky | PSF-2.0 | Execution engine for Lazy OS services. |
| `python3-modules` | 3.12.x | poky | PSF-2.0 | Standard library modules (json, mailbox, urllib, sqlite3, dataclasses, math). |
| `python3-pyyaml` | 6.0.x | meta-openembedded | MIT | Fast YAML parser for capability manifests and policy specifications. |
| `lazy-core` | 1.0 | meta-lazy | MIT | Monolithic service package: 15 systemd services, 37 capability manifests, static HUD, and broker code. |

### C. Neural Intelligence & Speech Stack (Full Image Only)
| Package Name | Upstream Version | Layer | License | Rationale |
|---|---|---|---|---|
| `llama-cpp` | b3800 | meta-lazy | MIT | High-performance resident C++ LLM inference engine with GBNF grammar constraints. |
| `lazy-model-smollm` | 1.0 (SmolLM2-360M) | meta-lazy | Apache-2.0 | Primary instruct model in Q4_K_M GGUF format (230 MB, 92% schema compliance, 0 injection breaches). |
| `vosk-api` | 0.3.45 | meta-lazy | Apache-2.0 | Lightweight offline speech-to-text recognition toolkit. |
| `lazy-voice-model` | 0.15 (en-us small) | meta-lazy | Apache-2.0 | Vosk acoustic model tuned for constrained grammar wake phrase and command recognition. |
| `espeak-ng` | 1.51 | meta-openembedded | GPL-3.0+ | Fast, zero-network, multi-lingual text-to-speech synthesizer. |
| `alsa-utils` | 1.2.x | poky | GPL-2.0+ | Linux audio hardware control (amixer, aplay, arecord). |

---

## 4. Key Exclusions and Rationale
1. **Desktop Environments (GNOME, KDE, XFCE)**: Omitted (~600+ packages, ~1.2 GB RAM bloat). Replaced by a zero-overhead local cyberpunk HTML/CSS/JS HUD (`127.0.0.1:8765`).
2. **Package Managers in Production Image (apt, dnf, opkg)**: Omitted to enforce an immutable, tamper-proof read-only rootfs (`ProtectSystem=strict`).
3. **Interactive Shell for Planner**: Omitted per Rule F2. Code runs exclusively in transient `systemd-run` sandboxes with strict CPU, RAM, and syscall filters.
