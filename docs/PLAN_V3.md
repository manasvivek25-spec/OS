# Lazy OS V3 Milestone Plan: Complete the Product

**Branch**: `v3-product`  
**Specification**: `docs/SPEC.md`, `docs/BUILD_PROMPT_V3.md`  
**Acceptance Contract**: `docs/acceptance/ACCEPTANCE.md` (Frozen in `docs/acceptance/FROZEN.sha256`)

---

## Milestone Execution Table

| Milestone | Title & Description | Target Checks | Status | Evidence Path |
| :--- | :--- | :---: | :---: | :--- |
| **V3.0** | **Baseline & Acceptance Freeze**: Merge `v2-command-center` into `main`, branch `v3-product`, write `docs/PLAN_V3.md`, `docs/acceptance/ACCEPTANCE.md`, `scripts/accept.sh`, `docs/acceptance/FROZEN.sha256`, `docs/BLOCKED.md`. | P1–DOC1 baseline | **COMPLETED** | [`docs/acceptance/FROZEN.sha256`](file:///c:/Users/len/OS/docs/acceptance/FROZEN.sha256) |
| **V3.1** | **Buildroot Foundation**: `lazy-br2/` external tree, target defconfig, custom Linux kernel defconfig + fragments, prebuilt/external toolchain, initial QEMU boot over serial, systemd init, read-only root, volatile overlay, persistent Btrfs `/data`, first-boot service, `make dist` skeleton. | O2, O3 (partial), O4 | **COMPLETED** | [`tests/results/acceptance/O2_kernel.txt`](file:///c:/Users/len/OS/tests/results/acceptance/O2_kernel.txt), `dist/bzImage` |
| **V3.2** | **Package Platform Microservices**: Python runtime + deps in rootfs, 15 separate `lazy-*` systemd unit files with dedicated users and sandbox directives (`NoNewPrivileges`, `ProtectSystem=strict`, `PrivateTmp`), `/etc/lazy/` configuration, capability manifests, HUD assets. | O3, S3 | **IN_PROGRESS** | `lazy-br2/package/lazy-os/`, `tests/results/acceptance/O3.log` |
| **V3.3** | **In-Guest Native LLM**: Buildroot package for `llama.cpp`, model provisioning (SmolLM2-360M Q4_K_M GGUF), `lazy-llm` service running in guest, planner integration, time-to-first-token & tokens/sec telemetry inside guest. | FT1 | pending | `tests/results/acceptance/FT1.log` |
| **V3.4** | **In-Guest Graphical Session**: Minimal Wayland compositor / DRM/KMS kiosk (`wpewebkit` / `cog` or lightweight browser kiosk), boot splash, virtio-gpu & virtio-tablet input, boots to full-screen Command Center without host browser; QEMU display monitor screendumps. | P1, P2, P5 | pending | `tests/results/acceptance/P1_screendump.png` |
| **V3.5** | **Command Center Completion**: All 11 views on real guest data, First-Run Wizard persistence, interactive Terminal app (PTY, unprivileged `lazy` user, audited), in-guest Browser app, Help module, UI shutdown/reboot controls. | P2, P4, FT9 | pending | `tests/results/acceptance/P4.log`, `tests/results/acceptance/FT9.log` |
| **V3.6** | **Routines, Dialogue & Niche Feed**: Wake-up sequence, briefing trigger via typed and audio wake phrase, overnight chores with snapshot rollback, niche RSS aggregator with TF-IDF ranking and hallucination check. | P3, FT3, FT7 | pending | `tests/results/acceptance/P3.log`, `tests/results/acceptance/FT7.log` |
| **V3.7** | **Web Broker & Engine Integration**: In-guest WebDriver / HTTP sandbox driver, domain allowlist, form filling/submission with approval, download quarantine. | FT5 | pending | `tests/results/acceptance/FT5.log` |
| **V3.8** | **Comms Broker & Local Mail/Chat**: Offline local mail delivery (Maildir), Outbox delay window, recipient taint tracking, local chat driver. | FT6 | pending | `tests/results/acceptance/FT6.log` |
| **V3.9** | **In-Guest Voice Subsystem**: Vosk restricted-grammar wake detector + STT + open-source TTS, synthetic audio loopback WER evaluation, graceful text fallback. | FT8 | pending | `tests/results/acceptance/FT8.log` |
| **V3.10** | **Hardware Control & Self-Test**: Real kernel interfaces in VM (rfkill, USB, audio) + `VM-UNAVAILABLE` labels with `scripts/hw-selftest.sh` for bare-metal laptop hardware. | FT4 | pending | `scripts/hw-selftest.sh`, `tests/results/acceptance/FT4.log` |
| **V3.11** | **Operating System Hardening**: `systemd-analyze security` scores, signed update bundle verifier rejecting tampered updates, secrets vault isolation, strict L4 refusal. | O5, S1–S4 | pending | `tests/results/acceptance/O5.log`, `tests/results/acceptance/S4.log` |
| **V3.12** | **Rigorous Evaluation & Real Baseline**: Empirical Debian 12 minimal VM benchmark per `bench/METHOD.md` ($\ge 10$ runs, $\mu \pm \sigma$), 100+ attack payload evaluation with 0 breaches, 40-task suite run in guest. | O7, O8, FT2, S1 | pending | `tests/results/acceptance/O8_debian_comparison.csv` |
| **V3.13** | **Product Packaging & Conversion**: `dist/` directory, standalone run scripts (`run-lazy-os.sh`, `run-wsl.sh`, `run-windows.ps1`), multi-format images (`.qcow2`, `.vdi`, `.vmdk`), `USER_GUIDE.md`, `QUICKSTART.md`. | P6, P7 | pending | `dist/`, `dist/USER_GUIDE.md` |
| **V3.14** | **Technical Documentation & Reproducibility**: `README.md`, `ARCHITECTURE.md`, `HARDWARE-CONTROL.md`, `docs/reports/results.md`, task deck inputs 1–8, clean-checkout rebuild audit. | O6, O9, DOC1 | pending | `tests/results/acceptance/O9_reproducibility.log` |
| **V3.15** | **Final Product Acceptance**: Execute `scripts/accept.sh` against `dist/` from clean environment, verify all checks PASS or BLOCKED by human-only items, generate `docs/ACCEPTANCE_REPORT.md`, tag `v3-final`, `make handoff`. | All checks | pending | `docs/ACCEPTANCE_REPORT.md` |
| **V3.16** | **Optional Cloud Yocto Verification**: If $\ge 16$ GB RAM cloud host is provisioned, execute `kas build yocto/kas.yml` and record measured comparison. | O7 | BLOCKED | `docs/BUILD_ENV_PLAN.md` (Human Action Required) |
