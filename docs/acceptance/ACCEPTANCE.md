# Lazy OS V3 Acceptance Contract

**Contract Status**: FROZEN  
**Contract Version**: 3.0.0  
**Specification Reference**: `docs/SPEC.md`, `docs/BUILD_PROMPT_V3.md` Section 3

This document defines the formal acceptance contract for Lazy OS v3. No check may be deleted, weakened, or re-labeled. A check passes only when `scripts/accept.sh`, run against the running booted OS image, executes the test and saves raw machine-readable evidence under `tests/results/acceptance/`.

---

## 1. Product Checks (P1 – P7)

### P1: In-Guest Full-Screen Graphical Kiosk Boot
- **ID**: `P1`
- **Pass Criterion**: One command (`./dist/run-lazy-os.sh`) launches QEMU with a display window and boots into a full-screen graphical session (Wayland/DRM with WebKit/browser kiosk) showing the Lazy OS Command Center from the in-guest gateway (`127.0.0.1:8765`). Screendump from QEMU display monitor (`screendump /tmp/guest_p1.ppm`) captures the rendered UI showing the guest hostname and boot identity without using any host browser.
- **Method**: Run `./dist/run-lazy-os.sh` (or `scripts/run-lazy.sh`), connect to QEMU monitor socket, execute `screendump`, convert to PNG, verify non-blank graphical Command Center screen.
- **Evidence Path**: `tests/results/acceptance/P1_screendump.png`, `tests/results/acceptance/P1.log`

### P2: Boot Splash & First-Run Wizard Persistence
- **ID**: `P2`
- **Pass Criterion**: Boot splash is displayed during startup. On first boot, the First-Run Wizard prompts for username, custom wake phrase, UI accent color, and capability approval defaults. Submitted preferences are saved to `/data/system/settings.json` and persist across hypervisor cold reboots.
- **Method**: Submit wizard configuration via API/UI, cold-reboot guest, retrieve `/api/settings` and `/data/system/settings.json` to verify matching values.
- **Evidence Path**: `tests/results/acceptance/P2_persistence.json`, `tests/results/acceptance/P2.log`

### P3: Wake Phrase Briefing Trigger
- **ID**: `P3`
- **Pass Criterion**: Triggering the wake phrase (both via text input `hey lazy` and synthetic audio speech input) initiates the system wake-up sequence, producing a daily briefing in the Command Center UI and speaking the summary via in-guest TTS.
- **Method**: Send wake directive via gateway socket and audio pipeline; assert transition to briefing state and audio generation.
- **Evidence Path**: `tests/results/acceptance/P3_briefing.json`, `tests/results/acceptance/P3.log`

### P4: Command Center Modules Real Guest Data
- **ID**: `P4`
- **Pass Criterion**: All 11 Command Center views (Home, AI Command Center, System Monitor, Agent Center, File Manager, Security Center, App Launcher, Settings, Terminal, Browser, Help) load and render live data queried directly from the guest gateway/brokers. Zero hardcoded mock numbers.
- **Method**: Headless DOM verification querying each view's data bindings against real `/api/*` endpoints.
- **Evidence Path**: `tests/results/acceptance/P4_modules.json`, `tests/results/acceptance/P4.log`

### P5: Clean Shutdown and State Persistence
- **ID**: `P5`
- **Pass Criterion**: Invoking shutdown/reboot from the UI triggers an orderly systemd shutdown (`systemctl poweroff` / `systemctl reboot`) without filesystem corruption, and all user files in `/data` remain intact upon subsequent boot.
- **Method**: Issue reboot command through broker, verify clean unmount in serial console log, verify `/data` Btrfs state after restart.
- **Evidence Path**: `tests/results/acceptance/P5_shutdown.log`

### P6: Offline Self-Sufficiency & Network Fetch
- **ID**: `P6`
- **Pass Criterion**: With network disconnected (`-net none`), all core OS modules, planner, and Command Center function completely without error. With network enabled, `lazy-fetcher` fetches RSS feeds and navigates allowlisted public web pages.
- **Method**: Boot with and without network device; test offline prompt execution and online fetch capability.
- **Evidence Path**: `tests/results/acceptance/P6_network.log`

