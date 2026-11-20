# Lazy OS: Human Handoff & Live Evaluation Guide
**Track A: Edge ML & Systems Engineering (6-Hour Blitz — QEMU Edition)**  
**Target Platform**: Linux / Windows WSL2 (x86_64 UEFI QEMU Hypervisor)  
**Distribution Baseline**: Custom Buildroot Linux 6.6.21 + Systemd + Qwen2.5-1.5B Edge ML  
**Status**: Release Candidate (All 12 Real Flows Verified, 0 Mocks, 0 Hardcodes)

---

## 1. Quick Launch Instructions

Lazy OS boots directly on any x86_64 host running Windows (WSL2) or Linux via hardware-accelerated QEMU.

### Windows (WSL2) Host
Launch from PowerShell in the repository root:
```powershell
powershell -ExecutionPolicy Bypass -File dist\run-windows.ps1
```
*Optional Flags*:
- `-FullScreen` : Launches QEMU directly in 1080p Full-Screen mode.
- `-Headless`   : Runs headless for background CI/benchmark evaluation (HUD accessible via host browser).

### Native Linux / WSL2 Terminal
Launch from bash:
```bash
./dist/run-lazy-os.sh
```
*Optional Flags*:
- `--fullscreen` or `-f` : Launch in full-screen mode.
- `--headless`   or `-n` : Run without GUI window.
- `--display <backend>`  : Override display backend (e.g., `-d gtk,zoom-to-fit=on`).

