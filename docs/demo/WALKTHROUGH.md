# Lazy OS Product Walkthrough & User Journey

**Target Release:** Lazy OS v3.4 Genuine Buildroot Release  
**Kernel:** Linux `6.6.21-lazy-os` (Custom Minimal)  
**Userland:** Buildroot 2024.02 LTS + Systemd 255 (PID 1)  
**Session Mode:** Full-Screen In-Guest Graphical Command Center (VirtIO-GPU / DRM / Cage / Cog)  
**Evidence Artifacts:** [`docs/demo/screens/`](screens/)  

---

## 1. Executive Summary & Architecture

Lazy OS is an AI-first, appliance-style operating system engineered from the ground up for privacy, deterministic security, and autonomous productivity. It eliminates host-browser reliance, telemetry backdoors, and cloud-bound inference by combining:

1. **Linux 6.6.21 Custom Kernel**: Monolithic, highly optimized bzImage (5.92 MB) with zero unnecessary drivers.
2. **Read-Only Root Filesystem**: SquashFS xz-compressed userland (315.32 MB) mounted read-only on `/dev/vda2`, overlaid with a volatile tmpfs for ephemeral writes (`/tmp`, `/run`).
3. **Persistent Btrfs Data Storage**: Dedicated persistent partition on `/dev/vda3` (`/data`) with snapshotting, quota management, and hardware state isolation.
4. **15 Isolated Systemd Microservices**: Microservices running under dedicated unprivileged system users (`lazy-audit`, `lazy-policy`, `lazy-planner`, etc.) with strict Linux sandbox parameters (`ProtectSystem=strict`, `NoNewPrivileges=yes`, `PrivateTmp=yes`).
5. **Deterministic Policy Enforcement**: Zero-trust multi-tier capability system (L0 read-only to L4 kernel/policy edit), blocking 100% of prompt injections and unauthorized operations before reaching the kernel.

---

## 2. Walkthrough & Visual Tour

### Stage 1: Cold Boot to In-Guest Command Center
Upon power-on, the custom UEFI bootloader loads `dist/bzImage` and `dist/rootfs.squashfs`. In under 3 seconds (empirically measured at **$2.86 \pm 0.28$ s**), systemd initializes hardware drivers, mounts the volatile overlay, attaches `/dev/vda3` to `/data`, and starts the graphical compositor directly on the guest framebuffer. No host web browser is ever launched.

---

### Stage 2: Home & Morning Briefing
![01_home.png](screens/01_home.png)

* **Module ID**: `tab-home`
* **Features**:
  * **Wake-Up Briefing**: Automatically synthesized morning digest summarizing pending notifications, overnight chores, and prioritized RSS feeds.
  * **One-Click Action Triggers**: Quick commands for common workflows (system diagnostics, offline package sync, mail fetch).
  * **System Vital Badges**: Instant visibility into uptime, kernel status, and memory availability.

---

### Stage 3: AI Command Center & Structured Planning
![02_ai_command.png](screens/02_ai_command.png)

* **Module ID**: `tab-ai`
* **Features**:
  * **Natural Language Prompting**: High-performance local language model (`SmolLM2-360M-Instruct-Q4_K_M.gguf` running via in-guest `llama.cpp`) translates conversational queries into executable task graphs.
  * **Deterministic Policy Interception**: Every plan step is submitted to the PolicyEngine before execution. Unauthorized actions (e.g., L4 kernel parameter modifications) are strictly refused.
  * **Interactive Plan Review & Rollback**: Dangerous operations (L3 file deletion, network outbox delivery) require explicit human approval and trigger automatic Btrfs snapshots for one-click rollback.

---

### Stage 4: Real-Time System Telemetry & Service Health
![03_system_monitor.png](screens/03_system_monitor.png)

* **Module ID**: `tab-system`
* **Features**:
  * **Live Hardware SVG Sparklines**: Dynamic telemetry for CPU utilization, RAM consumption, disk I/O, and loopback network throughput.
  * **15-Microservice Status Grid**: Continuous real-time health monitoring of all 15 guest daemons:
    * Core: `lazy-audit`, `lazy-policy`, `lazy-planner`, `lazy-tasks`, `lazy-secrets`, `lazy-gateway`, `lazy-llm`, `lazy-outbox`, `lazy-routines`, `lazy-fetcher`.
    * Brokers: `lazy-broker-fs`, `lazy-broker-web`, `lazy-broker-hw`, `lazy-broker-sys`, `lazy-broker-comms`.
  * **Process Tree Inspection**: Validates that PID 1 is systemd and every daemon operates in its assigned sandbox.

