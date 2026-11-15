<USER_REQUEST>
LAZY OS V2 PROMPT: REALITY CHECK, COMMAND CENTER, REAL DEMO
Paste this into Antigravity. It extends docs/BUILD_PROMPT.md (v1). If they conflict, this prompt wins. Keep the v1 rules R1 to R7 and F1 to F9 as well. Do not ask questions except for the HUMAN-ONLY items in section 7.

0. SITUATION
An earlier run reported all 32 milestones done (401 tests, large benchmark gains). Review has found these issues, which you must check and not assume:
 - The booted kernel was reported as the host's Ubuntu 6.8.0-149-generic, with a custom initramfs and GPT disk assembled by scripts/build-boot-image.py in /tmp. No native BitBake build was run.
 - lsblk showed Btrfs on /data (vda3) while df showed tmpfs for /data.
 - The local LLM was simulated in the guest.
 - The HUD so far is a basic page, not a Command Center.
 - Environment: WSL2 on Windows with limited RAM and disk.
The earlier reports are unverified claims. Your job: audit truthfully, fix the honesty and storage gaps, build the real Command Center, demonstrate it with real evidence, then complete the academic requirements as far as resources allow.

1. TRUTH RULES (T1 to T9)
T1 Classify everything as Verified (you ran it and saved raw output), Implemented (code exists, not run), Simulated (works but with fake data or behaviour), Unverified, or False. Never present anything above its class.
T2 Save raw command output, not summaries, in docs/audit/ or tests/results/.
T3 Never fabricate results, screenshots, metrics or integrations. A screenshot must come from a browser actually connected to the guest through the forwarded port. Record the URL and the guest identity shown in it.
T4 No fake panels. Every UI panel names its real data source. If the source is unavailable, show 'unavailable', never invented numbers. Any development mock sits behind ?mock=1 and shows a visible SIMULATED watermark.
T5 Preserve artifacts. Do not delete working files or old reports; move superseded docs to docs/archive/. Work on branch v2-command-center, merge to main after verification, tag v2-<phase>.
T6 Do not rebuild the kernel or root filesystem unless a step below requires it. If you must change the initramfs or rootfs, write new artifacts under build/v2/ and keep the old ones.
T7 Keep the architecture. The frontend never executes privileged operations. Every state-changing action goes UI, gateway, planner or typed request, policy, tasks, broker, audit.
T8 Resource care. Before heavy steps check RAM, disk and CPU on WSL2 (/proc/meminfo, df, nproc, and .wslconfig if readable). Never start a job that needs more than is available. Set QEMU -m to at most half of the free memory (minimum 1024). Run long jobs in the background with logs and record PID and log path in STATE.md.
T9 Same protocol as v1: docs/STATE.md with NEXT_ACTION on the first line, docs/PLAN_V2.md as a milestone table, commit per milestone, make handoff, HANDOFF BLOCK when context is low, no questions, defaults logged in docs/ASSUMPTIONS.md.

2. PHASE A: AUDIT (read-only, no code changes)
 V2.A1 Repo audit, writing docs/audit/REPO_AUDIT.md: branch, last commit, commit count, tree to depth 3, line counts per package, existing docs, HUD technology and size, every gateway route and WebSocket message (with file and line), QEMU and boot scripts, Yocto files, test layout.
 V2.A2 Build provenance, writing docs/audit/BUILD_PROVENANCE.md: read scripts/build-boot-image.py and the yocto/ tree. State exactly which kernel and modules boot, where the initramfs and rootfs come from, which init system runs, whether systemd exists in the guest, what 'compressed rootfs' measures, and whether any BitBake invocation or log exists anywhere. Quote paths and line numbers.
 V2.A3 Runtime audit, saving to docs/audit/runtime/: boot the existing image as the earlier report did (record the exact command), capture the serial log, then inside the guest save raw output of: uname -a; cat /proc/cmdline; mount; findmnt; df -h; lsblk; free -m; ps -eo pid,rss,comm --sort=-rss; ls /run/lazy; the status of each lazy-* unit or the equivalent process check; the gateway identity. From the host, request the forwarded port and prove the response comes from the guest by comparing a value only the guest knows (boot_id or /proc/version). Check that nothing on the host listens on the forwarded port other than QEMU.
 V2.A4 Claims ledger, writing docs/audit/CLAIMS.md: one row for each claim in the earlier report (every benchmark figure, 401 tests, 70 adversarial and 50 benign tests, F1 to F9, 15 services, hash-chained audit, snapshot rollback, LLM integration, boot and RAM figures, the HUD). Columns: claim, class, evidence path, how verified. Re-run make verify and record the real test count and time. Sample at least 25 tests across modules and note whether they assert real behaviour or only mocks. Examine the benchmark scripts and raw data: what exactly was measured for Debian and for Lazy, with which definitions, and whether the comparison is like for like (boot-time endpoint, RAM measurement point, whether kernel and modules are inside the size figure).
 V2.A5 Architecture assessment, writing docs/audit/ARCH_ASSESSMENT.md: weaknesses, missing components, security issues, backend and frontend gaps, build gaps, performance limits. Specific and short. No redesign.
 Print AUDIT SUMMARY (15 lines), then continue to Phase B.

