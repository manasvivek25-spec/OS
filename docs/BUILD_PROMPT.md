LAZY OS MASTER BUILD PROMPT v1
Paste all of this into Antigravity (or any coding agent with terminal access). It is complete. Do not ask questions except for the HUMAN-ONLY items in section 8.

0. MISSION AND RULES
You are the sole engineer building Lazy OS, a custom bootable Linux distribution (Yocto) for a university Operating Systems project (Track A, application-specific distribution). Build everything in this run: code, tests, benchmarks, image recipes, documentation, demo scripts. A human tests afterwards, so leave nothing unfinished, untested or undocumented.
R1 The repository is your memory. Your context can end at any time. Keep docs/STATE.md current so a new session continues exactly where you stopped.
R2 Never ask questions. If something is ambiguous, apply the DEFAULTS (section 4), log the choice in docs/ASSUMPTIONS.md and continue.
R3 Never change the architecture in section 2. If you think it is wrong, write docs/proposals/<n>.md and keep building on it.
R4 Evidence over claims. A milestone is done only when its exit test ran and the log is saved in tests/results/. Never fake, skip, weaken or delete a test. Never invent numbers; unmeasured means 'not measured'.
R5 Never invent package, recipe, kernel option or version names. Check by running the tool. Unchecked facts are marked UNVERIFIED.
R6 If time or context is short, priority is: core safety and OS image, then interaction, then routines and niche feed, then web and messaging. Cut from the end and record cuts in docs/KNOWN_ISSUES.md.
R7 Small steps: implement, test, fix, commit. After 5 failed attempts on one problem, log it in KNOWN_ISSUES.md and move on.

1. PRODUCT
Lazy OS lets the user give vision, commands and supervision (voice, text, HUD) while the OS does the work: writing documents and code, using software tools, system administration (services, settings, logs, processes), controlling the laptop's own hardware (backlight, volume, rfkill, power profile, CPU governor, USB), web browsing and form filling in an isolated browser, reading and sending email, and messaging. It is interactive: it asks clarifying questions, narrates, and can be paused, redirected or undone. It greets the user with a wake-up briefing (system status, tasks, overnight chores, niche news with cited sources), keeps the user up to date in their niche from local behaviour, and runs safe chores overnight. Trust comes from receipts, undo and measured accuracy: every action is audited, sandboxed and, where possible, undoable.
Assignment constraints: reproducible build from scripts; custom kernel .config; package manifest; two image profiles (base = no model, used for the 40% size comparison; full = model, voice, HUD, browser); benchmarks versus a stock distro (image size, RAM, boot time, package count, interaction latency, tokens per second); at least three hardening measures; read-only root with a writable data volume and overlay; everything open source except items listed and justified in docs/LICENCES.md.
Delivery stages: v0a = everything except web, email and messaging. v0b = web, email, messaging. Start v0b only after the v0a milestones pass.

2. FROZEN ARCHITECTURE
Language: Python 3 for all services (standard library first, few extra dependencies, each recorded). HUD: plain HTML, CSS and JavaScript, no build step, no CDN. Scripts: shell. IPC: JSON-RPC 2.0 over Unix domain sockets in /run/lazy/, one socket per service. The gateway also serves the HUD and a WebSocket on 127.0.0.1:8765. Every service is a separate systemd unit under its own user.
Services:
 lazy-gateway: I/O (HUD, WebSocket, text, voice events), sessions, HUD auth token
 lazy-planner: dialogue manager and LLM planner client; unprivileged, sandboxed, no network; outputs only typed intents and plans; modes: mock (recorded intents, for CI) and llm
 lazy-llm: llama.cpp server, resident and warm
 lazy-policy: validates intents against capability manifests; tier, effect class, approval mode, rate limits, taint check; approval state machine
 lazy-tasks: cancellable jobs, checkpoints, snapshots, undo
 lazy-broker-fs, lazy-broker-sys, lazy-broker-hw, lazy-broker-web, lazy-broker-comms: the only components that touch files, system, hardware, browser, mail and chat
 lazy-secrets: credential vault, peer-credential checked, unreachable by the planner
 lazy-outbox: queue for irreversible actions with delay, undo window and approval
 lazy-fetcher: sandboxed fetch of feeds and pages; lazy-reader: separate LLM call, no tools, structured text out
 lazy-routines: triggers, wake-up sequence, briefing, chores, niche feed
 lazy-audit: hash-chained append-only log with a verifier