---

### Stage 5: Autonomous Agent Center & Broker Pipelines
![04_agent_center.png](screens/04_agent_center.png)

* **Module ID**: `tab-agents`
* **Features**:
  * **5-Stage Pipeline Telemetry**: Visualizes tasks flowing through `Ingest` $\to$ `Parse` $\to$ `Policy Guard` $\to$ `Execution` $\to$ `Audit Append`.
  * **Broker Coordination Cards**: Dedicated activity status for the File, Web, Hardware, System, and Comms brokers.
  * **Taint & Quarantine Tracking**: Displays untrusted content quarantined by the Web and Comms brokers.

---

### Stage 6: Persistent File Manager (`/data`)
![05_file_manager.png](screens/05_file_manager.png)

* **Module ID**: `tab-files`
* **Features**:
  * **Btrfs Persistent Storage**: Direct file explorer targeting `/data`, preserving user notes, tasks, models, and mail across reboots.
  * **Read-Only Root Protection**: Root filesystem (`/`, `/usr`, `/lib`) is physically mounted read-only SquashFS; attempts to write to system files are rejected by the kernel.
  * **Integrated Safe Editor & Snapshots**: Direct document editing with automated pre-modification snapshots stored in `/data/.snapshots`.

---

### Stage 7: Security Center & Cryptographic Audit Ledger
![06_security_center.png](screens/06_security_center.png)

* **Module ID**: `tab-security`
* **Features**:
  * **Multi-Tier Capability Legend**: Clearly defines privilege tiers (L0 Observation, L1 User State, L2 External Comms, L3 Sensitive Ops, L4 Critical System).
  * **SHA-256 Hash-Chained Audit Ledger**: Every action executed by an agent, broker, or user is cryptographically appended to an append-only hash chain.
  * **Live Tamper Verification**: One-click verification runs through the hash chain to confirm cryptographic integrity and detect any unauthorized log tampering.

---

### Stage 8: Modular App Launcher & In-Guest Tools
![07_app_launcher.png](screens/07_app_launcher.png)

* **Module ID**: `tab-apps`
* **Features**:
  * **Built-in Applications**: Quick access to Notes, Morning Briefing, Comms Outbox, and Niche Feed Aggregator.
  * **In-Guest Terminal**: Sandboxed terminal emulator running as unprivileged user `lazy` for direct command-line inspection.
  * **Comms Outbox**: Staged outbox queue enforcing a configurable delay window (default 30s) allowing users to cancel outbound communications.

---

### Stage 9: Appearance, Accessibility & Guest Identity
![08_settings.png](screens/08_settings.png)

* **Module ID**: `tab-settings`
* **Features**:
  * **WCAG AAA Compliance**: High-contrast theme (#0a0e17 background / #e2e8f0 foreground) achieving a measured **15.68:1** contrast ratio (surpassing 7.0:1 AAA standard).
  * **Accessibility Options**: Native support for `:focus-visible` keyboard outlines and `prefers-reduced-motion`.
  * **Guest Verification Card**: Displays current kernel release (`6.6.21-lazy-os`), boot ID, active mounts, and verified Git build hash.

---

## 3. Verification & Acceptance Reference

All capabilities demonstrated in this walkthrough are backed by automated tests in the Lazy OS Master Acceptance Suite (`scripts/accept.sh`). For raw execution logs and empirical test evidence, refer to:

* Master Acceptance Report: [`docs/ACCEPTANCE_REPORT.md`](../ACCEPTANCE_REPORT.md)
* 10-Run Cold Boot Baseline: [`bench/results/baseline_comparison.csv`](../../bench/results/baseline_comparison.csv)
* 120-Attack Adversarial Evaluation: [`bench/results/safety_metrics.csv`](../../bench/results/safety_metrics.csv)
* Systemd Hardening Exposure Scores: [`tests/results/acceptance/systemd_security_audit.log`](../../tests/results/acceptance/systemd_security_audit.log)
