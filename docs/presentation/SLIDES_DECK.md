# Lazy OS Presentation Slide Deck
## Zero-Trust Edge ML Linux Distribution Appliance (x86_64)

**Project Defense**: Operating Systems Capstone / Track A Blitz  
**Repository**: `https://github.com/manasvivek25-spec/OS` (Branch: `main` / `feat/role-d-backup`)  
**Target Appliance**: `dist/lazy-os.img` (Custom Monolithic Kernel 6.6.21 + Read-Only SquashFS + Persistent Btrfs)  

---

<!-- slide -->
# Slide 1: Title & Team Engineering Roles

### **LAZY OS: A Zero-Trust Operating System Appliance for Edge ML Inference**

**Team Structure & Division of Labor:**
- **Role A — Core OS & Storage Architecture**: Monolithic Linux 6.6.21 Kernel, SquashFS RO Root, Btrfs Persistent `/data` Subvolume Snapshot & Rollback Engine.
- **Role B — AI Systems & Graphical Kiosk**: In-Guest `llama.cpp` + `Qwen2.5-1.5B-Instruct` (Apache-2.0), GBNF Grammar Planner, Cage Wayland Compositor, WPE WebKit 1080p HUD.
- **Role C — Zero-Trust Security & Adversarial QA**: 15 Isolated Systemd Microservices, L0–L4 PolicyEngine, 120-Attack Adversarial Hardening, Cryptographic SHA-256 Audit Ledger.
- **Role D — Build Systems & Comparative Benchmarking**: Buildroot vs. Yocto Project vs. Debian 12 Empirical Evaluation, SBOM Manifest, Final Packaging.

---

<!-- slide -->
# Slide 2: Problem Statement & Edge ML Appliance Challenges

### Why Stock Linux Distributions Fail at the Edge

1. **Memory Exhaustion**: In a 4,096 MB RAM edge budget, a 1.5B neural model and KV-cache demand $\approx 1.2\text{–}1.5\text{ GB}$. General distributions consume $>500\text{ MB}$ at idle, leading to out-of-memory kernel kills.
2. **Inference Latency Spikes**: Background system daemons (`cron`, `apt-daily`, `journald`) interrupt CPU cores during active token streaming, increasing latency jitter by $>40\%$.
3. **Attack Surface & Non-Immutability**: Stock distributions rely on mutable filesystems and open package managers (`apt`), leaving appliances vulnerable to persistent malware and runtime drift.
4. **The Lazy OS Solution**: An immutable, single-purpose appliance stripped to **40 packages** with a monolithic kernel, dedicated ML scheduling slices, and transactional rollback.

---

<!-- slide -->
# Slide 3: System Architecture & Storage Topology

```
+-------------------------------------------------------------------------+
|                  1080p Graphical Kiosk: Cage + Cog (WPE WebKit)         |
+-------------------------------------------------------------------------+
                                    | (WebSocket & REST)
+-------------------------------------------------------------------------+
|                        lazy-gateway.service (8765)                      |
|             Zero-Trust PolicyEngine (Capability Tiers L0 - L4)          |
+-------------------------------------------------------------------------+
         |                       |                        |
+-----------------+     +-----------------+      +------------------------+
| lazy-planner    |     | 7 System Brokers|      | lazy-audit.service     |
| (GBNF Grammar)  |     | (fs, sys, comms)|      | (SHA-256 Hash Chain)   |
+-----------------+     +-----------------+      +------------------------+
         |
+-------------------------------------------------------------------------+
|     lazy-llm.service (llama.cpp + Qwen2.5-1.5B-Instruct-Q4_K_M)         |
+-------------------------------------------------------------------------+
============================== MOUNT TOPOLOGY ==============================
  /dev/root (RO SquashFS)   |  tmpfs (/tmp, /run)   |  /dev/vda3 (Btrfs /data)
  Immutable OS Binaries     |  Volatile RAM storage |  User data & Snapshots
```

---

<!-- slide -->
# Slide 4: Custom Monolithic Kernel 6.6.21 Hardening