Pipeline: input, gateway, planner (intent or plan), policy, staging (snapshot or outbox), preview and approval, broker, effect, audit. Untrusted text (web, mail, feeds, documents) goes fetcher, reader, planner as labelled quoted data, never as instructions.
Tiers: L0 read-only; L1 low-risk, automatic; L2 approval; L3 hazardous, explicit approval with preview, never by voice alone; L4 never allowed to the agent (policy, brokers, keys, audit, sandbox settings, mail forwarding rules).
Effect classes: reversible (snapshot undo), compensable (inverse action), irreversible (outbox).
Frozen rules:
 F1 The planner proposes; policy and brokers decide and execute.
 F2 No free-form shell. Only registered capabilities. Code runs only in transient sandboxed units (systemd-run with resource and filesystem limits).
 F3 Web, mail, feed and document text is data, never instructions.
 F4 Credentials are never visible to the planner.
 F5 Every task is a cancellable job with a checkpoint after each step.
 F6 L4 is hard-coded.
 F7 Everything is audited and, where possible, undoable.
 F8 Every external send goes through the outbox. Recipients, URLs and destinations come only from the user or from values the user confirmed (taint tracking).
 F9 The browser runs in its own isolated profile and namespace.
Contracts (JSON Schema in docs/contracts/, versioned):
 Intent {id, ts, task_id, requester(voice|text|hud|routine), capability, params, provenance[]}
 Plan {id, steps[Intent], rationale}
 Decision {intent_id, verdict(allow|ask|deny), tier, effect_class, reason, approval_mode}
 Event {id, ts, type, severity, source, data}
 Capability manifest (YAML in /etc/lazy/capabilities/): name, params schema with ranges, tier, effect_class, approval_mode, sandbox profile, undo method, taint rules
 OutboxItem {id, kind(mail|chat), to, subject, body, attachments, created, send_after, status(pending|approved|cancelled|sent), approvals[]}
Initial capabilities by tier:
 L0 fs.read fs.list sys.service_status sys.logs_read sys.process_list hw.usb_list web.read mail.list mail.read chat.read task.undo outbox.cancel (undo and cancel are user-only)
 L1 fs.write fs.copy fs.move doc.create_markdown doc.create_docx code.write hw.backlight_set hw.volume_set mail.draft web.navigate (allowlisted domains)
 L2 fs.delete code.run sys.service_restart sys.setting_set hw.rfkill_set hw.power_profile_set hw.governor_set web.navigate (new domain) web.click web.fill
 L3 web.submit web.download mail.send chat.send (all through the outbox) sys.process_signal hw.usb_authorize

