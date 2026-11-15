# Lazy OS

Lazy OS is a custom, bootable, application-specific Linux distribution (Yocto Project, Track A) built for university Operating Systems evaluation. It provides an autonomous, interactive assistant runtime where user vision and supervision drive audited, sandboxed, and reversible operating system actions.

---

## Quick Start (Under 10 Commands)

```bash
# 1. Verify host environment and dependencies
./scripts/check-env.sh

# 2. Setup Python virtual environment and modules
make setup

# 3. View milestone status table
make status

# 4. Run master verification suite (186 unit, integration, and security tests)
make verify

# 5. Run end-to-end evaluation benchmark on 40-task suite
make eval-tasks

# 6. Launch interactive local demo with Cyberpunk HUD
make demo

# 7. Build minimal headless Base OS image (38 MB footprint)
./build.sh base

# 8. Build full Assistant OS image with resident neural stack (285 MB)
./build.sh full

# 9. Verify generated image inside QEMU over SSH
make verify-image
```

---

## Key Achievements & Track A Benchmarks

| Metric | Stock Debian 12 Minimal | Lazy OS Base | Track A Requirement | Measured Improvement |
|---|---|---|---|---|
| **Compressed Rootfs** | 148.0 MB | **38.0 MB** | $\ge 40.0\%$ | **-74.3% (EXCEEDED)** |
| **Idle RAM Footprint** | 215.0 MB | **74.0 MB** | $\ge 40.0\%$ | **-65.6% (EXCEEDED)** |
| **Cold Boot Time (to HUD)** | 3.82 s | **0.94 s** | $\ge 40.0\%$ | **-75.4% (EXCEEDED)** |
| **Installed Package Count** | 224 packages | **54 packages** | $\ge 40.0\%$ | **-75.9% (EXCEEDED)** |
| **Kernel vmlinux Image** | 48.2 MB | **19.6 MB** | — | **-59.3% (OPTIMIZED)** |
| **Adversarial Safety Rate** | 57.14% breaches | **0.00% breaches** | 0 breaches | **100% BLOCKED (0/70)** |

---

## Architectural Pillars (Frozen Rules F1–F9)
- **No Free-Form Shell (Rule F2)**: Agent acts exclusively through 37 typed capability manifests.
- **Unprivileged Neural Planner (Rule F1, F4)**: Unprivileged `lazy-planner` generates plans; policy engine decides; brokers execute. Planner never sees credentials or raw sockets.
- **Untrusted Input Is Data (Rule F3)**: Web pages, emails, and feeds are tagged as quoted data, neutralizing prompt injections.
- **Cryptographic Audit & Instant Undo (Rule F5, F7)**: Zero-copy Btrfs subvolume snapshots enable sub-millisecond rollbacks backed by a SHA-256 hash-chained ledger.
- **Outbox Delay Barrier (Rule F8)**: External communication routes through a staged queue with a countdown undo window.
- **Isolated Browser Sandbox (Rule F9)**: Headless browser driver operates in an isolated namespace with quarantined downloads.

---

## Documentation Index
- [docs/SPEC.md](file:///c:/Users/len/OS/docs/SPEC.md): Complete product requirements and frozen architecture.
- [docs/PLAN.md](file:///c:/Users/len/OS/docs/PLAN.md): Milestone progress and exit test verification matrix.
- [docs/STATE.md](file:///c:/Users/len/OS/docs/STATE.md): Current active session state and next action.
- [docs/ARCHITECTURE.md](file:///c:/Users/len/OS/docs/ARCHITECTURE.md): Deep-dive system design and Mermaid diagrams.
- [docs/HARDWARE-CONTROL.md](file:///c:/Users/len/OS/docs/HARDWARE-CONTROL.md): Hardware sysfs abstractions and drivers.
- [docs/PACKAGES.md](file:///c:/Users/len/OS/docs/PACKAGES.md): Package manifest and size reduction rationale.
- [docs/LICENCES.md](file:///c:/Users/len/OS/docs/LICENCES.md): 100% open-source software license audit.
- [docs/reports/results.md](file:///c:/Users/len/OS/docs/reports/results.md): Master empirical benchmark results report.
- [docs/demo/RUNSHEET.md](file:///c:/Users/len/OS/docs/demo/RUNSHEET.md): Live demo runsheet and fallback video script.
- [docs/deck-inputs/](file:///c:/Users/len/OS/docs/deck-inputs/): Slide deck inputs for assignment tasks 1 through 8.

---

## License
Open source under the [MIT License](file:///c:/Users/len/OS/LICENSE).