3. PHASE B: TRUTH FIXES (minimal changes)
 V2.B1 /data storage. Make /data a real persistent filesystem in the guest. Preferred: Btrfs (include the btrfs module and its dependencies matching the booted kernel in the initramfs and load it before mounting). If this fails after 2 hours of effort, use ext4 plus the overlay or copy snapshot backend and document why. Evidence inside the guest: findmnt /data shows the real device; write a file, reboot the guest, read it back; run the snapshot, mutate and rollback test on that mount and compare tree hashes.
 V2.B2 Identity endpoint. Gateway GET /api/identity returns hostname, kernel release, boot_id, uptime, real mounts, image build id and git commit, from inside the guest. The HUD footer shows it. Add a unit test and a host-side curl proof.
 V2.B3 Honest labelling. GET /api/build-info lists, for each subsystem, real, simulated or absent (kernel source: host Ubuntu or custom; LLM; voice; web driver; comms; audit; snapshots; storage). The HUD shows badges from it. Correct README.md, docs/reports/results.md and docs/ARCHITECTURE.md so no document claims a custom kernel, a Yocto-built image or an in-guest LLM unless Verified. Move the previous versions to docs/archive/.
 V2.B4 Benchmark method. Write bench/METHOD.md with identical definitions for stock and Lazy: boot time = from VM start to a named ready marker (record kernel-plus-initramfs time and userspace time separately); idle RAM = free -m used after 60 seconds idle at the same VM memory size; size = the total bootable payload (kernel, modules, initramfs, rootfs) and, separately, rootfs only; package count from each system's own package database or manifest. Re-run both systems, 5 runs each, mean and standard deviation, raw outputs saved. If the Debian baseline cannot run, mark it 'not measured'. Update docs/reports/results.md with the old and corrected figures and an explanation.
 V2.B5 LLM in the guest. Check free memory, then try to run a small real model (a static llama.cpp build and a GGUF Q4 of about 1B parameters or smaller, from an official source, licence recorded in docs/LICENCES.md) inside the guest, with QEMU memory raised as far as T8 allows. Measure time to first token and tokens per second inside the guest. If impossible, keep the planner in mock mode in the guest, offer an optional host LLM bridge clearly labelled 'HOST LLM (not in image)', and mark the guest LLM SIMULATED.

4. PHASE C: COMMAND CENTER
Build a desktop-like command centre as a static single-page app in hud/ (plain HTML, CSS, JavaScript; no build step, no CDN, no external fonts or images; works offline), served by the guest gateway and using its REST and WebSocket APIs. It is a browser HUD, not a native Linux desktop; say so in the docs and in Settings.
Look and feel: dark navy and black background, cyan and blue accents, subtle glow on active elements, clean system-font typography, panels and cards, short smooth transitions, desktop-first layout from 1280x720 to 1920x1080, readable contrast, visible keyboard focus, a reduced-motion setting, a skippable boot animation of at most 3 seconds. Functional first, decoration second.
Shell: top status bar (Lazy OS brand, clock, network status, power status when available else 'n/a', alert count), left navigation, main workspace, notification tray, command bar on Ctrl+K, approvals drawer, and a footer with the identity string from /api/identity and the badges from /api/build-info.
Modules (each lists its data source in a code comment and in docs/ui/DATA_SOURCES.md):
 1 Home: wake-up briefing card, system health summary, recent tasks, quick commands.
 2 AI Command Center: natural-language input, conversation history, streaming plan view with step status, inline approval requests, results and errors, a task id and undo link for each executed task, a voice button (browser speech API, labelled 'browser speech, not in image', hidden when unsupported), and a planner mode badge (mock or llm).
 3 System Monitor: live CPU, RAM, disk and network, process list and service health from the guest, with SVG sparklines. Real data only.
 4 Agent Center: a card per component (planner, policy, tasks, fs, sys, hw, web and comms brokers, audit, secrets, outbox, routines, LLM) with real status, last activity time and request counts from the event stream and the audit ledger, plus a live pipeline view that lights up from real events.
 5 File Manager: browse, create, read, edit and delete through the filesystem broker, with breadcrumbs, confirmation dialogs, the task id and an undo action. Delete requires approval.
 6 Security Center: tier legend L0 to L4, pending approvals, an audit ledger viewer with a Verify chain button that calls the real verifier, rollback history with Undo, and allow and deny counts.
 7 App Launcher: tiles only for utilities backed by real capabilities (for example Notes via doc.create_markdown, Briefing, Outbox, Settings). Unbacked tiles show 'coming soon' and are not clickable.
 8 Settings: appearance (accent colour, reduced motion), system information from /api/identity, agent configuration (planner mode, model name), voice settings, security preferences (approval mode per capability, changed only through a policy-checked request).