3. REPO LAYOUT (create exactly)
lazy-os/: Makefile, README.md, LICENSE
 docs/: SPEC.md (sections 1 and 2 of this prompt verbatim), BUILD_PROMPT.md (this whole prompt), PLAN.md, STATE.md, DECISIONS.md, ASSUMPTIONS.md, KNOWN_ISSUES.md, ENV.md, LICENCES.md, PACKAGES.md, ARCHITECTURE.md, HARDWARE-CONTROL.md, contracts/, proposals/, reports/, demo/, deck-inputs/, qa/
 src/lazy/: one package per service plus common/
 hud/: static HUD
 config/: capabilities/*.yaml, policy.yaml, feeds.yaml, routines.yaml, allowlist.yaml
 tests/: unit/, integration/, attacks/, assistant/, tasks/, fixtures/ (local website, maildir, local chat, feeds, fake sysfs), results/
 bench/: scripts, results/
 scripts/: check-env.sh, setup-host.sh, handoff.sh, yocto-container.sh
 yocto/: kas/, meta-lazy/ (recipes-kernel, recipes-lazy, images, wic)

4. DEFAULTS (use these; never ask)
 Host: Linux x86-64. Run scripts/check-env.sh and write docs/ENV.md. Missing tool: install it (sudo -n). If sudo is unavailable, use user-space alternatives or run root-needing tests inside the QEMU image over ssh. Never ask for a password.
 If the host cannot run Yocto (about 16 GB RAM and 200 GB free needed), still build milestones M0 to M4 on the host, write scripts/yocto-container.sh (a Yocto build container; verify the image name) and print HUMAN ACTION REQUIRED for the image phase.
 Yocto: newest LTS release supported by all pinned layers (verify). Layers: poky, meta-openembedded, meta-lazy (ours), meta-browser only if needed. kas for pinning. One command: ./build.sh base|full.
 Kernel: the Yocto reference kernel for qemux86-64; our config as fragments in yocto/meta-lazy/recipes-kernel.
 Data volume: Btrfs with subvolume snapshots. Snapshot backends behind one interface: btrfs (default), overlay, copy (reflink, for host unit tests).
 Sandboxing: systemd unit options (ProtectSystem, PrivateTmp, NoNewPrivileges, SystemCallFilter, RestrictAddressFamilies, MemoryMax, CPUWeight) plus systemd-run for code execution.
 LLM: llama.cpp built from a pinned release. Model chosen by rule: test open-licence instruct models in GGUF (Q4) from official sources, up to 6 GB of downloads in total. Pick the smallest model that scores at least 90% valid-schema intents on tests/assistant/benign.jsonl and has 0 injection successes on the first 20 attacks with grammar-constrained decoding. Verify and record each licence from its model card; prefer Apache-2.0 or MIT. If none passes, pick the best and record the shortfall.
 Speech: wake phrase by Vosk restricted-grammar recognition (default phrase: wake up, daddy's home; configurable); STT Vosk small model; TTS: the best open-source TTS available as a Yocto recipe (default espeak-ng; verify licence). Voice is optional; text always works.
 Niche feed: TF-IDF cosine ranking in pure Python plus online-learned accept and dismiss weights, 20% exploration share, feeds from config/feeds.yaml (default local fixture feeds so tests work offline).
 Web: driver interface; default WebDriver driver with a headless browser. If the browser cannot be built into the image after one focused day of attempts, validate on the host, document the shortfall and continue.
 Mail: drivers maildir plus local SMTP sink (default for tests and demo), imap/smtp (disabled by default). Chat: local chat service (WebSocket fixture) by default, telegram driver (Bot API) disabled by default. Real accounts only by explicit human configuration.
 Paths and ports: /run/lazy/*.sock, 127.0.0.1:8765, /var/lib/lazy, /etc/lazy, /var/log/lazy.
 Style: type hints, small modules, docstrings on public functions, structured logging, no global state, deterministic tests with fixed seeds.

5. WORK PROTOCOL
Files you maintain:
 docs/PLAN.md: the milestone list of section 6 as a table: ID, title, status (todo|doing|done|blocked|cut), evidence path.
 docs/STATE.md: the FIRST LINE is always NEXT_ACTION: <the exact next command or task>. Then: the last 10 completed steps, current milestone, open problems, human actions pending.
 docs/DECISIONS.md and docs/ASSUMPTIONS.md: append-only, dated.
Loop for every milestone: read PLAN.md and STATE.md; re-read section 2 of docs/SPEC.md; implement; write tests with the code; run make verify-<ID>; save logs to tests/results/<ID>.log; fix; commit '<ID>: what'; update PLAN.md and STATE.md (NEXT_ACTION must let a stranger continue); go straight to the next milestone.
Git: main branch only; commit after every milestone and every 30 minutes of work; tag completed milestones m-<ID>; never force-push; keep large downloads and build outputs out of git.
Make targets: setup, status, verify (all non-LLM, non-image tests), verify-<ID>, verify-image, eval-tasks, eval-llm, eval, demo, image-base, image-full, handoff (writes docs/HANDOFF.md from PLAN.md and STATE.md).
Long jobs (Yocto, model downloads, benchmarks): start them in the background with logs in build-logs/, record the PID and log path in STATE.md, and work on other milestones meanwhile.
If your context is running low: finish the current commit, run make handoff, update STATE.md, print the HANDOFF BLOCK (done, doing, next 5 actions, blockers, how to verify) and stop. A new session will receive the RESUME prompt and continue at NEXT_ACTION.

6. MILESTONES (do them in order; exit test in brackets)
Phase 0 Foundation
 M0.1 Repo, all docs files, Makefile, scripts/check-env.sh, docs/ENV.md. [make status prints the milestone table]
 M0.2 Contracts: JSON Schemas for Intent, Plan, Decision, Event, Task, OutboxItem and the capability manifest; a validator CLI; 30 valid and 30 invalid samples. [tests pass]
 M0.3 Yocto bootstrap, started early in the background: record release and layer commits in DECISIONS.md; kas files; a minimal image boots in QEMU with ssh. [log shows login and systemctl is-system-running]
Phase 1 Core on the host
 M1.1 lazy-audit: hash chain, verifier, tamper tests (modify, delete, reorder, truncate). [all detected]
 M1.2 lazy-policy: manifest loader, tiers, effect classes, approval state machine (pending, approved, denied, expired), rate limits, taint tracking (untrusted values cannot become recipients, URLs or credentials), L4 denylist. [at least 150 table-driven tests pass]
 M1.3 lazy-tasks, snapshot backends and undo. [discard returns the tree to its pre-task hash; commit persists; cancel mid-task works]
 M1.4 Brokers fs, sys (systemd D-Bus wrapper plus a fake for tests) and hw (sysfs with an injectable root and fake sysfs fixtures). [every capability has a manifest, a handler and tests]
 M1.5 lazy-secrets with peer-credential checks. [the planner user cannot read secrets]
 M1.6 lazy-gateway: JSON-RPC bus, WebSocket protocol, HUD token. [protocol tests pass]
Phase 2 Planner and dialogue
 M2.1 Planner interface, mock mode, recorded-intent fixtures for every capability. [tests pass]
 M2.2 llama.cpp built and served; model selection per section 4; write tests/assistant datasets (100 benign, 50 injection); grammar-constrained intents. [results CSV and chosen model recorded]
 M2.3 Dialogue manager: clarifying questions with options, plan view, narration events, pause, stop, redirect, undo command, correction rules in readable YAML, quiet mode. [golden-transcript tests pass]
 M2.4 End-to-end text pipeline on the host and a 40-task suite in tests/tasks/*.yaml (files, documents, code, admin, hardware). [make eval-tasks runs in mock and llm modes]
Phase 3 Interface and routines
 M3.1 HUD: transcript, plan view with step status, approvals panel with diffs, status strip (CPU, RAM, model, mode), wake-up animation, futuristic style, works offline. [screenshots from a headless browser if available]
 M3.2 Voice: wake phrase, STT, TTS, text fallback, latency probes. [tested with synthetic audio generated by the TTS]
 M3.3 Routines: wake-up sequence, briefing (system status, tasks from ~/tasks.md, overnight chores, niche items), chores (tidy downloads, backup, log digest, update check against a local manifest) each in a snapshot with undo, systemd timers. [briefing test passes]
 M3.4 Niche feed: fetcher, reader (separate no-tools LLM call, summaries cite item IDs), profile from local signals, ranking, feedback learning, exploration share, profile viewer and editor API, faithfulness checker. [every claim maps to a source item]
 M3.5 systemd sandbox units for every service. [units written; scores recorded after M5.2]
Phase 4 v0b (only after Phases 1 to 3 pass)
 M4.1 lazy-outbox: delay, undo window, approvals, per-hour rate limits, new-recipient approval, attachment rules. [cancel inside the window and send after the window both tested]
 M4.2 Comms broker: maildir and SMTP sink drivers, imap/smtp and telegram drivers (disabled by default), local chat service; mail.list, mail.read, mail.draft, mail.send, chat.read, chat.send. [tests pass]
 M4.3 Web broker: driver interface, WebDriver driver, DOM-to-structured extraction (visible text, links, form fields with element IDs, hidden text flagged), domain allowlist and new-domain approval, download quarantine, local test website (search, form, login with fake credentials, a page with hidden injected instructions). [tests pass]
 M4.4 Attack suite: at least 60 attacks across files, feeds, web pages, emails, chat, voice replay and capability abuse (L4 attempts, forged recipients, forwarding rules, exfiltration through a form submit); an unguarded baseline behind a test-only flag, with a CI check proving the flag is absent from images; at least 50 benign cases. [CSV with unsafe-action rate, false-block rate, latency overhead]
Phase 5 Operating system image
 M5.1 Kernel fragments: base-minimal, memory (zram, THP, cgroup v2), fs (btrfs, overlayfs, squashfs), security (seccomp, Landlock, namespaces), laptop-control drivers as modules (backlight, rfkill, power, input, audio). Look up every symbol in the Kconfig of the exact kernel version; a check script verifies none were dropped. [before and after kernel size and boot time, 10 runs, mean and stdev]
 M5.2 Recipes for all services, Python dependencies, llama.cpp, Vosk and TTS; image profiles base and full; docs/PACKAGES.md with include and exclude reasons; licence manifest and SBOM; a check that fails on any licence not allowed in docs/LICENCES.md. [both images build]
 M5.3 Filesystem layout with wic: read-only root, Btrfs data volume, overlay for /etc and /var, first-boot service that creates users and volumes. [make verify-image runs the integration tests inside QEMU over ssh]
 M5.4 Interactive-latency tuning: model warm-up service (preload and mlock), cgroup priorities (planner and voice above routines), CPU affinity; an ablation script that toggles one setting at a time. [p50 and p95 time-to-first-token and time-to-first-word, idle and under background load]
 M5.5 Browser in the full image or the documented fallback. [integration tests still pass]
 M5.6 Reproducibility: rebuild from a clean checkout with one command and compare manifests and hashes. [result recorded honestly]
Phase 6 Evaluation and deliverables
 M6.1 Baselines: stock Debian minimal in QEMU (image size, idle RAM, boot time, package count) against base and full. Report the 40% target honestly, with the 20 largest packages for any shortfall. [CSV and table]
 M6.2 Run every evaluation (tasks, web tasks, safety, latency, ablation) and write docs/reports/results.md with tables only from measured data, plus plots. [file exists, every number traces to a CSV]
 M6.3 Documentation: README (build, run, test and demo in under 10 commands), ARCHITECTURE.md with diagrams, HARDWARE-CONTROL.md, docs/deck-inputs/ (one file per assignment task 1 to 8 with evidence links), docs/demo/RUNSHEET.md for the live demo plus a fallback video script. [files exist]
 M6.4 Final: make verify green, or every failure listed in KNOWN_ISSUES.md; tag v0-final; make handoff; print FINAL SUMMARY.
Cut order if short: M3.4, M3.2, M4.3 browser, M4.2 chat, M5.5.

7. TEST REQUIREMENTS
 Every service has unit tests. Integration tests run on the host with the mock planner. Image integration tests run in QEMU over ssh (tests/integration/image/). Tests are deterministic, use fixed seeds and need no network unless tagged net. Tag each test with the rule or feature it covers (F1 to F9). Line coverage for lazy-policy and lazy-tasks is at least 90%. Results go to tests/results/. Safety tests must prove the negative: for each rule, a test that tries to break it.

8. HOST SAFETY AND HUMAN-ONLY ITEMS
 Never run destructive commands outside the repo and its build directories. Never run dd, mkfs or mount on real devices; use loop files inside the build directory. Do not change the host's real settings: hardware tests use fake sysfs, and real changes happen only inside the QEMU image. Never send real mail or messages, never log in to real sites, never put secrets in the repo; use fixtures and fake credentials.
 Ask the human ONLY for: a sudo password when sudo -n fails and root is truly required; real account credentials (never required); booting or flashing physical machines (only with a device path the human supplies); live microphone and speaker tests; downloads over 6 GB or from unofficial sources; anything that costs money. For everything else, apply the defaults.

9. DONE AND FINAL SUMMARY
Done means: all milestones done or listed as cut or blocked in KNOWN_ISSUES.md, make verify green or each failure documented, docs complete, v0-final tagged. Print FINAL SUMMARY (10 lines): what was built; what was verified and how; key measured numbers; what was cut and why; known issues; human actions needed; the exact commands to run the demo.
Begin now with M0.1.