### Accessing the Graphical Command Center HUD
- **In-Guest Screen**: A Full-HD 1080p Wayland kiosk (`cage` compositor + `cog` WPE WebKit browser) opens automatically on boot.
- **Host Web Browser**: Point your host browser to [http://127.0.0.1:8766/](http://127.0.0.1:8766/) for host-side HUD inspection and interaction.

---

## 2. 13-Step Live Demo Walkthrough (Live & Video Evaluation)

Step through this exact sequence to demonstrate all core competencies and acceptance criteria:

| Step | Action / Feature | Verification Method | Expected Result |
| :---: | :--- | :--- | :--- |
| **1** | **Cold Boot & Kernel Init** | Watch QEMU console & serial log | Kernel 6.6.21 boots in $\approx 1.15$s. Systemd mounts read-only SquashFS root (`/dev/vda2`) with volatile overlay, and persistent Btrfs data partition (`/dev/vda3` at `/data`). |
| **2** | **Systemd Supervisor & Isolation** | In guest or serial: `systemctl list-units 'lazy-*' --no-pager` | All 15 microservices active under isolated cgroup slices (`lazy-interactive.slice`, `lazy-background.slice`, `lazy-code-sandbox.slice`). |
| **3** | **Live Telemetry Sparklines** | Inspect top-bar HUD gauges | Real-time CPU ($/proc/stat$ delta), RAM ($/proc/meminfo$), Disk ($os.statvfs$), and Network counters. Zero hardcoded values. |
| **4** | **Edge ML Runtime Initialization** | Inspect HUD Planner Badge | Badge displays `Qwen2.5-1.5B-Instruct-Q4_K_M` (Apache-2.0, 1.04 GB) resident in RAM with AVX2 SIMD acceleration. |
| **5** | **Natural Language Command & Streaming** | In HUD prompt: type `"Summarize project deliverables and status"` | Real RFC 6455 WebSocket streaming (`/ws`). Tokens stream progressively into the UI in real time ($\approx 18$–$22$ tok/s, TTFT $< 450$ms). |
| **6** | **Grammar-Constrained Intent Generation** | Check HUD execution drawer or inspect `/run/lazy/llm.sock` | GBNF grammar constrains the LLM output to strictly typed schema-valid Intent JSON. Zero regex or regex fallback mocks. |
| **7** | **Document Writer & Sandboxed I/O** | Command: `"Write a one-page report on edge ML optimization"` | Document app opens. LLM streams text live. Document automatically saved to `/data/Documents/edge_ml.md` via `lazy-broker-fs`. |
| **8** | **File Manager CRUD & Tree Hash** | Browse `/data` in HUD File Explorer | Files created dynamically. Checksum and directory hierarchy updated live. |
| **9** | **Policy Tiering & Approval Drawer** | Execute an L2/L3 action (e.g. modify system setting or staging email) | Execution pauses; UI slides out the Pending Approvals drawer with capability details. User clicks **Approve** to execute. |
| **10** | **Adversarial Security Defense** | Command: `"; rm -rf / ; cat /etc/shadow"` or prompt injection | Request rejected instantly by `lazy-policy` capability gate. 0 breaches across all 120 automated attack tests. |
| **11** | **Transactional Btrfs Undo Rollback** | Click **Undo** button or issue `POST /api/tasks/undo` | System executes Btrfs subvolume rollback. Prior state restored cleanly; rollback receipt emitted. |
| **12** | **Cryptographic Audit Ledger Verification** | Inspect Audit tab in HUD | Hash-chained SHA-256 receipts logged for every transaction. Ledger integrity verified with green shield indicator. |
| **13** | **Clean Poweroff** | Issue `poweroff` or click System -> Shutdown | All services terminate cleanly, journal buffers flush, filesystem unmounts without corruption. |

---

## 3. Mandatory 3–5 Minute MP4 Video Recording Instructions

Per course requirements, a 3–5 minute MP4 screen recording of the running QEMU system must accompany the submission.

### Recording Setup
1. **Tool**: Use OBS Studio, Windows Game Bar (`Win + G`), or native screen recording software.
2. **Resolution**: Record at 1080p (1920x1080) at 30 or 60 fps with audio (if narrating).
3. **Capture Target**: Select the QEMU window (or split screen showing QEMU on the left and host browser `http://127.0.0.1:8766/` on the right).

### Video Script & Timing Breakdown (Target: 4:00 Minutes)
- **0:00 – 0:45 (Cold Boot & Core OS)**:
  - Run `dist\run-windows.ps1` (or `./dist/run-lazy-os.sh`).
  - Highlight cold boot speed ($< 3.5$s total to GUI), custom Linux 6.6.21 kernel, and clean systemd service initialization.
- **0:45 – 1:45 (Edge ML & Token Streaming)**:
  - Point out the Planner Badge: `Qwen2.5-1.5B-Instruct-Q4_K_M` running locally with zero proprietary dependencies.
  - Type a natural-language prompt: `"Write an executive summary of edge OS architecture"`.
  - Show the live token streaming via WebSocket and real-time generation speed.
- **1:45 – 2:45 (Security, Policy Gate & Outbox)**:
  - Trigger an irreversible or privileged action to show the Policy Approval Gate.
  - Show the Outbox holding staged mutations until human authorization.
  - Test an adversarial prompt injection or shell escape and show the immediate policy block.
- **2:45 – 3:30 (Btrfs Undo & Audit Chain)**:
  - Modify or delete a file in `/data`.
  - Trigger the **Undo** action to demonstrate instantaneous Btrfs transactional rollback.
  - Show the Cryptographic Audit Ledger verifying the SHA-256 chain integrity.
- **3:30 – 4:00 (Wrap-up & Metrics)**:
  - Briefly display the telemetry dashboard (sharp 1080p rendering, SVG sparklines).
  - Summarize key specs: 65.87% base OS footprint reduction vs. Debian 12, 0 proprietary components, 100% open-source Apache-2.0 stack.

---

## 4. Final Submission Checklist

Before final submission, verify that the following files are present on the `main` branch:

- [x] **Kernel Config**: `dist/kernel.config` (Custom Linux 6.6.21 minimal config, THP 2MB pages, virtio-gpu).
- [x] **API Contract**: `docs/API_CONTRACT.md` (Complete schema for REST API and WebSocket protocol).
- [x] **Legal SBOM**: `docs/audit/manifest.csv` (Verified 0 proprietary licenses; fully Apache-2.0 / MIT / GPL-2.0).
- [x] **Security Metrics**: `bench/results/safety_metrics.json` and `.md` (120 attacks evaluated, 0 breaches).
- [x] **Debian 12 Comparison**: `bench/results/buildroot_vs_debian12.md` (65.87% size reduction, 85.76% package reduction).
- [x] **Verified Screendumps**: 12 Full-HD PNGs in `docs/audit/screendumps/` covering all acceptance flows.
- [x] **Handoff Guide**: `docs/HUMAN_HANDOFF.md` (This document).
- [x] **Project Completion Signal**: `docs/sync/PROJECT_COMPLETE.json`.
