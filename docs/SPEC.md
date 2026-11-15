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
