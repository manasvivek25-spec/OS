# Lazy OS v2 Comprehensive Demonstration Report

**Evaluation Date**: 2026-11-15T20:47:12Z  
**Branch**: `v2-command-center`  
**Guest Environment**: QEMU x86_64 Virtual Machine (`lazy-os`, Linux `6.8.0-149-generic`)  
**Access URL**: `http://127.0.0.1:8766/`  
**Demonstration Suite**: [`scripts/demo-e2e.py`](file:///c:/Users/len/OS/scripts/demo-e2e.py)  
**Raw Machine Evidence**: [`docs/demo/demo_e2e_results.json`](file:///c:/Users/len/OS/docs/demo/demo_e2e_results.json)  
**UI Screenshots Manifest**: [`docs/demo/screens/manifest.json`](file:///c:/Users/len/OS/docs/demo/screens/manifest.json)  

---

## 1. Executive Summary

All **8 canonical demonstration operations** executed against the live booted virtual machine passed with 100% compliance. Real persistent storage on `/dev/vda3` (Btrfs) was exercised, policy approval pipelines were verified live, live guest telemetry was captured, and the cryptographic audit ledger was confirmed tamper-evident.

| Metric | Target | Measured / Result | Evaluation |
| :--- | :--- | :--- | :--- |
| **Canonical Operations Passed** | 8 / 8 | **8 / 8 (100%)** | **PASS** |
| **Command Center Modules Verified** | 8 | **8 (Screenshots & Hashes)** | **PASS** |
| **Storage Persistence** | Btrfs on block device | **`/dev/vda3` on `/data` (Btrfs)** | **VERIFIED** |
| **Policy Invariants (L0–L4)** | Auto L1, Confirm L2 | **L1 Auto-approved, L2 Prompted & Denied** | **VERIFIED** |
| **Cryptographic Audit Ledger** | SHA-256 Hash Chained | **`valid=True`, Tamper Flagged** | **VERIFIED** |
| **Accessibility Compliance** | WCAG AAA | **15.68:1 contrast, focus ring, reduced motion** | **PASS** |

---

## 2. Step-by-Step Demonstration Audit Table

| Step | Operation Description | Expected Behavior | Live Measured Outcome | Result | Evidence Path |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **1** | **Identity & Subsystem Badges** | Guest returns real mounts, hostname `lazy-os`, and honest subsystem statuses. | `hostname="lazy-os"`, `btrfs` on `/data`, kernel real, storage real, LLM simulated. | **PASS** | `docs/demo/demo_e2e_results.json#step1` |
| **2** | **L1 Note Creation** | Natural directive creates `plan.md` via auto-approved L1 policy evaluation. | HTTP 200, `plan.md` created (159 bytes), verified in guest `/data`. | **PASS** | `docs/demo/demo_e2e_results.json#step2` |
| **3** | **L2 Deletion Approved** | Deletion triggers L2 approval prompt; upon approval, target file is deleted. | HTTP 202 Accepted, approval `app-...` created, approved via API, file 404. | **PASS** | `docs/demo/demo_e2e_results.json#step3` |
| **4** | **L2 Deletion Denied** | Deletion triggers L2 approval prompt; upon rejection, file remains intact. | HTTP 202 Accepted, denied via API, target file `/data/safe_doc.txt` unmodified. | **PASS** | `docs/demo/demo_e2e_results.json#step4` |
| **5** | **Agent Center Activity** | Service registry reports all core services; capabilities loaded. | 15 services tracked in `/lazy-interactive.slice`, 37 capabilities loaded. | **PASS** | `docs/demo/demo_e2e_results.json#step5` |
| **6** | **System Monitor Telemetry** | Guest exposes real CPU, memory, disk, and network metrics. | CPU 4.2%, RAM 234.7 MB / 961 MB (24.4%), Disk 5.8 MB / 128 MB. | **PASS** | `docs/demo/demo_e2e_results.json#step6` |
| **7** | **Audit Chain & Tamper Test** | Ledger validates from genesis; injected bitflip is detected. | Ledger verified `valid=True` (10 entries); tampered block detected (`tamper=True`). | **PASS** | `docs/demo/demo_e2e_results.json#step7` |
| **8** | **Task Undo / Rollback** | Temporary directory mutation is rolled back to exact initial tree state. | Tree hash before mutation matches tree hash after undo (`restored=True`). | **PASS** | `docs/demo/demo_e2e_results.json#step8` |

---

## 3. Command Center UI Screenshots Audit (Milestone V2.C5)

High-resolution $1440 \times 900$ screenshots were captured directly from the running guest over forwarded port 8766 using headless Chromium:

| Module | Image File | Filesize | SHA-256 Checksum | Verification Source |
| :--- | :--- | :--- | :--- | :--- |
| **1. Home & Briefing** | [`01_home.png`](file:///c:/Users/len/OS/docs/demo/screens/01_home.png) | 76.4 KB | `ff93ee63a7e945285bbec0f89e4bcb9d5470c86fa2f23a8347fb692de5d9502c` | Forwarded Port 8766 |
| **2. AI Command Center** | [`02_ai_command.png`](file:///c:/Users/len/OS/docs/demo/screens/02_ai_command.png) | 48.2 KB | `5876420e8dc9faa2e532756b60511dfd3c8921b9f8ecc7f469fdb2dd05f82846` | Forwarded Port 8766 |
| **3. System Monitor** | [`03_system_monitor.png`](file:///c:/Users/len/OS/docs/demo/screens/03_system_monitor.png) | 113.3 KB | `c8636c56235c777b744d2d7c58ad06a12ee7a27ebf107386d5d59043e06ef5a3` | Forwarded Port 8766 |
| **4. Agent Center** | [`04_agent_center.png`](file:///c:/Users/len/OS/docs/demo/screens/04_agent_center.png) | 73.4 KB | `71b53866d3c2fc7b7ba1b7e4113ef0d565782782e37943aa5c555512271dfad9` | Forwarded Port 8766 |
| **5. File Manager** | [`05_file_manager.png`](file:///c:/Users/len/OS/docs/demo/screens/05_file_manager.png) | 46.5 KB | `df62dd92b9e51f1519b59e51147e85c2c9d19a2e6f477e382d622f6fa731efc7` | Forwarded Port 8766 |
| **6. Security Center** | [`06_security_center.png`](file:///c:/Users/len/OS/docs/demo/screens/06_security_center.png) | 53.0 KB | `5df45378a08ef3a8e747a827051b73e8774fbe5e4bf7e9b0aa35fecb438cf15c` | Forwarded Port 8766 |
| **7. App Launcher** | [`07_app_launcher.png`](file:///c:/Users/len/OS/docs/demo/screens/07_app_launcher.png) | 60.2 KB | `bb9a5c9d8f9b1c35639d67bc584346859e97f5b7e9a8fec93e77fbc784f1a6f8` | Forwarded Port 8766 |
| **8. Settings** | [`08_settings.png`](file:///c:/Users/len/OS/docs/demo/screens/08_settings.png) | 63.9 KB | `5ae1953e0bf95dd593d6e191ae88ce1aa0bf22d711019183404fb8ae88b75fc4` | Forwarded Port 8766 |

---

## 4. Truth Ledger: Table of Simulated & Absent Subsystems (Rule T1/T4)

In compliance with Rule T1 and Truth Rules T1–T9, this table unflinchingly records every subsystem that is simulated, heuristic, or unverified:

| Subsystem | Classification | Status & Explanation | Mitigation / Plan |
| :--- | :---: | :--- | :--- |
| **Kernel Source** | **Real** | Boots host Ubuntu generic kernel (`vmlinuz-6.8.0-149-generic`) with custom initramfs and in-tree Btrfs modules. Not compiled via BitBake. | Feasibility and build env plan detailed in `docs/BUILD_ENV_PLAN.md`. |
| **Storage Subsystem** | **Real** | Persistent Btrfs partition on raw GPT disk (`/dev/vda3` on `/data`). Survives reboot; supports copy-on-write snapshots. | Production-grade. |
| **Audit Ledger** | **Real** | SHA-256 hash-chained append-only record ledger with complete tamper verification. | Production-grade. |
| **Local LLM Engine** | **Simulated** | Heuristic intent matcher with slot extraction (`lazy.planner.rule_based`). Host bridge provided (`lazy.gateway.host_bridge`). | Marked `SIMULATED` on UI and `/api/build-info`. |
| **Voice Interface** | **Simulated** | Uses browser Web Speech API when available; otherwise mock audio waveform. | Labelled `browser speech, not in image`. |
| **Yocto Image Build** | **Unverified** | Yocto layer metadata (`meta-lazy`, recipes, kas config) exists in repo, but full native BitBake image build has not completed on this WSL host due to RAM/CPU constraints. | Human action runbook provided in `docs/BUILD_ENV_PLAN.md`. |
| **Web Browser Automation** | **Real** | Pure Python DOM engine with URL filtering and domain-based quarantine sandbox. | Operational. |
| **Comms Broker** | **Real** | Local Maildir format driver and local chat session driver. | Operational. |
