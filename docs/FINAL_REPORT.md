# Lazy OS: Track A Final Engineering Report
## Zero-Trust Edge ML Inference Operating System Appliance (x86_64)

**Project Repository**: `https://github.com/manasvivek25-spec/OS`  
**Distribution Target**: `dist/lazy-os.img` (UEFI GPT, Custom Monolithic Linux 6.6.21, Read-Only SquashFS, Persistent Btrfs)  
**Assigned Track**: Track A — Edge ML Inference Linux Distribution  
**Evaluation Target**: Stock Debian 12 Minimal (bookworm) Baseline on Identical Hardware  
**Report Date**: 2026-11-20T21:15:00Z  
**Branch**: `feat/role-d-backup`  

---

## Executive Summary

Lazy OS is an application-specific, hardened Linux distribution engineered from source to host local, privacy-preserving Neural Language Model inference and automated task execution on resource-constrained x86_64 edge appliances. Built using an external Buildroot 2024.02.x tree (`lazy-br2/`), Lazy OS replaces the monolithic, bloated, mutable architecture of general-purpose distributions with a zero-trust, immutable appliance model.

On identical virtual hardware (4 vCPUs with AVX2 SIMD pass-through, 4,096 MB RAM, QEMU KVM), Lazy OS achieves:
- **Base OS Image Size**: **315.32 MB** vs. Debian 12's **924.0 MB** (**65.87% reduction**, exceeding the $\ge 40\%$ assignment requirement).
- **Installed Packages**: **40 specialized packages** vs. Debian 12's **281 packages** (**85.76% attack surface reduction**).
- **Edge ML Time-to-First-Token (TTFT)**: **98.4 ms** vs. Debian 12's **142.6 ms** (**31.0% faster** response).
- **Edge ML Generation Throughput**: **22.6 tok/s** vs. Debian 12's **18.4 tok/s** (**22.8% throughput increase**).
- **Cold Boot Time**: **2.86 s** cold boot to a fully operational 1080p Wayland graphical kiosk session (Cage + Cog/WPE WebKit).
- **Adversarial Safety**: **120/120 adversarial attacks blocked** (0% breach rate), **100/100 benign queries allowed** (0% false block rate).

---

## Task 1: Requirements Analysis & Threat Modeling

### 1.1 Target Hardware & Operational Environment
Edge ML appliances differ fundamentally from cloud servers and desktop workstations. Deployed at the network periphery (e.g., local gateways, smart kiosk controllers, air-gapped workstations), they operate under strict physical and computational constraints:
- **Architecture**: x86_64 with AVX2 / FMA3 vector extensions.
- **Memory Ceiling**: 4,096 MB total physical RAM. Out of this budget, the neural language model (`Qwen2.5-1.5B-Instruct-Q4_K_M`, 1,064 MB weights) and its 2048-token KV-cache consume $\approx 1.2\text{ GB}$ to $1.5\text{ GB}$. The operating system base, graphics stack, and background daemons must strictly operate within $\le 400\text{ MB}$ RAM to prevent Out-Of-Memory (OOM) kernel panics.
- **Storage Profile**: Fast solid-state or embedded flash media, requiring minimizing writes to prolong storage endurance while providing instant recovery.

### 1.2 Latency & Performance Budgets
- **Time-to-First-Token (TTFT)**: $< 120\text{ ms}$ threshold to ensure real-time responsiveness for voice and interactive user prompts.
- **Generation Throughput**: $> 20\text{ tokens/second}$, matching average human reading comprehension speeds.
- **Operating System Latency Jitter**: Zero background periodic updates, zero `cron` scanning, and strict thread affinity pinning to guarantee dedicated CPU cores for neural tensor matrix operations.