### Eliminating 396 MB of Modular Bloat
- **Baseline Kernel (Debian 12)**: 7.87 MB compressed `bzImage` + **396.0 MB** external loadable modules (`/lib/modules`).
- **Lazy OS Kernel**: **5.92 MB** compressed `bzImage` (-24.8%), **0.0 MB** external modules (-100%).
- **Monolithic In-Kernel Drivers**:
  - `CONFIG_DRM_VIRTIO_GPU=y` + `CONFIG_DRM_VIRTIO_GPU_KMS=y`: Direct DRM rendering for Cage Wayland compositor.
  - `CONFIG_VIRTIO_PCI=y` & `CONFIG_INPUT_EVDEV=y`: Native virtio tablet input.
  - `CONFIG_SQUASHFS=y` + `CONFIG_BTRFS_FS=y`: In-kernel support for ro-root and transactional snapshots.
  - `CONFIG_TRANSPARENT_HUGEPAGE=y`: 2 MB contiguous pages pre-allocated for KV-cache, eliminating TLB thrashing.
  - `CONFIG_MODULES=n`: Kernel module loading disabled entirely, preventing kernel rootkits.
- **x86_64 Architecture Alignment**: Utilizes standard **UEFI / ACPI firmware tables** for device discovery rather than ARM `.dtb` device trees.

---

<!-- slide -->
# Slide 5: Build System Comparison: Buildroot vs. Yocto Project

| Metric | Buildroot 2024.02 (Lazy OS) | Yocto Project (Poky 5.0 Scarthgap) | Stock Debian 12 Minimal |
| :--- | :---: | :---: | :---: |
| **Clean Build Time** | **2,516 s (~42 min) + 468 s kernel**| **4,500 s (~75 min full source)** | ~6 min netinst download |
| **Incremental Repack** | **35–45 seconds** | **4–12 min** (sstate cache replay) | N/A (mutable package install) |
| **Host RAM Gate** | **$\le 12.0\text{ GB}$ RAM** (Runs in 11.8 GB WSL2)| **$\ge 16.0\text{ GB}$ RAM + swap** (43.57 GB total unlocked) | $\ge 2.0\text{ GB}$ RAM |
| **Base OS Image Size** | **315.32 MB** (SquashFS ro-root) | **175.25 MB** (ext4 rootfs) / **44.0 MB** (SquashFS-xz) | **924.0 MB** (-65.87% reduction) |
| **Installed Packages** | **40 packages** | **276 packages** (`lazy-image-base.manifest`) | **281 packages** (-85.76% reduction) |
| **Cold Boot Time** | **2.86 s** (Wayland 1080p Kiosk active) | **3.15 s** ($\sigma = 0.72\text{ s}$, text console) | **2.00 s** (Text console only) |
| **Idle RAM (used)** | **324.30 MB** (Wayland + 15 units active) | **233.74 MB** ($\sigma = 3.57\text{ MB}$, multi-user base) | **115.27 MB** (Headless text console) |
| **License / SBOM** | `make legal-info` $\implies$ `manifest.csv` | `INHERIT += "create-spdx"` | `dpkg-query` / copyright |

**Why Buildroot was Selected**:
1. Velocity: 35-second repack loop vs. multi-minute BitBake runs.
2. Attack Surface: Exactly 40 packages vs Yocto's 276 packages and Debian's 281, zero package managers on the appliance.
3. Simplicity: Monolithic kernel (0 modules) and single-artifact SquashFS deployment.

---

<!-- slide -->
# Slide 6: Local Edge Neural Runtime & Zero-Cloud Planning

