# Lazy OS (V2 Command Center)

Lazy OS is an application-specific operating system prototype and autonomous assistant runtime built for university Operating Systems evaluation. It provides a supervised execution environment where user directives and vision drive audited, sandboxed, and reversible operating system capabilities through a browser-based Command Center.

> [!NOTE]
> **Build Provenance & Subsystem Status (Audit V2.A1–V2.B3)**:
> - **Booted OS Profile:** Linux 6.8 host kernel paired with a custom-assembled Busybox userspace initramfs (25.3 MB) and GPT partitioned virtual disk with persistent Btrfs storage on `/dev/vda3`.
> - **Yocto Metadata:** Recipes, layer configurations (`meta-lazy`), and kas specifications (`yocto/kas/`) are authored and validated, with native BitBake compilation planned as host resources permit (see `docs/BUILD_ENV_PLAN.md`).
> - **In-Guest Intelligence:** Heuristic Mock Planner resident in guest; optional Host LLM bridge (`SmolLM2-360M`) supported.
> - **Audit & Undo:** 100% Verified in-guest SHA-256 cryptographic hash-chained audit ledger and persistent snapshot rollback.

---

## Quick Start (Under 10 Commands)

```bash
# 1. Inspect environment and resources
cat /proc/meminfo; df -h /

# 2. Setup Python environment
make setup

# 3. View milestone status table
cat docs/PLAN_V2.md

# 4. Run master verification suite (401 unit, attack, and API tests)
PYTHONPATH=src .venv/bin/pytest tests/

# 5. Build bootable V2 artifacts (initramfs + Btrfs disk)
python3 scripts/build_image_v2.py

# 6. Launch Lazy OS in QEMU (hardware accelerated)
./scripts/run-lazy.sh

# 7. Open Lazy OS Command Center in your browser
# URL: http://127.0.0.1:8766/

# 8. Run end-to-end automated demonstration
python3 scripts/demo-e2e.py

# 9. Stop Lazy OS virtual machine
./scripts/stop-lazy.sh
```

---

## Subsystem Truth & Verification Matrix

Every subsystem is labelled honestly per Rule T1 (see [`docs/audit/CLAIMS.md`](docs/audit/CLAIMS.md)):

| Subsystem | Status | Implementation Details |
| :--- | :---: | :--- |
| **Storage (`/data`)** | **Verified Real** | Persistent Btrfs filesystem on `/dev/vda3` (survives reboot; subvolume/directory rollback verified) |
| **Audit Ledger** | **Verified Real** | Cryptographic SHA-256 hash-chained ledger (`lazy.audit`), bitflip & truncation tamper detection |
| **Snapshot Rollback** | **Verified Real** | Instant undo via `lazy.tasks`, verified with deterministic tree hashing before/after tasks |
| **Capability Mediation**| **Verified Real** | 37 capability manifests; L0–L4 tier enforcement; taint propagation tracking (`lazy.policy`) |
| **Command Center HUD** | **Verified Real** | Desktop-like SPA in `hud/` served by guest gateway (Identity, Metrics, Tasks, Files, Security) |
| **Identity API** | **Verified Real** | `GET /api/identity` and `GET /api/build-info` verified via in-guest curl proof |
| **Security Attack Suite**| **Verified Real**| 70 prompt injections and 50 benign queries evaluated; 0 breaches |
| **Local LLM Engine** | **Simulated** | Heuristic rule-based planner in guest; optional host LLM bridge |
| **Voice Interface** | **Simulated** | Web Speech API fallback in browser (labelled 'browser speech, not in image') |
| **Kernel & Yocto Build**| **Dev Root / Unverified Yocto** | Booted image uses host Linux 6.8 kernel with custom initramfs; BitBake build pending |

---

## Architectural Pillars (Rules F1–F9)
- **No Free-Form Shell (Rule F2)**: Agent acts exclusively through 37 typed capability manifests.
- **Unprivileged Neural Planner (Rule F1, F4)**: Planner decomposes intent; policy engine decides; brokers execute. Planner never sees credentials or raw sockets.
- **Untrusted Input Is Data (Rule F3)**: Web pages, emails, and feeds are tagged as quoted data, neutralizing prompt injections.
- **Cryptographic Audit & Instant Undo (Rule F5, F7)**: Persistent Btrfs storage enables instant rollbacks backed by a SHA-256 hash-chained ledger.
- **Outbox Delay Barrier (Rule F8)**: External communication routes through a staged queue with a countdown undo window.
- **Isolated Browser Sandbox (Rule F9)**: Headless browser driver operates with quarantined downloads.