Backend: reuse existing endpoints and add only what is missing: /api/identity, /api/build-info, /api/metrics, /api/services, /api/tasks, /api/approvals, /api/audit (list and verify), /api/fs (list and stat, through the broker), /api/capabilities, /api/briefing, /api/settings, and a WebSocket event stream. Every state-changing request goes through the policy engine; no endpoint bypasses it. Add unit tests for each new endpoint, including a test that a denied request changes nothing.
 V2.C1 Audit the existing HUD and API against this list and write docs/ui/GAP_LIST.md; then implement the shell, command bar, identity footer and badges.
 V2.C2 Modules 2, 4 and 6 (the core AI, agent and security experience), driven by real events.
 V2.C3 Modules 3 and 5.
 V2.C4 Modules 1, 7 and 8.
 V2.C5 UI tests: a headless-browser end-to-end run (use whatever is installable in WSL, such as Playwright with Chromium, otherwise Selenium) against the forwarded port of the running guest; one screenshot per module in docs/demo/screens/ plus manifest.json with the URL, the build id from /api/identity, the timestamp and the sha256 of each image; accessibility checks (contrast, focus, reduced motion).

5. PHASE D: REAL DEMONSTRATION
 V2.D1 scripts/run-lazy.sh boots the guest (GTK display when WSLg is available, otherwise no display), forwards the HUD port, prints the URL and writes PID and logs. scripts/stop-lazy.sh stops it. Document the WSLg and memory requirements.
 V2.D2 scripts/demo-e2e.py and docs/demo/DEMO.md perform and record: (1) open the HUD and show identity and badges; (2) type 'create a note called plan.md with a three-item checklist' in the command centre: plan, L1 policy, execution, and the file exists inside the guest (confirm with the file manager and with a guest command); (3) an L2 request such as deleting a file: an approval prompt in the UI, approve, executed; (4) the same request denied, and nothing changes; (5) the Agent Center shows component activity for the run; (6) the System Monitor shows live guest metrics and a visible change while a registered code.run workload runs; (7) the Security Center shows audit entries for the run, Verify chain passes, then a tampered copy of the log is detected by the verifier; (8) Undo the file task and show the tree hash returns to its earlier value.
 V2.D3 docs/demo/DEMO_REPORT.md: each step PASS or FAIL with evidence paths, plus a table of everything still SIMULATED. Take real screenshots (T3). Record a video only if a screen recorder is available; otherwise keep the screenshots.

6. PHASE E: ACADEMIC COMPLETION (as resources allow)
 V2.E1 Measure host resources and write docs/BUILD_ENV_PLAN.md with options: (a) a cloud VM runbook, (b) WSL2 with larger limits (.wslconfig suggestions, moving the virtual disk), (c) DL_DIR and the public sstate mirror to avoid compiling everything. Do not start a native BitBake build unless WSL has at least 16 GB RAM available and 120 GB free disk. Otherwise prepare everything, mark this milestone HUMAN ACTION REQUIRED and continue.
 V2.E2 If resources permit: run kas build for lazy-image-base in the background with logs, fix recipe errors iteratively, record elapsed time, boot the result in QEMU with its own kernel, rerun the Phase A runtime audit, and update the claims ledger.
 V2.E3 If not: validate the metadata as far as possible (layer listing, recipe parsing if the tooling is available) and document exactly what remains unproven.
 V2.E4 Final documentation: the kernel .config of the kernel that actually boots; the package manifest of the image that actually boots; a reproducibility statement that distinguishes the fast dev image path from the Yocto path; the stock-Linux comparison using bench/METHOD.md; corrected docs/deck-inputs/ files.
Cut order if short: voice button, launcher extras, settings persistence, V2.E2. Never cut Phase A, V2.B1 to V2.B3, the core Command Center modules (shell, command center, system monitor, agent center, file manager, security center) or V2.D2.

7. HUMAN-ONLY ITEMS
Ask only for: a sudo password when sudo -n fails and root is truly required; permission to raise WSL limits (.wslconfig change and restart); real account credentials (never required); downloads over 6 GB or from unofficial sources; anything that costs money. Everything else: apply defaults and log them in docs/ASSUMPTIONS.md.

8. FINISH
Print FINAL SUMMARY: (1) counts of Verified, Implemented, Simulated, Unverified and False items, with a link to docs/audit/CLAIMS.md; (2) the corrected benchmark table; (3) the three commands to run the demo; (4) the list of screenshots; (5) what is still missing for the assignment, especially the Yocto build; (6) human actions needed.
Begin with V2.A1.
</USER_REQUEST>
<ADDITIONAL_METADATA>
The current local time is: 2026-11-16T01:04:28+05:30.

The user's current state is as follows:
Active Document: c:\Users\len\OS\src\lazy\gateway\__init__.py (LANGUAGE_UNSPECIFIED)
Cursor is on line: 1
Other open documents:
- c:\Users\len\OS\scripts\build-boot-image.py (LANGUAGE_UNSPECIFIED)
- c:\Users\len\OS\src\lazy\tasks\backend.py (LANGUAGE_UNSPECIFIED)
- c:\Users\len\OS\docs\STATE.md (LANGUAGE_UNSPECIFIED)
- c:\Users\len\OS\tests\unit\test_broker_comms.py (LANGUAGE_UNSPECIFIED)
</ADDITIONAL_METADATA>