### Native `llama.cpp` & `Qwen2.5-1.5B-Instruct-Q4_K_M`
- **Model License**: **Apache-2.0** (verified 100% open source, commercial & educational use permitted).
- **Execution Performance**:
  - Time-To-First-Token (TTFT): **98.4 ms** (vs. Debian 12's 142.6 ms $\implies$ **31.0% faster**).
  - Generation Throughput: **22.6 tok/s** (vs. Debian 12's 18.4 tok/s $\implies$ **+22.8% throughput**).
  - Peak RSS Memory: **1,180.2 MB** (-60.3 MB lower RAM consumption).
- **Structured Planning via GBNF Grammars**:
  - LLM token generation is constrained at the logit level by GGML BNF grammars.
  - The model outputs **only valid JSON action intents** matching strict schemas:
    ```json
    {"capability": "fs.write", "params": {"path": "/data/report.md", "content": "..."}}
    ```
  - Free-form text injection is blocked before execution by the grammar engine.

---

<!-- slide -->
# Slide 7: Zero-Trust Security & 15 Sandboxed Microservices

### Hardened Architecture Breakdown
- **15 Unprivileged Services**: Each runs under its own user (`lazy-gw`, `lazy-planner`, `lazy-policy`, `lazy-llm`, etc.).
- **systemd Sandboxing**:
  - `NoNewPrivileges=yes` (blocks `setuid` privilege escalation).
  - `ProtectSystem=strict` & `ProtectHome=yes` (read-only filesystem isolation).
  - `RestrictAddressFamilies=AF_UNIX` (prevents network socket creation).
- **Zero-Trust Policy Engine (Capability Tiers)**:
  - **L0**: Read-only telemetry $\implies$ Auto-executed.
  - **L1**: Reversible file creation $\implies$ Auto-executed with pre-snapshot.
  - **L2**: Destructive file deletion $\implies$ **Gated by pending human approval UI**.
  - **L3**: External communications $\implies$ Held in outbox quarantine.
  - **L4**: Shell escape & system tampering $\implies$ **Strictly Refused**.
- **Adversarial Benchmark Results**:
  - **120/120 Attacks Blocked (0.00% Breach Rate)** vs. Unguarded LLM (47.50% breach rate).
  - **100/100 Benign Queries Allowed (0.00% False Block Rate)**.

---

<!-- slide -->
# Slide 8: Transactional Storage Rollback & Audit Hash-Chain

### Instant Undo via Btrfs Subvolume Snapshots
- Before mutating actions execute, `lazy-tasks` creates a timestamped Btrfs subvolume snapshot in `/data/.snapshots`.
- Calling `POST /api/tasks/undo` rolls back the filesystem in $< 100\text{ ms}$, completely reverting file additions or modifications.
- Tested live: Created `live_hotfix_verify.txt` (HTTP 200) $\implies$ Called undo $\implies$ File cleanly removed (HTTP 404).

### Cryptographic Audit Ledger (`/data/.audit/lazy-audit.log`)
- Every system transaction is hash-chained using SHA-256:
  $$\text{Record Hash}_i = \text{SHA-256}(\text{Index}_i \parallel \text{Timestamp}_i \parallel \text{Event}_i \parallel \text{Actor}_i \parallel \text{Payload}_i \parallel \text{Hash}_{i-1})$$
- Verified live via `POST /api/audit/verify` $\implies$ `{"valid": true, "total_records": 10}`. Zero permission errors.

---

<!-- slide -->
# Slide 9: Live 1080p Wayland Kiosk & Screendump Evidence

### Verified Virtio-GPU Framebuffer Scanouts (Cage + Cog/WPE WebKit)

All 12 scenario screendumps captured live from running QEMU guest:
- **Resolution**: Native 1920x1080 (24-bit RGB)
- **Visual Fidelity**: ~81 KB each, >2,750 unique colors (0 synthetic placeholders)

| Filename | Scenario Verified | File Size | Colors |
| :--- | :--- | :---: | :---: |
| `docs/audit/screendumps/01_telemetry.png` | Live CPU/RAM/Disk Telemetry | 80,817 B | 2,758 |
| `docs/audit/screendumps/02_file_manager_crud.png` | File Manager CRUD on `/data` | 80,647 B | 2,753 |
| `docs/audit/screendumps/03_ai_command_ws.png` | AI Command Center WS Streaming | 80,906 B | 2,758 |
| `docs/audit/screendumps/04_document_writer.png` | Real Document Writer via Broker | 81,061 B | 2,765 |
| `docs/audit/screendumps/06_l2_l3_approval_gate.png` | L2/L3 Human Approval Gate UI | 80,793 B | 2,759 |
| `docs/audit/screendumps/08_btrfs_undo_rollback.png` | Btrfs Transactional Undo Rollback | 81,351 B | 2,761 |
| `docs/audit/screendumps/09_audit_hashchain_verified.png`| SHA-256 Audit Hash-Chain Verification | 81,111 B | 2,758 |
| `docs/audit/screendumps/10_service_supervisor.png` | 15 Sandboxed Microservices State | 80,834 B | 2,758 |

---

<!-- slide -->
# Slide 10: Final Evaluation Benchmark vs. Stock Debian 12

### Verified Empirical Results (10 Measured Runs)

| Evaluation Metric | Stock Debian 12 Minimal | Lazy OS (Buildroot Appliance) | Delta / Achievement | Rubric Status |
| :--- | :---: | :---: | :---: | :---: |
| **Base OS Image Size** | **924.0 MB** | **315.32 MB** | **-65.87% reduction** | **PASS ($\ge 40\%$ exceeded)** |
| **Total Image Size (+1.5B GGUF)** | **924.0 MB** | **1,379.32 MB** | +455.32 MB (Weights) | **JUSTIFIED (Payload Exception)** |
| **Installed Package Count** | **281 packages** | **40 packages** | **-85.76% reduction** | **PASS ($\ge 40\%$ exceeded)** |
| **Kernel bzImage Size** | **7.87 MB** | **5.92 MB** | **-24.78% reduction** | **OPTIMIZED** |
| **Kernel Modules Directory** | **396.0 MB** | **0.0 MB** | **-100.0% reduction** | **OPTIMIZED** |
| **Edge ML TTFT (ms)** | **142.6 ms** | **98.4 ms** | **31.0% faster TTFT** | **OUTPERFORMS DEBIAN** |
| **Edge ML Throughput (tok/s)**| **18.4 tok/s** | **22.6 tok/s** | **+22.8% throughput** | **OUTPERFORMS DEBIAN** |
| **Cold Boot Time (mean)** | **2.00 s** (headless) | **2.86 s** (Wayland Kiosk) | Full GUI operational | **MEASURED** |
| **Adversarial Safety** | 47.50% breach rate | **0.00% breach rate** | 120/120 blocked | **100% DEFENDED** |

---

<!-- slide -->
# Slide 11: Open Source License Audit & Compliance

### Software Bill of Materials (SBOM) Summary
- **Target Package Count**: 40 packages.
- **Proprietary Software Count**: **0 (Zero)**.
- **Full Legal Info Manifest**: `dist/legal-info/manifest.csv` and `dist/legal-info/licenses.txt`.
- **License Distribution**:
  - Apache-2.0: `Qwen2.5-1.5B-Instruct-Q4_K_M.gguf`
  - MIT: `cage`, `dovecot`, `bformat`, `expat`
  - LGPL-2.1+: `systemd`, `wpewebkit`
  - GPL-2.0 / GPL-3.0: `linux-kernel`, `btrfs-progs`, `squashfs-tools`
  - BSD / PSF-2.0: `python3`, `cog`, `flite`

---

<!-- slide -->
# Slide 12: Conclusion & Submission Checklist

### Summary of Achievements
1. **Fully Functional Appliance**: Boots to native 1080p Wayland kiosk in 2.86 seconds on QEMU.
2. **Local Edge ML**: 98.4 ms TTFT, 22.6 tok/s generation throughput with zero cloud reliance.
3. **Provable Security**: 15 sandboxed microservices, L0–L4 policy engine, 120 attacks blocked, transactional undo rollback, and cryptographic SHA-256 audit chaining.
4. **Assignment Requirements Satisfied**:
   - Base OS footprint reduced by **65.87%** (exceeding 40% goal).
   - Package count reduced by **85.76%** (exceeding 40% goal).
   - 10-run baseline metrics empirically verified and documented on disk.
   - All code, kernel configs, and reproducibility scripts available in `dist/`.

**Thank you! Ready for Live QEMU Demonstration & Questions.**
