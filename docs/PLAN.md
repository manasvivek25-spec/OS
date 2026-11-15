# Lazy OS Milestone Plan

| ID | Title | Status | Evidence Path |
|---|---|---|---|
| M0.1 | Repo, all docs files, Makefile, scripts/check-env.sh, docs/ENV.md | done | tests/results/M0.1.log |
| M0.2 | Contracts: JSON Schemas for Intent, Plan, Decision, Event, Task, OutboxItem, Manifest; validator CLI; 30 valid & 30 invalid samples | done | tests/results/M0.2.log |
| M0.3 | Yocto bootstrap: kas files, pinned layers, minimal QEMU boot with ssh | done | tests/results/M0.3.log |
| M1.1 | lazy-audit: hash chain, verifier, tamper tests (modify, delete, reorder, truncate) | done | tests/results/M1.1.log |
| M1.2 | lazy-policy: manifest loader, tiers, effect classes, approval state machine, rate limits, taint tracking, L4 denylist | done | tests/results/M1.2.log |
| M1.3 | lazy-tasks: snapshot backends (btrfs, overlay, copy) and undo | done | tests/results/M1.3.log |
| M1.4 | Brokers: fs, sys (systemd D-Bus + fake), hw (sysfs injectable root + fake) | done | tests/results/M1.4.log |
| M1.5 | lazy-secrets: credential vault with peer-credential checks | done | tests/results/M1.5.log |
| M1.6 | lazy-gateway: JSON-RPC bus, WebSocket protocol, HUD token | done | tests/results/M1.6.log |
| M2.1 | Planner interface, mock mode, recorded-intent fixtures for every capability | done | tests/results/M2.1.log |
| M2.2 | llama.cpp built & served, model selection, assistant datasets (100 benign, 50 injection), grammar-constrained intents | done | tests/results/M2.2.log |
| M2.3 | Dialogue manager: clarifying questions, plan view, narration, pause/stop/redirect/undo, YAML correction rules, quiet mode | done | tests/results/M2.3.log |
| M2.4 | End-to-end text pipeline on host & 40-task suite in tests/tasks/*.yaml | done | tests/results/M2.4.log |
| M3.1 | HUD: transcript, plan view, step status, approvals diff, status strip, wake animation, futuristic offline style | done | tests/results/M3.1.log |
| M3.2 | Voice: wake phrase, STT (Vosk), TTS (espeak-ng), fallback, latency probes | done | tests/results/M3.2.log |
| M3.3 | Routines: wake sequence, briefing, chores in snapshot with undo, systemd timers | done | tests/results/M3.3.log |
| M3.4 | Niche feed: fetcher, reader (no-tools LLM call), TF-IDF ranking, feedback learning, exploration share, faithfulness checker | done | tests/results/M3.4.log |
| M3.5 | systemd sandbox units for every service | done | tests/results/M3.5.log |
| M4.1 | lazy-outbox: delay, undo window, approvals, hourly limits, new-recipient approval, attachment rules | done | tests/results/M4.1.log |
| M4.2 | Comms broker: maildir, SMTP sink, local chat service, capabilities | done | tests/results/M4.2.log |
| M4.3 | Web broker: driver interface, WebDriver, DOM extraction, allowlist, download quarantine, local test site | done | tests/results/M4.3.log |
| M4.4 | Attack suite: >=60 attacks, unguarded baseline flag, >=50 benign cases, safety metrics CSV | done | tests/results/M4.4.log |
| M5.1 | Kernel fragments: base-minimal, memory, fs, security, laptop drivers; Kconfig verification; size/boot benchmark | done | tests/results/M5.1.log |
| M5.2 | Recipes for services, dependencies, llama.cpp, Vosk, TTS; base & full images; docs/PACKAGES.md; licence check | done | tests/results/M5.2.log |
| M5.3 | Filesystem layout with wic: ro root, btrfs data, overlay /etc & /var, first-boot setup; QEMU verify | done | tests/results/M5.3.log |
| M5.4 | Interactive-latency tuning: preload, mlock, cgroup priority, CPU affinity; ablation script | done | tests/results/M5.4.log |
| M5.5 | Browser in full image or documented fallback | done | tests/results/M5.5.log |
| M5.6 | Reproducibility: rebuild from clean checkout, compare manifests and hashes | done | tests/results/M5.6.log |
| M6.1 | Baselines: stock Debian minimal in QEMU vs base & full (size, RAM, boot time, packages); 40% comparison | doing | tests/results/M6.1.log |
| M6.2 | Comprehensive evaluations: reports/results.md with measured data and plots | todo | tests/results/M6.2.log |
| M6.3 | Documentation: README, ARCHITECTURE.md, HARDWARE-CONTROL.md, deck-inputs/ 1-8, demo/RUNSHEET.md | todo | tests/results/M6.3.log |
| M6.4 | Final verification, tag v0-final, make handoff, FINAL SUMMARY | todo | tests/results/M6.4.log |
