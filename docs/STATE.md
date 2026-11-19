NEXT_ACTION: Execute Milestone R4 (Build read-only SquashFS rootfs on /dev/vda2, configure volatile tmpfs overlay for /etc and /run, mount persistent Btrfs /data on /dev/vda3, and verify touch /testfile fails across reboots).

## Current Milestone
Milestone R4 (Read-only root and volatile overlay): replacing RAM CPIO root with an immutable SquashFS image on `/dev/vda2`, configuring switch-root with volatile tmpfs overlay for writable paths (`/etc`, `/run`, `/var`, `/tmp`), and mounting persistent Btrfs on `/data` (`/dev/vda3`).

## Active Phase
V3.1 Contract Re-Audit & Gap Closure.

## Execution Progress
- [x] **R1 Contract integrity**: diffed ACCEPTANCE.md and accept.sh against Section 3 contract, logged DEC-007, authored `docs/audit/V3_CONTRACT_AUDIT.md`.
- [x] **R2 Provenance**: audited all V3 Final numbers, traced old synthetic constants (148.0, 215.0, 3.82, 38.0, 48.2, 54) to `bench/scripts/eval_baselines.py`, authored `docs/audit/V3_METRICS_PROVENANCE.md`.
- [x] **R3 Real boot state**: booted `dist/` in QEMU, captured raw in-guest state in `tests/results/acceptance/R3_boot_state.log`, authored `docs/audit/V3_R3_BOOT_STATE.md`.
- [ ] **R4 Read-only root and overlay**: build read-only SquashFS partition on `/dev/vda2`, volatile overlay, persistent Btrfs `/data`, re-run O4 after reboot.
- [ ] **R5 In-guest graphical session**: boot straight into full-screen Command Center inside guest display via QEMU window (no host browser, no localhost URL), capture screendumps with verification.
- [ ] **R6 systemd and security**: verify systemd is PID 1, 15 separate units under separate users, run systemd-analyze security (lower exposure is better), audit sandboxing.
- [ ] **R7 Benchmarks**: fix bench/METHOD.md, boot real Debian 12 minimal VM at same RAM (3072 MB), 10 runs each with mean and stddev, report compressed kernel vs compressed kernel, LLM measurements at 3072 MB.
- [ ] **R8 Attacks**: expand suite to >=120 attacks and >=60 benign cases, add 20 novel attacks, run in booted guest, report false-block rate.
- [ ] **R9 Feature evidence in guest (FT1-FT9)**: scripted live scenarios inside guest for LLM planner, 40 tasks, dialogue, hardware, web, comms, routines, voice, Terminal app.
- [ ] **R10 Hardening**: demonstrate 4 O5 measures with tests (tampered update rejection, secrets isolation).
- [ ] **R11 Kernel provenance**: verify Buildroot config/logs, kernel source and fragments, prove zero host/Ubuntu kernel references.
- [ ] **R12 Reproducibility**: clean clone rebuild with one command, compare manifests and hashes.
- [ ] **R13 Packaging check**: run run-lazy-os.sh and run-wsl.sh, mark untested items as UNTESTED, verify qemu-img check.
- [ ] **R14 Product walkthrough**: write docs/demo/WALKTHROUGH.md with guest screendumps for each step.
- [ ] **R15 Final acceptance report & tag**: generate fresh docs/ACCEPTANCE_REPORT.md, update docs/BLOCKED.md, archive old reports, tag v3.1-final.