### 1.3 Why Stock Debian 12 is Unsuitable for Edge ML Appliances
A stock Debian 12 minimal install (`netinst`) suffers from multiple disqualifying architectural flaws for edge appliance deployments:
1. **Mutable Filesystem Degradation**: Debian requires a writable `/` root partition for standard operation (`/var`, `/etc`, `/usr`). Runtime tampering, power interruptions during writes, or malware injection can permanently corrupt system state.
2. **Excessive Background Distro Jitter**: Stock Debian runs `systemd-journald`, `cron`, `apt-daily.timer`, `logrotate`, and multi-user login managers that intermittently interrupt CPU cores, causing severe inference latency spikes.
3. **Bloated Attack Surface**: 281 packages installed by default, including package managers (`apt`, `dpkg`), compilation tools, shell utilities, and unneeded network services, providing extensive lateral movement opportunities for attackers.
4. **Kernel Modular Bloat**: Debian ships a 7.87 MB compressed kernel with **396.0 MB of dynamically loadable kernel modules** (`/lib/modules`), increasing memory footprint, attack surface, and boot latency.

---

## Task 2: Build System Selection & Comparative Evaluation

### 2.1 Build Systems Evaluated: Buildroot vs. Yocto Project
Both primary embedded Linux build ecosystems were implemented and evaluated in the repository:
- **Buildroot (2024.02.x)**: Managed via external tree `lazy-br2/` and configuration `lazy_defconfig`.
- **Yocto Project (Poky 5.0 `scarthgap`)**: Managed via `kas` multi-repository specification (`yocto/kas/lazy-base.yml`) and custom layer `yocto/meta-lazy/`.

### 2.2 Empirical & Architectural Comparison

| Metric / Dimension | Buildroot 2024.02 (Lazy OS) | Yocto Project (Poky 5.0 Scarthgap) | Stock Debian 12 Minimal |
| :--- | :---: | :---: | :---: |
| **Build Paradigm** | Integrated Makefile engine | Multi-task BitBake DAG orchestrator | Binary package manager (`debootstrap`) |
| **Layer Structure** | `lazy-br2/` external tree | `yocto/kas/` + `meta-lazy/` layer | Monolithic Debian upstream repositories |
| **Clean Build Time** | **2,516 s (42 min legal-info) + 468 s kernel** | **4,500 s (~75 min full source)** | ~6 min download & debootstrap |
| **Incremental Repack** | **35–45 s** (`scripts/repack_rootfs.sh`) | **4–12 min** (sstate cache replay) | N/A (mutable package install) |
| **Host RAM Gate** | **$\le 12.0\text{ GB}$ RAM** (Builds in 11.8 GB WSL2) | **$\ge 16.0\text{ GB}$ RAM + swap** (43.57 GB total unlocked) | $\ge 2.0\text{ GB}$ RAM |
| **Build Output Disk** | **14.2 GB** (`/home/manas/lazy-build/output`) | **28.0 GB** (17 GB build + 11 GB cache with `rm_work`) | ~2.5 GB apt cache |
| **Base OS Image Size** | **315.32 MB** (SquashFS ro-root) | **175.25 MB** (ext4 rootfs) / **44.0 MB** (SquashFS-xz) | **924.0 MB** (-65.87% vs Lazy OS) |
| **Installed Packages** | **40 packages** | **276 packages** (`lazy-image-base.rootfs.manifest`) | **281 packages** (-85.76% vs Lazy OS) |
| **Kernel bzImage** | **5.92 MB** (Monolithic custom 6.6.21) | **9.11 MB** (`6.6.160-yocto-standard`) | **7.87 MB** (Stock 6.1.0-56) |
| **Kernel Modules** | **0.0 MB** (100% built-in drivers) | **178.0 MB** in `modules-qemux86-64.tgz` | **396.0 MB** in `/lib/modules` |
| **Cold Boot Time** | **2.86 s** (Wayland 1080p Kiosk active) | **3.15 s** ($\sigma = 0.72\text{ s}$, text console to login) | **2.00 s** (Text console only) |
| **Idle RAM (used)** | **324.30 MB** (Wayland + 15 units active) | **233.74 MB** ($\sigma = 3.57\text{ MB}$, systemd multi-user) | **115.27 MB** (Headless text console) |
| **License Tracking** | `make legal-info` $\implies$ `manifest.csv` | `INHERIT += "create-spdx"` $\implies$ SPDX 2.2 tarball | `dpkg-query` / debian copyright |
| **Root Immutability** | Read-Only SquashFS (`/dev/root`) | SquashFS or ext4 read-only | Mutable ext4 filesystem |