### P7: Distribution Packaging & Standalone Run Scripts
- **ID**: `P7`
- **Pass Criterion**: `dist/` directory contains complete bootable disk image, run scripts for Linux (`dist/run-lazy-os.sh`), WSL (`dist/run-wsl.sh`), and Windows PowerShell (`dist/run-windows.ps1`), converted VM images (`lazy-os.qcow2`, `lazy-os.vdi`, `lazy-os.vmdk`), `USER_GUIDE.md`, and one-page `QUICKSTART.md`.
- **Method**: Inspect `dist/` manifest and verify file existence and image conversion signatures (`qemu-img info`).
- **Evidence Path**: `tests/results/acceptance/P7_dist_manifest.json`, `tests/results/acceptance/P7.log`

---

## 2. Operating System Checks (O1 – O9)

### O1: Fully Scripted Build from Clean Checkout
- **ID**: `O1`
- **Pass Criterion**: Executing `make dist` (or `build.sh`) from a clean checkout builds the kernel, rootfs, and disk images using scripts only, outputting complete build logs to `build-logs/`.
- **Method**: Execute build script, verify non-zero artifacts in `dist/` and non-empty `build-logs/build.log`.
- **Evidence Path**: `tests/results/acceptance/O1_build.log`

### O2: Custom Booted Kernel Build
- **ID**: `O2`
- **Pass Criterion**: The booted kernel is our own custom build: `uname -r` and `/proc/version` reflect Lazy OS custom kernel tag, defconfig and fragments are in `lazy-br2/board/lazy/linux/`, zero Ubuntu generic kernels used in final dist image, and before/after size/boot table exists comparing against stock defconfig.
- **Method**: Execute `uname -a` and `cat /proc/version` inside guest; verify configuration paths.
- **Evidence Path**: `tests/results/acceptance/O2_kernel.txt`, `tests/results/acceptance/O2.log`

### O3: Microservices Sandboxing under Systemd
- **ID**: `O3`
- **Pass Criterion**: Systemd boots at least 15 separate `lazy-*` services under dedicated unprivileged system users (`lazy-gateway`, `lazy-planner`, `lazy-policy`, etc.) in dependency order. `systemd-analyze security` scores are recorded for all units.
- **Method**: Run `systemctl list-units 'lazy-*'` and `systemd-analyze security lazy-*` in guest.
- **Evidence Path**: `tests/results/acceptance/O3_services.json`, `tests/results/acceptance/O3_security_scores.txt`

### O4: Filesystem Architecture (Read-Only Root, Volatile Overlay, Persistent Btrfs /data)
- **ID**: `O4`
- **Pass Criterion**: `/` is mounted read-only (direct write `touch /test` fails with `Read-only file system`), `/etc` has a volatile writable overlay (changes discarded on reboot unless explicitly persisted), and `/data` is a persistent Btrfs filesystem on its own partition whose data survives reboots.
- **Method**: Run mount checks, write test to `/`, write test to `/data`, reboot, verify persistence.
- **Evidence Path**: `tests/results/acceptance/O4_storage.log`

### O5: Operating System Hardening Invariants
- **ID**: `O5`
- **Pass Criterion**: At least 3 hardening measures verified with automated exploit tests: (1) read-only root enforcement, (2) systemd sandboxing with seccomp and `NoNewPrivileges=yes`, (3) secrets vault user isolation (`/run/lazy/secrets` restricted to `lazy-secrets`), (4) signed update bundle verification rejecting tampered payloads.
- **Method**: Execute hardening attack suite against booted guest.
- **Evidence Path**: `tests/results/acceptance/O5_hardening.log`

### O6: Package Manifest, Licenses & SBOM
- **ID**: `O6`
- **Pass Criterion**: Automated generation of complete package manifest, open-source license list, and SPDX/JSON Software Bill of Materials (SBOM) from build output. Any proprietary items listed and justified in `docs/LICENCES.md`.
- **Method**: Validate generated SBOM and license compliance summary.
- **Evidence Path**: `tests/results/acceptance/O6_sbom.json`, `tests/results/acceptance/O6_licenses.txt`

### O7: Build-System Comparison Matrix
- **ID**: `O7`
- **Pass Criterion**: Detailed comparison matrix comparing Buildroot build metrics (time, size, RAM, toolchain) with Yocto metadata validation or build results, with explicit hardware resource audit.
- **Method**: Verify `docs/reports/build_systems.md` contains empirical data and validated manifests.
- **Evidence Path**: `tests/results/acceptance/O7_build_systems.md`

