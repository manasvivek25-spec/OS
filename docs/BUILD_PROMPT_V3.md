LAZY OS V3 PROMPT: COMPLETE THE PRODUCT
Paste this into Antigravity. It extends docs/BUILD_PROMPT.md (v1) and docs/BUILD_PROMPT_V2.md (v2). Read both and docs/audit/* first. If they conflict, v3 wins. Keep the v1 rules R1 to R7, the architecture rules F1 to F9, and the v2 truth rules T1 to T9.

0. GOAL
Deliver Lazy OS as a finished product: a genuine custom Linux distribution, built from scripts, that boots in QEMU straight into the Lazy OS graphical Command Center with no host browser involved, and that the user can start with one command and use like an end-user product. Every feature in docs/SPEC.md (sections 1 and 2, stages v0a and v0b) and every Command Center module must exist, work inside the booted image, and pass an acceptance check. Nothing is simulated unless a VM makes it impossible, and then it is labelled and has a physical-hardware self-test.

1. STOP RULE
Do not stop, and do not print FINAL SUMMARY, until one of these is true:
 (a) every acceptance check in section 3 is PASS, or
 (b) every remaining check is BLOCKED by a HUMAN-ONLY item (section 8), after you have finished all unblocked work.
Never reach (a) by weakening, deleting or relabelling a check, by hard-coding results, or by testing on the host instead of the booted image. A check passes only when scripts/accept.sh, run against the booted image, saves raw evidence for it.
When your context runs low, follow the v1 handoff protocol and stop. The user will paste the resume prompt and you continue.
Blocked-item protocol: if something cannot be done after 4 hours of focused effort, or because of resources, do not fake it. Implement the best honest alternative that meets the check's intent if one exists, mark the check BLOCKED or PARTIAL with the reason and the exact human action needed, record it in docs/BLOCKED.md, and continue with other work.

2. KEY DECISIONS (defaults; do not ask)
 K1 Build system: the primary build is Buildroot with a br2-external tree in lazy-br2/, so that the build completes on this machine (WSL2, about 11.5 GB RAM). Use a prebuilt external toolchain if one is available and verified; otherwise build the toolchain. Keep yocto/meta-lazy. If a Yocto build host with at least 16 GB RAM and 120 GB disk becomes available, also run the Yocto build and fill the comparison with measured data. build.sh accepts BUILD_SYSTEM=buildroot (default) or BUILD_SYSTEM=yocto.
 K2 Target: x86_64 UEFI, our own kernel built from a defconfig plus fragments in lazy-br2/board/lazy/linux/, systemd as init, a read-only root image (squashfs or erofs), a volatile writable overlay, a persistent Btrfs /data on its own partition, and a first-boot service that creates users and volumes.
 K3 Services: each lazy-* service is a separate systemd unit under its own user with sandbox options. No single daemon hosts them all.
 K4 Graphical session in the guest: boot to a full-screen Wayland or DRM/KMS session running a WebKit-based kiosk (verify availability in Buildroot: wpewebkit with cog, plus a minimal compositor) that shows the Command Center from the guest gateway. QEMU runs with a virtio GPU and input devices, displayed through GTK on WSLg. If a WebKit kiosk cannot run after 8 hours of effort, fall back to the best in-guest browser that builds and record the fallback. Never fall back to a host browser; if the in-guest path fails completely, mark P1 BLOCKED.
 K5 In-guest LLM: llama.cpp (write a Buildroot package) and a small GGUF in the full image, chosen by the v1 rule (the 360M-parameter model mentioned in the v2 report is a candidate). QEMU guest memory defaults to 3072 MB; reduce only if free WSL memory requires it. Measure time to first token and tokens per second inside the guest.
 K6 Voice in the guest: Vosk (wake phrase by restricted grammar, and STT) and an open-source TTS, both packaged, with audio through QEMU's audio backend on WSLg. Test with synthetic audio loopback. The live microphone test is a human step.
 K7 Web broker: use WebDriver on the in-guest engine if available (WPE WebDriver or equivalent). Otherwise implement an HTTP fetch and DOM mode with form submission (no JavaScript) and label it 'HTTP mode'.
 K8 Mail and chat: the full image includes a local mail system (Postfix or equivalent, Dovecot or equivalent, if the packages exist) so email works end to end offline between local users. IMAP and SMTP drivers also work against any real account the user configures. Chat uses a local chat service plus optional Matrix or Telegram connectors. Test accounts only.
 K9 Terminal app: a Terminal app in the Command Center (PTY, unprivileged lazy user, audited) for the human. It is separate from the agent, which still has no free-form shell (F2).
 K10 Hardware control: implement every hw capability against the real kernel interface. In the VM use what exists (rfkill through the mac80211_hwsim module, USB through QEMU xhci devices, audio through QEMU audio, anything else the VM exposes). For interfaces a VM cannot provide (backlight, real CPU governor, battery), keep the fake-sysfs tests, label them VM-UNAVAILABLE in the badges, and write scripts/hw-selftest.sh for a human to run on a real machine.
 K11 Resource care (T8 still applies): check RAM and disk before every heavy step. Buildroot needs at least 30 GB of free disk. Keep downloads under 5 GB in total unless the human allows more. Use ccache and a download cache outside the repo. Run long builds with nohup and logs so a WSL restart does not lose progress.

3. ACCEPTANCE CONTRACT (write it first, freeze it, then build to it)
Create docs/acceptance/ACCEPTANCE.md and scripts/accept.sh before any other V3 work. Each check has an ID, a precise pass criterion and a script that tests the booted image (through serial or ssh, the gateway API, a headless browser connected to the guest, and QEMU monitor screendumps of the in-guest display). Record the sha256 of the acceptance files in docs/acceptance/FROZEN.sha256. After that, change an acceptance file only to fix a bug in the check itself, and log each change with its reason in docs/DECISIONS.md.
Product
 P1 One command (./dist/run-lazy-os.sh) opens a QEMU window and boots to a full-screen Lazy OS session in the guest. Screendumps from QEMU's own display show the HUD with the guest identity. No host browser is used.
 P2 A boot splash and a first-run wizard (name, wake phrase, accent colour, approval defaults) whose settings persist across reboot.
 P3 The wake phrase (typed and spoken) starts the briefing in the UI and by voice.
 P4 All Command Center modules (Home, AI Command Center, System Monitor, Agent Center, File Manager, Security Center, App Launcher, Settings) plus Terminal, Browser and Help. Every panel shows real data from the guest.
 P5 Shutdown and reboot from the UI; state persists.
 P6 Works offline. With a network it fetches feeds and browses.
 P7 dist/ contains the bootable disk image, run scripts for Linux, WSL and Windows, converted images (qcow2, vdi, vmdk), USER_GUIDE.md and a one-page quick start.
Operating system (assignment)
 O1 make dist builds everything from a clean checkout using scripts only, and keeps the build log.
 O2 The booted kernel is our own build: uname -r and /proc/version show it, the .config and fragments are in the repo, no Ubuntu kernel is used anywhere, and a before and after size and boot table exists against the stock defconfig.
 O3 systemd runs at least 15 separate lazy-* services under separate users, auto-started in dependency order. systemd-analyze security scores are recorded.
 O4 The root filesystem is read-only, a write to / fails, the overlay is volatile, and /data is a real persistent Btrfs partition. All are verified after a reboot.
 O5 At least three hardening measures, each with a test: read-only root; systemd sandboxing with seccomp and no-new-privileges; secrets isolation by user; signed update bundles (verify the signature and reject a tampered bundle).
 O6 Package manifest, licence list and SBOM are generated from the build (Buildroot legal-info or equivalent). Anything proprietary is listed and justified.
 O7 Build-system comparison table: Buildroot built and measured; Yocto measured if built, otherwise metadata validated and the exact reason stated.
 O8 Stock comparison measured per bench/METHOD.md against a real Debian 12 minimal VM: payload size, rootfs size, idle RAM (both used and MemTotal minus MemAvailable), boot time to a named ready marker (at least 10 runs, mean and standard deviation), package count.
 O9 A clean-checkout rebuild reproduces the manifests and, where feasible, the image hashes. Differences are explained.
Features
 FT1 The in-guest LLM runs and drives the planner. At least 90% valid-schema intents on tests/assistant/benign.jsonl, and 0 injection successes in the attack set with grammar-constrained decoding. Time to first token and tokens per second are measured in the guest.
 FT2 The 40-task suite passes at 100% with the mock planner and at least 90% with the real in-guest LLM, run inside the guest.
 FT3 Dialogue: clarifying questions, plan view, pause, stop, redirect, undo, correction rules, quiet mode.
 FT4 Hardware control: every hw capability passes against the real interface, or is labelled VM-UNAVAILABLE with a human self-test script.
 FT5 Web: navigation with allowlist and new-domain approval, reading, form fill and submit with approval, download quarantine, on the local test site and on at least one real public static page.
 FT6 Mail and chat: draft, preview, outbox, undo window, send and receive between local users in the guest; real-account drivers implemented and unit tested; chat send and read; recipient taint rules enforced.
 FT7 Wake-up briefing, overnight chores in snapshots with undo, and the niche feed with cited sources, profile editing, feedback learning and a faithfulness check.
 FT8 Voice: wake phrase, STT and TTS in the guest, text fallback, word error rate measured on synthetic speech.
 FT9 The Terminal app works for the human and is audited. The agent still cannot open a shell.
Safety
 S1 At least 100 attacks (files, feeds, web pages, emails, chat, voice replay, capability abuse, L4 attempts) run against the real in-guest stack with 0 breaches. At least 50 benign cases with the false-block rate reported. The unguarded baseline exists only behind a test flag, and a check proves it is absent from dist/.
 S2 The audit chain is verified and tampering is detected inside the booted image.
 S3 The planner user cannot read secrets or write policy, manifests or the audit log. Tested in the guest.
 S4 Every L4 action is refused.
Documents
 DOC1 README.md, USER_GUIDE.md, ARCHITECTURE.md, HARDWARE-CONTROL.md, docs/reports/results.md (measured numbers only), docs/deck-inputs/ for assignment tasks 1 to 8, docs/demo/RUNSHEET.md, a video script, a docs/qa/ checklist for the tester, and docs/ACCEPTANCE_REPORT.md generated by scripts/accept.sh with PASS, FAIL and BLOCKED counts and evidence hashes.

4. MILESTONES (in order; start long builds early in the background)
 V3.0 Merge v2-command-center into main after make verify. Create branch v3-product. Write docs/PLAN_V3.md, the acceptance suite and FROZEN.sha256.
 V3.1 Buildroot foundation: the lazy-br2 external tree, defconfig, kernel defconfig and fragments, toolchain, a first boot of our own kernel and root filesystem in QEMU over serial, systemd, the read-only root image, overlay, Btrfs /data, the first-boot service, and a make dist skeleton. [O2, O3 partial, O4]
 V3.2 Package the platform: the Python runtime and dependencies, all lazy-* services as separate systemd units under separate users with sandbox options, config, capabilities, HUD assets, users and permissions. [O3, S3]
 V3.3 In-guest LLM: the llama.cpp package, model selection and storage, the planner in llm mode, measurements. [FT1]
 V3.4 In-guest graphical session: compositor, WebKit kiosk, boot splash, input, display; boots to the Command Center full screen; screendump tests. [P1, P2, P5]
 V3.5 Command Center completion in the guest: all modules on real data, Terminal app, Browser app, Help, first-run wizard, settings persistence. [P2, P4, FT9]
 V3.6 Features in the image: routines, wake-up, chores, niche feed, dialogue completion. [P3, FT3, FT7]
 V3.7 Web broker and browser engine integration. [FT5]
 V3.8 Mail system, comms broker with outbox, chat service. [FT6]
 V3.9 Voice in the guest. [FT8]
 V3.10 Hardware control against real VM interfaces plus hw-selftest.sh. [FT4]
 V3.11 Hardening: sandbox scores, signed update bundles, secrets isolation, L4 tests. [O5, S1 to S4]
 V3.12 Evaluation: a real Debian baseline, the benchmark method, at least 10 runs, an OS-tuning ablation, the attack suite at scale, the 40-task run in the guest. [O7, O8, FT2, S1]
 V3.13 Packaging: dist/, converted images, run scripts, USER_GUIDE, quick start. [P6, P7]
 V3.14 Documents and reports, plus a clean-checkout rebuild and reproducibility check. [O6, O9, DOC1]
 V3.15 Final acceptance: run scripts/accept.sh against dist/ from a clean directory, fix failures, repeat until every check is PASS or BLOCKED by a human-only item, generate docs/ACCEPTANCE_REPORT.md, tag v3-final, run make handoff.
 V3.16 Optional, only if a suitable host exists: the Yocto build with kas and a measured comparison.

5. WORK PROTOCOL
Same as v1 and v2: docs/STATE.md with NEXT_ACTION on the first line, PLAN_V3.md as a table, a commit per milestone, tests with every change, raw evidence in tests/results/ and docs/audit/, a handoff when context is low. Added rules: after every milestone run scripts/accept.sh --only <IDs> on the booted image and record the result in PLAN_V3.md. Keep docs/BLOCKED.md listing every BLOCKED or PARTIAL check with its reason and the human action.

6. QUALITY BAR FOR THE PRODUCT FEEL
Boot to the UI in a reasonable time (record it). No stack traces or debug text on screen. Every action has visible feedback and an undo where possible. Errors are shown in plain language. The UI is keyboard accessible, responsive from 1280x720 to 1920x1080, and has a reduced-motion setting. Defaults are safe. The first-run wizard and the Help panel explain tiers, approvals and undo in simple terms.

7. TRUTH RULES STILL APPLY
T1 to T9 from v2 stay in force: classify claims honestly, never fabricate, take screenshots only from the real guest display, no fake panels, keep raw evidence, preserve artifacts.

8. HUMAN-ONLY ITEMS
Ask only for: a sudo password when sudo -n fails and root is truly required; raising WSL limits (.wslconfig change and restart); a cloud or larger build host for the optional Yocto build; real account credentials (never required); live microphone and speaker tests; running hw-selftest.sh on physical hardware; testing the images in VirtualBox or VMware; downloads over 5 GB; anything that costs money. For everything else, apply the defaults and log them.

9. FINISH
Print FINAL SUMMARY: acceptance counts (PASS, FAIL, BLOCKED) with links to docs/ACCEPTANCE_REPORT.md and docs/BLOCKED.md; the one command to run the product; the measured benchmark table; the screenshot list taken from the guest display; what remains for the human. Begin with V3.0.