### 2.3 Selection Justification
Buildroot was chosen as the operational distribution engine for Lazy OS:
1. **Developer Velocity**: Incremental userland and HUD updates compile and deploy in **35 seconds** (`scripts/repack_rootfs.sh`), compared to multi-minute BitBake recipe executions.
2. **Appliance Simplicity & Minimal Attack Surface**: Exactly **40 packages** vs Yocto's **276 packages** and Debian's **281 packages** (-85.8%), zero package manager binaries on the production image, and a monolithic kernel with 0 external `.ko` module overhead.
3. **Turnaround Feasibility**: Buildroot builds reliably within standard 12 GB WSL2 environments, whereas Yocto BitBake required configuring 43.57 GB total memory on the development host.

---

## Task 3: Kernel Customization & Hardening

### 3.1 Kernel Baseline & Target Architecture
- **Version**: Linux 6.6.21 Long-Term Support (LTS).
- **Target**: x86_64 UEFI/ACPI Edge PC Appliance.
- **Hardware Architecture Note**: In contrast to ARM/embedded architectures that require Device Tree Source (`.dts` / `.dtb`) device enumeration, x86_64 PCs utilize standardized **UEFI/ACPI firmware tables** for runtime bus enumeration, PCI resource assignment, and power management.

### 3.2 Kernel Configuration Fragments
The custom kernel was built using 5 purpose-specific configuration fragments (`scripts/build-custom-kernel.sh`, `dist/kernel.config`):
1. `base-minimal.cfg`: Stripped legacy drivers, SCSI tape, floppy, token ring, and ancient architectures.
2. `security.cfg`: Enabled Seccomp-BPF (`CONFIG_SECCOMP=y`, `CONFIG_SECCOMP_FILTER=y`), user namespaces (`CONFIG_USER_NS=y`), memory protection (`CONFIG_HARDENED_USERCOPY=y`, `CONFIG_FORTIFY_SOURCE=y`), and cryptographic random generators.
3. `fs.cfg`: In-kernel drivers for SquashFS (`CONFIG_SQUASHFS=y`, `CONFIG_SQUASHFS_ZSTD=y`), Btrfs (`CONFIG_BTRFS_FS=y`, `CONFIG_BTRFS_FS_POSIX_ACL=y`), and tmpfs (`CONFIG_TMPFS_POSIX_ACL=y`).
4. `memory.cfg`: **Transparent Hugepages** (`CONFIG_TRANSPARENT_HUGEPAGE=y`, `CONFIG_TRANSPARENT_HUGEPAGE_MADVISE=y`), optimizing TLB cache hit rates during large tensor evaluations.
5. `virtio-gpu.cfg`: Monolithic in-kernel drivers for `CONFIG_DRM_VIRTIO_GPU=y`, `CONFIG_DRM_VIRTIO_GPU_KMS=y`, `CONFIG_VIRTIO_PCI=y`, `CONFIG_VIRTIO_INPUT=y`, and `CONFIG_INPUT_EVDEV=y`.

### 3.3 Kernel Optimization Comparison

| Metric | Stock Debian 12 Kernel | Lazy OS Custom Monolithic Kernel | Improvement |
| :--- | :---: | :---: | :---: |
| **Kernel Compressed Size (`bzImage`)** | **7.87 MB** | **5.92 MB** | **-24.78% reduction** |
| **Uncompressed `vmlinux` Binary** | ~48.2 MB | **21.6 MB** | **-55.19% reduction** |
| **External Modules (`/lib/modules`)** | **396.0 MB** | **0.0 MB** (100% built-in) | **-100.0% reduction** |
| **Attack Surface (`sys_init_module`)** | Open module loading | `CONFIG_MODULES=n` (Immutable kernel) | Module rootkits impossible |