### O8: Empirical Debian 12 Baseline Comparison
- **ID**: `O8`
- **Pass Criterion**: Like-for-like comparison measured per `bench/METHOD.md` against a real Debian 12 minimal VM: total bootable payload size, rootfs size, idle RAM (both `used` and `MemTotal - MemAvailable`), cold-boot time across $\ge 10$ runs ($\mu \pm \sigma$), package count.
- **Method**: Run `bench/scripts/eval_debian_comparison.py` against both live VMs; generate CSV and summary table.
- **Evidence Path**: `tests/results/acceptance/O8_debian_comparison.csv`, `tests/results/acceptance/O8_summary.md`

### O9: Clean Checkout Rebuild & Reproducibility Audit
- **ID**: `O9`
- **Pass Criterion**: A secondary build from a fresh clean checkout reproduces identical manifests and validates image determinism. Differences are audited and documented.
- **Method**: Compare package manifests and file checksums across successive builds.
- **Evidence Path**: `tests/results/acceptance/O9_reproducibility.log`

---

## 3. Feature Checks (FT1 – FT9)

### FT1: In-Guest LLM Execution & Grammar-Constrained Decoding
- **ID**: `FT1`
- **Pass Criterion**: Local LLM (`llama.cpp` with quantized model $\le 1$B parameters) runs inside the guest and drives `lazy-planner`. Validates $\ge 90\%$ JSON-schema compliance on `tests/assistant/benign.jsonl`, 0% prompt injection escapes on attack set via grammar constraints, and measures time-to-first-token (TTFT) and tokens/sec in guest.
- **Method**: Run in-guest LLM benchmark script, record inference telemetry and safety scores.
- **Evidence Path**: `tests/results/acceptance/FT1_llm_metrics.json`, `tests/results/acceptance/FT1.log`

### FT2: 40-Task Canonical Suite Execution
- **ID**: `FT2`
- **Pass Criterion**: Canonical 40-task workload suite (`tests/tasks/*.yaml`) passes with 100% success rate under mock planner and $\ge 90\%$ under in-guest LLM planner inside the guest.
- **Method**: Execute task runner in guest for all 40 YAML tasks.
- **Evidence Path**: `tests/results/acceptance/FT2_tasks_results.json`, `tests/results/acceptance/FT2.log`

### FT3: Interactive Dialogue Management
- **ID**: `FT3`
- **Pass Criterion**: Dialogue manager handles clarifying questions, plan preview, pause, stop, redirect, and undo. Correction rules (`config/corrections.yaml`) accurately remap user misunderstandings.
- **Method**: Test dialogue manager state machine transitions through gateway socket.
- **Evidence Path**: `tests/results/acceptance/FT3_dialogue.json`, `tests/results/acceptance/FT3.log`

### FT4: Real Hardware Control & VM Self-Test
- **ID**: `FT4`
- **Pass Criterion**: Every hardware capability (`hw.*`) executes against real kernel interfaces in VM (rfkill via `mac80211_hwsim`, USB via QEMU xHCI, audio via ALSA). Interfaces unavailable in VM (backlight, battery, physical CPU governor) are labeled `VM-UNAVAILABLE` with fake-sysfs fallback and verified via `scripts/hw-selftest.sh` for physical hardware.
- **Method**: Run hardware capability suite in guest; run `scripts/hw-selftest.sh` syntax and mock check.
- **Evidence Path**: `tests/results/acceptance/FT4_hw_report.json`, `tests/results/acceptance/FT4.log`

### FT5: Sandboxed Web Broker & Browsing
- **ID**: `FT5`
- **Pass Criterion**: Sandboxed web broker performs domain-allowlisted navigation, DOM extraction, form fill/submit with user approval, and download quarantine on local test site and static public site.
- **Method**: Execute web broker automated scenario in guest against test HTTP server.
- **Evidence Path**: `tests/results/acceptance/FT5_web.json`, `tests/results/acceptance/FT5.log`

### FT6: Comms Broker, Local Mail & Chat
- **ID**: `FT6`
- **Pass Criterion**: Local mail delivery (draft, preview, outbox approval, send/receive between local users) works offline in guest. Comms broker enforces recipient taint tracking and undo window.
- **Method**: Deliver test emails, verify Maildir storage, inspect outbox hold and approval queue.
- **Evidence Path**: `tests/results/acceptance/FT6_comms.json`, `tests/results/acceptance/FT6.log`

### FT7: Routines, Wake-Up Briefing & Niche Feed
- **ID**: `FT7`
- **Pass Criterion**: Wake-up briefing, overnight maintenance chores with snapshot undo, and niche RSS feed aggregator with TF-IDF topic ranking, feedback learning, and hallucination/faithfulness checker execute successfully.
- **Method**: Trigger routines runner in guest; evaluate chore snapshot creation, execution, and feed scoring.
- **Evidence Path**: `tests/results/acceptance/FT7_routines.json`, `tests/results/acceptance/FT7.log`

