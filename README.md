# Lazy OS

Lazy OS is a custom, bootable, application-specific Linux distribution (Yocto Project, Track A) built for university Operating Systems evaluation. It provides an autonomous, interactive assistant runtime where user vision and supervision drive audited, sandboxed, and reversible operating system actions.

## Quick Start (Under 10 Commands)

```bash
# 1. Check host environment and create docs/ENV.md
./scripts/check-env.sh

# 2. Setup python dependencies and virtualenv
make setup

# 3. Check milestone progress
make status

# 4. Run core verification suite (unit + integration + security tests)
make verify

# 5. Run end-to-end task evaluation suite
make eval-tasks

# 6. Run live interactive demo
make demo

# 7. Build Yocto Base image (minimal headless footprint)
make image-base

# 8. Build Yocto Full image (model, HUD, voice, browser)
make image-full

# 9. Verify generated image in QEMU over SSH
make verify-image
```

## System Architecture

Lazy OS enforces strict privilege separation:
- **No Free-Form Shell (Rule F2)**: Agent acts solely through strictly typed capabilities.
- **Planner Isolation (Rule F1, F4)**: Unprivileged planner proposes; policy engine decides; brokers execute. Planner never sees credentials or touches raw networks.
- **Untrusted Input Is Data (Rule F3)**: Feeds, web text, and emails are processed through isolated readers and tagged as data, preventing prompt injections.
- **Audit & Undo (Rule F5, F7)**: Checkpointed tasks backed by Btrfs snapshots and an append-only hash-chained receipt ledger.
- **Outbox Barrier (Rule F8)**: Irreversible external communications require explicit user verification, taint clearance, and undo windows.

## Documentation
- [docs/SPEC.md](docs/SPEC.md): Complete product requirements and frozen architecture.
- [docs/PLAN.md](docs/PLAN.md): Milestone progress and exit test verification matrix.
- [docs/STATE.md](docs/STATE.md): Session state and immediate next action.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): Deep-dive system design.
- [docs/HARDWARE-CONTROL.md](docs/HARDWARE-CONTROL.md): Hardware sysfs abstractions.