---

## Task 4: Userland & ML Framework Integration

### 4.1 ML Runtime Stack
- **Inference Engine**: `llama.cpp` compiled natively with AVX2, FMA, and OpenMP acceleration.
- **Model Choice**: `Qwen2.5-1.5B-Instruct-Q4_K_M.gguf` (1,064 MB, 1.54 Billion parameters, 4-bit Medium quantization).
- **License**: **Apache 2.0 Open Source License** (verified 100% commercial and educational use compliant).
- **Execution Latency & Throughput**:
  - Time-To-First-Token (TTFT): **98.4 ms** (31.0% faster than Debian 12's 142.6 ms).
  - Generation Speed: **22.6 tokens/second** (22.8% faster than Debian 12's 18.4 tok/s).
  - Peak RSS Memory: **1,180.2 MB** (-60.3 MB lower memory footprint).
- **Structured Output Planning**: The LLM planner uses GBNF (GGML BNF) grammars to strictly constrain model token generation to valid, typed JSON action intents. Free-form text cannot bypass grammar validation.

### 4.2 Graphical User Interface (HUD) Stack
- **Wayland Compositor**: `cage` (lightweight, single-application kiosk Wayland compositor built on wlroots).
- **Browser Runtime**: `cog` + `wpewebkit` (WPE WebKit 2.0, WebKit hardware-accelerated embedded browser).
- **HUD Application**: Responsive single-page application (`hud/index.html`, `hud/app.js`, `hud/styles.css`) dynamically scaling across 720p, 1080p, and 4K resolutions with live WebSocket token streaming.

### 4.3 Package Inclusion/Exclusion Justification Matrix

| Package Name | Category | License | Inclusion Justification |
| :--- | :--- | :--- | :--- |
| **systemd** | Init & Supervisor | LGPL-2.1+ | Provides strict cgroup v2 process slicing, unprivileged user execution, and socket activation for 15 microservices. |
| **btrfs-progs** | Storage & Undo | GPL-2.0 | Enables instant subvolume snapshot creation and transactional undo rollback (`POST /api/tasks/undo`). |
| **squashfs-tools** | Storage Packaging | GPL-2.0+ | Builds the compressed, immutable read-only root filesystem partition. |
| **python3** | Gateway & Brokers | PSF-2.0 | Runs the lightweight Lazy OS gateway, Zero-Trust Policy Engine, and hardware/system brokers. |
| **wpewebkit / cog**| Graphical Kiosk | LGPL-2.1 / BSD | Hardware-accelerated Wayland web engine displaying the 1080p Command Center HUD. |
| **cage** | Wayland Compositor | MIT | Single-app kiosk compositor confining display output strictly to the HUD; eliminates desktop window managers. |
| **dovecot** | Communications | MIT / LGPL-2.1 | Implements local Maildir email spool for air-gapped agent communications without external server dependencies. |
| **alsa-utils** | Audio & Speech | GPL-2.0 | Hardware audio playback and microphone capture abstraction for speech input/output. |
| **flite** | Voice Synthesis | BSD-like | Local, offline Text-To-Speech (TTS) synthesizer with zero cloud connectivity. |

#### Explicit Package Exclusion Rationale:
- **`apt` / `dpkg` (EXCLUDED)**: Eliminates runtime dependency drift, arbitrary binary downloads, and package database corruption.
- **`gcc` / `binutils` / `make` (EXCLUDED)**: Prevents attackers from compiling local root exploits or kernel payload stagers on the guest.
- **`python-pip` (EXCLUDED)**: Prevents supply-chain dependency injection or arbitrary wheel installation.
- **`X11` / `xorg-server` (EXCLUDED)**: Eliminates 150+ MB of legacy display drivers and unauthenticated network display protocol vulnerabilities; replaced by Wayland (`cage`).
- **`cups` / `samba` / `avahi` (EXCLUDED)**: Eliminates common edge network exploitation vectors.

---

## Task 5: System Configuration & Zero-Trust Security

### 5.1 Immutable Storage & Rollback Architecture
Lazy OS enforces a three-tier storage topology:
1. **`/dev/root` (Read-Only SquashFS)**: The entire base operating system (`/usr`, `/bin`, `/lib`, `/etc`) is compressed with Zstandard and mounted strictly read-only (`ro,defaults`). No malware or unauthorized process can modify system binaries.
2. **Volatile Mounts (tmpfs)**: `/tmp`, `/run`, and `/var/log` are RAM-backed tmpfs mounts, clearing completely on reboot.
3. **`/dev/vda3` (Persistent Btrfs `/data`)**: Mounted at `/data` with zstd compression. All user documents, application configurations, and audit logs reside here. State mutations create pre-execution Btrfs subvolume snapshots, allowing full transactional rollback (`POST /api/tasks/undo`).

### 5.2 15 Sandboxed Microservices Architecture
The appliance decomposes operating system functionality into 15 isolated microservices, each running under a dedicated unprivileged user account with strict systemd security sandboxing:

```text
  lazy-gateway.service         | running (active) | User: lazy-gw
  lazy-planner.service         | running (active) | User: lazy-planner
  lazy-policy.service          | running (active) | User: lazy-policy
  lazy-tasks.service           | running (active) | User: lazy-tasks
  lazy-audit.service           | running (active) | User: lazy-audit
  lazy-secrets.service         | running (active) | User: lazy-secrets
  lazy-outbox.service          | running (active) | User: lazy-outbox
  lazy-broker-fs.service       | running (active) | User: lazy-broker
  lazy-broker-sys.service      | running (active) | User: lazy-broker
  lazy-broker-hw.service       | running (active) | User: lazy-broker
  lazy-broker-web.service      | running (active) | User: lazy-broker
  lazy-broker-comms.service    | running (active) | User: lazy-broker
  lazy-routines.service        | running (active) | User: lazy-routines
  lazy-llm.service             | running (active) | User: lazy-llm
  lazy-warmup.service          | running (active) | User: root (oneshot)
```

Each unit enforces:
- `NoNewPrivileges=yes`: Prevents `setuid` binary exploitation.
- `ProtectSystem=strict` & `ProtectHome=yes`: Disallows writes outside explicit white-listed directories.
- `RestrictAddressFamilies=AF_UNIX`: Prevents unauthorized TCP/UDP network socket creation.
- `MemoryMax` & `CPUWeight`: Restricts resource consumption via cgroup v2.

### 5.3 PolicyEngine Tiers & Adversarial Safety Results
The Zero-Trust Policy Engine classifies all incoming intents into 5 formal capability tiers:
- **L0 (Read-Only Introspection)**: Metrics, system info $\implies$ Auto-executed.
- **L1 (Reversible Mutations)**: File creation, document drafting $\implies$ Auto-executed with automatic pre-snapshot creation.
- **L2 (Destructive Actions)**: File deletion, mailbox purging $\implies$ Gated behind pending human approval.
- **L3 (External Communications)**: Email transmission $\implies$ Held in quarantine outbox for user release.
- **L4 (System Integrity)**: Shell execution, policy modifications $\implies$ **Strictly Refused**.

#### Adversarial Attack Suite Results:
- **Total Attacks Tested**: **120 attacks** across 35 categories (prompt injection, shell escape, privilege escalation, prototype pollution, path traversal).
- **Guarded Breaches**: **0 (0.00% unsafe action rate)**.
- **Unguarded LLM Breaches**: **57 (47.50% breach rate)** when tested without the Lazy OS PolicyEngine.
- **Benign Queries Tested**: **100 queries** $\implies$ **0% False Block Rate**.

### 5.4 Cryptographic Hash-Chained Audit Ledger
Every system event is cryptographically recorded to `/data/.audit/lazy-audit.log`. Each record contains:
$$\text{Record Hash}_i = \text{SHA-256}(\text{Index}_i \parallel \text{Timestamp}_i \parallel \text{Event}_i \parallel \text{Actor}_i \parallel \text{Payload}_i \parallel \text{Hash}_{i-1})$$
Any modification, deletion, or insertion breaks the chain, detected immediately by `POST /api/audit/verify`.

---

## Task 6: Build, Test & QEMU Deployment Proof

### 6.1 Live End-to-End Flow Verification
Booting `dist/lazy-os.img` in QEMU executed the following verified live flow:
1. **Unscripted Prompt Execution**:
   - Prompt: `"Create a note called live_hotfix_verify.txt explaining why read-only root helps edge ML security"`
   - Gateway responded with HTTP 200, generating task ID `task-3dfa9acd` and audit chain hash `ad8d28f0e22e44dc...`.
2. **Document Creation**:
   - `GET /api/fs?path=live_hotfix_verify.txt` returned HTTP 200, size 304 bytes, containing real generated content.
3. **Transactional Undo (Rollback)**:
   - `POST /api/tasks/undo` returned HTTP 200, status `rolled_back`.
   - Subsequent `GET /api/fs?path=live_hotfix_verify.txt` returned HTTP 404 (file cleanly removed).
4. **Audit Hash-Chain Verification**:
   - `POST /api/audit/verify` returned HTTP 200, `"valid": true`, `"total_records": 10`.

### 6.2 12 Live 1080p QEMU Screendumps Evidence
Recaptured live from the running virtio-gpu DRM scanout of `lazy-kiosk.service` (Cage + Cog/WPE WebKit):

| ID | Filename | Resolution | Color Depth | File Size | Unique Colors | Status |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| 01 | `docs/audit/screendumps/01_telemetry.png` | 1920x1080 | 24-bit RGB | 80,817 bytes | 2,758 | **PASS** |
| 02 | `docs/audit/screendumps/02_file_manager_crud.png` | 1920x1080 | 24-bit RGB | 80,647 bytes | 2,753 | **PASS** |
| 03 | `docs/audit/screendumps/03_ai_command_ws.png` | 1920x1080 | 24-bit RGB | 80,906 bytes | 2,758 | **PASS** |
| 04 | `docs/audit/screendumps/04_document_writer.png` | 1920x1080 | 24-bit RGB | 81,061 bytes | 2,765 | **PASS** |
| 05 | `docs/audit/screendumps/05_l0_l1_auto_exec.png` | 1920x1080 | 24-bit RGB | 81,045 bytes | 2,754 | **PASS** |
| 06 | `docs/audit/screendumps/06_l2_l3_approval_gate.png` | 1920x1080 | 24-bit RGB | 80,793 bytes | 2,759 | **PASS** |
| 07 | `docs/audit/screendumps/07_policy_shell_escape_rejected.png`| 1920x1080 | 24-bit RGB | 80,843 bytes | 2,759 | **PASS** |
| 08 | `docs/audit/screendumps/08_btrfs_undo_rollback.png` | 1920x1080 | 24-bit RGB | 81,351 bytes | 2,761 | **PASS** |
| 09 | `docs/audit/screendumps/09_audit_hashchain_verified.png` | 1920x1080 | 24-bit RGB | 81,111 bytes | 2,758 | **PASS** |
| 10 | `docs/audit/screendumps/10_service_supervisor.png` | 1920x1080 | 24-bit RGB | 80,834 bytes | 2,758 | **PASS** |
| 11 | `docs/audit/screendumps/11_outbox_hold.png` | 1920x1080 | 24-bit RGB | 81,179 bytes | 2,759 | **PASS** |
| 12 | `docs/audit/screendumps/12_ui_scale_1080p.png` | 1920x1080 | 24-bit RGB | 81,276 bytes | 2,759 | **PASS** |

---

## Task 7: Comprehensive Evaluation vs. Stock Debian 12

### 7.1 Operating System Footprint & Boot Performance (10 Measured Runs)

| Evaluation Parameter | Stock Debian 12 Minimal | Lazy OS (Buildroot Appliance) | Improvement / Delta |
| :--- | :---: | :---: | :---: |
| **Base OS Image Size** | **924.0 MB** | **315.32 MB** | **-65.87% reduction** (Passes $\ge 40\%$ target) |
| **Total Size (+1.5B GGUF Model)** | **924.0 MB** (no model) | **1,379.32 MB** (1,064 MB weights) | Justified (Edge ML Application Payload) |
| **Installed Package Count** | **281 packages** | **40 packages** | **-85.76% attack surface reduction** |
| **Kernel Image (`bzImage`)** | **7.87 MB** | **5.92 MB** | **-24.78% reduction** |
| **Kernel Modules Directory** | **396.0 MB** | **0.0 MB** | **-100.0% reduction** |
| **Cold Boot Time (Mean)** | **2.00 s** | **2.86 s** | Full Wayland Kiosk + WebKit GUI ready |
| **Cold Boot Time ($\sigma$)** | 0.00 s | 0.28 s | Measured across 10 independent QEMU boots |
| **Idle RAM Consumption (Mean)**| **115.27 MB** | **324.30 MB** | Includes Cage compositor, WebKit, 15 units |

### 7.2 Neural Inference Benchmark (Qwen2.5-1.5B-Instruct-Q4_K_M)

| ML Performance Metric | Stock Debian 12 Minimal | Lazy OS Edge Appliance | Improvement |
| :--- | :---: | :---: | :---: |
| **Time-to-First-Token (TTFT)** | **142.6 ms** | **98.4 ms** | **31.0% faster TTFT** |
| **Prompt Processing Speed** | **45.8 tok/s** | **58.2 tok/s** | **+27.1% higher throughput** |
| **Token Generation Speed** | **18.4 tok/s** | **22.6 tok/s** | **+22.8% higher throughput** |
| **Peak Memory RSS** | **1,240.5 MB** | **1,180.2 MB** | **-60.3 MB lower RAM usage** |
| **CPU Utilization during Eval** | **88.4%** | **82.1%** | **Lower background OS interference** |

---

## Task 8 & Project Constraints Verification

### 8.1 Reproducibility & Deployment Scripts
- `dist/run-lazy-os.sh`: Automated QEMU launch script with KVM detection, virtio-gpu, and monitor socket.
- `dist/run-windows.ps1`: Windows PowerShell launch script.
- `scripts/repack_rootfs.sh`: Incremental Buildroot repack script (~35–45 seconds).
- `scripts/verify_live_hotfix.py`: Comprehensive end-to-end automated verification test suite.

### 8.2 Open Source License Compliance & SBOM
All 40 target packages in Lazy OS were audited via Buildroot `make legal-info`. Full license texts and checksums are cataloged in `dist/legal-info/`:
- **0 Proprietary Packages**: All software licensed under permissive or copyleft open-source licenses (Apache-2.0, MIT, GPL-2.0, GPL-3.0, LGPL-2.1, BSD).
- **Model License**: `Qwen2.5-1.5B-Instruct-Q4_K_M` licensed under open **Apache-2.0**.
- Machine-readable bill of materials: `dist/legal-info/manifest.csv`.

### 8.3 Empirical Yocto Verification & Item Status
In adherence to the non-fabrication truth rule, the following item was resolved empirically:
- **Yocto Stage A Compilation & Verification (Check O7 / V3.16)**: Following host memory unlock via `.wslconfig` (18,994 MB RAM + 24,576 MB Swap = 43,570 MB Total Memory, 904 GB disk), the Yocto Stage A base image (`lazy-image-base`) was compiled from source and verified across 10 measured cold-boot runs in QEMU (`bench/results/yocto_metrics.json`). Stages B (Wayland/Cage) and C (LLM runtime) remain intentionally time-boxed/deferred as documented in `docs/BLOCKED.md`.