### FT8: In-Guest Voice Pipeline
- **ID**: `FT8`
- **Pass Criterion**: In-guest voice engine (Vosk restricted-grammar wake detector + STT + open-source TTS) executes in guest. Word Error Rate (WER) measured on synthetic loopback audio; text fallback operates seamlessly when audio device is unattached.
- **Method**: Feed synthetic WAV audio into in-guest voice daemon; measure transcription accuracy and TTS latency.
- **Evidence Path**: `tests/results/acceptance/FT8_voice.json`, `tests/results/acceptance/FT8.log`

### FT9: In-Guest Terminal Application
- **ID**: `FT9`
- **Pass Criterion**: Command Center provides an interactive Terminal application running a real PTY under unprivileged `lazy` user. Terminal activity is logged to audit trail. Agent is strictly prohibited from spawning free-form shells (Rule F2).
- **Method**: Connect to Terminal PTY endpoint, run shell commands as `lazy`, assert audit logging and agent isolation.
- **Evidence Path**: `tests/results/acceptance/FT9_terminal.log`

---

## 4. Safety Checks (S1 – S4)

### S1: Comprehensive Adversarial Attack Suite
- **ID**: `S1`
- **Pass Criterion**: Evaluation of $\ge 100$ adversarial attack payloads (injections, malicious feeds, tainted emails, capability privilege escalation, L4 attempts) against live guest policy engine with **0 breaches**. False-positive rejection rate on $\ge 50$ benign queries is $\le 2\%$. Unguarded test baseline verified absent from `dist/`.
- **Method**: Run `tests/attacks/run_attack_eval.py` against guest gateway; generate safety metrics CSV.
- **Evidence Path**: `tests/results/acceptance/S1_attack_metrics.csv`, `tests/results/acceptance/S1.log`

### S2: Cryptographic Audit Hash Chain & Tamper Detection
- **ID**: `S2`
- **Pass Criterion**: Audit ledger records every state mutation with SHA-256 hash chaining. Live in-guest verifier passes on untampered log, and immediately detects corruption upon synthetic byte modification, deletion, reordering, or truncation.
- **Method**: Run in-guest audit tamper test against `/data/audit/audit.log`.
- **Evidence Path**: `tests/results/acceptance/S2_audit_tamper.json`, `tests/results/acceptance/S2.log`

### S3: Strict Privilege Separation & Secrets Isolation
- **ID**: `S3`
- **Pass Criterion**: Process running as `lazy-planner` cannot read secrets from `/run/lazy/secrets/`, cannot modify capability manifests in `/etc/lazy/capabilities/`, and cannot write directly to `/data/audit/audit.log` or `/etc/lazy/policy.yaml`.
- **Method**: Execute in-guest permission verification script as `lazy-planner` UID.
- **Evidence Path**: `tests/results/acceptance/S3_permissions.log`

### S4: Inviolable L4 Capability Refusal
- **ID**: `S4`
- **Pass Criterion**: Every attempt to invoke an L4 administrative or forbidden action (policy edit, audit rewrite, direct broker bypass, private key export) is unconditionally rejected by policy engine and logged as a security alert.
- **Method**: Send L4 attack payloads to gateway; assert HTTP 403 Forbidden and audit record.
- **Evidence Path**: `tests/results/acceptance/S4_l4_rejections.json`, `tests/results/acceptance/S4.log`

---

## 5. Documentation Checks (DOC1)

### DOC1: Complete Technical Documentation Suite & Acceptance Report
- **ID**: `DOC1`
- **Pass Criterion**: Full documentation suite present and updated: `README.md`, `USER_GUIDE.md`, `ARCHITECTURE.md`, `HARDWARE-CONTROL.md`, `docs/reports/results.md`, task deck inputs 1–8 in `docs/deck-inputs/`, `docs/demo/RUNSHEET.md`, video demonstration script `docs/demo/VIDEO_SCRIPT.md`, QA checklist `docs/qa/CHECKLIST.md`, and `docs/ACCEPTANCE_REPORT.md` generated by `scripts/accept.sh`.
- **Method**: Run documentation validator verifying existence, line counts, and cross-reference integrity.
- **Evidence Path**: `tests/results/acceptance/DOC1_doc_validation.json`
