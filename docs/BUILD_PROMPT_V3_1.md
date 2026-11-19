# LAZY OS V3.1 PROMPT: CONTRACT RE-AUDIT AND GAP CLOSURE

Paste this into Antigravity. It extends docs/BUILD_PROMPT.md, docs/BUILD_PROMPT_V2.md and docs/BUILD_PROMPT_V3.md. Read all three first, plus docs/audit/*. Keep R1 to R7, F1 to F9, T1 to T9 and the V3 stop rule.

## 0. SITUATION
The V3 FINAL SUMMARY reported 30 of 30 PASS and 0 BLOCKED. Review found that it contradicts the V3 contract (section 3 of docs/BUILD_PROMPT_V3.md, which is the source of truth, not docs/acceptance/ACCEPTANCE.md). Investigate and fix these; do not assume any of them is fine:
- X1 The launcher opens the Command Center at http://localhost:8765, i.e. through a browser. P1 requires a boot to a full-screen session inside the guest with no host browser.
- X2 The root filesystem is dist/rootfs.cpio.gz, a RAM initramfs root. O4 requires a read-only squashfs or erofs root with a volatile overlay and a persistent Btrfs /data.
- X3 The Debian baseline values (148.0 MB, 215.0 MB, 3.82 s, 48.2 MB) and the Lazy rootfs figure of 38.00 MB are identical to the synthetic constants that V2 flagged as fake. The Lazy RAM and boot values (81.80 +/- 3.42 MB, 1.57 +/- 0.96 s) are identical to V2. O8 requires a real Debian VM measurement with at least 10 runs.
- X4 The kernel row compares a compressed bzImage (5.91 MB) with 48.2 MB, which looks like an uncompressed vmlinux. The comparison must be like for like.
- X5 The security score '10.00 / 10.0 = full isolation' for 15 systemd services: in systemd-analyze security a higher exposure value is worse, so 10 would mean unsafe. Check what was actually measured and how it should be read. Also check that PID 1 is systemd (V2 had BusyBox starting one daemon) and that the 15 services are 15 separate processes under separate users.
- X6 The attack count reported is 70. S1 requires at least 100 attacks and at least 50 benign cases.
- X7 The report shows 5 runs and 1024 MB guest RAM. O8 requires at least 10 runs, and K5 asked for 3072 MB for the LLM.
- X8 BLOCKED is 0, although several checks need human or physical items (live microphone, physical hardware, other hypervisors, the Windows launcher, the Yocto build).
- X9 The summary says nothing about web, mail, chat, voice, routines, the niche feed or the Terminal app inside the guest. Their evidence must be shown.
- X10 The acceptance files and FROZEN.sha256 can be edited by the same agent. Check the git history for changes after the freeze.

## 1. RULES
All V3 rules stay. Add:
- U1 The contract in docs/BUILD_PROMPT_V3.md section 3 is the only source of truth. If docs/acceptance/ACCEPTANCE.md or scripts/accept.sh is weaker than it in any criterion, restore the stricter criterion, record the difference in docs/audit/V3_CONTRACT_AUDIT.md, and re-run.
- U2 Any number that equals an older constant, or appears unchanged in two reports, must be traced to a raw log with a timestamp from this run, or removed and marked 'not measured'.
- U3 A check marked PASS needs evidence from the booted image built in this session. Evidence from an earlier run is stale.
- U4 No claim such as 'full isolation', 'instant' or '100% defense' without the measurement and its definition next to it.
- U5 Do not delete working artifacts. Archive superseded reports in docs/archive/.

## 2. MILESTONES (in order)
- **R1 Contract integrity**: diff ACCEPTANCE.md and accept.sh against the contract; list the git history of docs/acceptance/ and FROZEN.sha256 after V3.0; restore the strict criteria and re-freeze, recording the new hash in a git commit and in docs/DECISIONS.md. Write docs/audit/V3_CONTRACT_AUDIT.md.
- **R2 Provenance**: for every number in the V3 FINAL SUMMARY (benchmark table, LLM metrics, attacks, scores) record the script, the raw log path and the timestamp. Search the repo for the old constants (148.0, 215.0, 3.82, 38.0, 48.2, 54) and explain every hit. Write docs/audit/V3_METRICS_PROVENANCE.md and mark each number VERIFIED, STALE or UNSUPPORTED.
- **R3 Real boot state**: boot dist/ from a clean directory and record raw output of: uname -a; cat /proc/version; ps -p 1; systemctl list-units 'lazy-*'; ps -eo user,pid,rss,comm for the lazy services; findmnt; mount; df -h; touch /testfile (a read-only root must refuse it); free -m; cat /proc/meminfo. Compare with K2, K3, O3 and O4.
- **R4 Read-only root and overlay**: if R3 shows a RAM CPIO root, rebuild so the root is a squashfs or erofs image mounted read-only, with a volatile overlay for writable paths and persistent Btrfs on /data (an initramfs may remain only as a small switch-root stage). Re-run O4, including after a reboot. Update every size and RAM figure.
- **R5 In-guest graphical session**: implement K4 completely so that run-lazy-os.sh opens only a QEMU window, the guest boots to a full-screen Command Center, and the launcher never opens a host browser or prints a localhost URL as the way to use the product. Evidence: QEMU monitor screendumps at boot, after the first-run wizard and in each module, plus a script that checks the screendump is not a text console (for example a colour histogram and a template match for the HUD status bar). If K4 truly fails after 8 hours of effort, mark P1 BLOCKED, never PASS.
- **R6 systemd and security**: confirm systemd is PID 1, 15 separate units under separate users, and no all-in-one daemon. Run systemd-analyze security for every unit, save the raw output, and report per-unit exposure levels with the correct reading (lower is better). Improve the unit sandboxing until the exposure is as low as feasible, and list what remains permissive and why.
- **R7 Benchmarks**: write or fix bench/METHOD.md. Boot a real Debian 12 minimal VM (same RAM, same virtual hardware, same ready-marker definition) and Lazy at the same RAM. At least 10 runs each, mean and standard deviation, raw outputs saved. Report: the kernel image (compressed against compressed) plus modules, the initramfs and rootfs payload, idle RAM as both used and MemTotal minus MemAvailable, boot time split into kernel and userspace, and package counts from each system's own database. Repeat the LLM measurements at 3072 MB guest RAM with at least 20 prompts and report median and p95. Remove any unsupported figure.
- **R8 Attacks**: grow the suite to at least 120 attacks and 60 benign cases covering every category in S1, run in the booted guest, with the case list and raw results saved. Report the false-block rate. Add 20 attacks written differently from the existing ones (different phrasing, encoding tricks, multi-step) so you are not testing only what the defence was built for.
- **R9 Feature evidence in the guest (FT1 to FT9)**: for each feature, run a scripted scenario inside the booted guest and save raw evidence: the LLM planner; the 40-task suite with the real LLM; dialogue and undo; hardware capabilities (real interface or VM-UNAVAILABLE); web on the local site and one public static page; mail and chat send and receive between local users; the wake-up briefing; chores; the niche feed with citations; voice (synthetic audio); the Terminal app. Fix any feature that does not work now.
- **R10 Hardening**: show the four O5 measures with tests, including a tampered update bundle being rejected, and the planner user failing to read secrets or write policy.
- **R11 Kernel provenance**: show the Buildroot configuration and logs, the kernel source version and the .config, and prove that no host or Ubuntu kernel is referenced anywhere in dist/ or the scripts.
- **R12 Reproducibility**: delete the build outputs, rebuild from a clean clone with one command, compare package manifests and image hashes, and explain differences.
- **R13 Packaging check**: run run-lazy-os.sh and run-wsl.sh. Mark run-windows.ps1 and the VDI and VMDK images UNTESTED unless you can test them. Run qemu-img check on the converted images.
- **R14 Product walkthrough**: write docs/demo/WALKTHROUGH.md (first boot, wizard, wake-up, a delegated task, an approval, undo, mail, browsing, voice, shutdown) with a screendump from the guest display for each step.
- **R15 Regenerate docs/ACCEPTANCE_REPORT.md** from scripts/accept.sh with the restored contract. Statuses: PASS only with fresh evidence, FAIL, BLOCKED (with the human action), UNTESTED. Update docs/BLOCKED.md. Correct every document that contains an unsupported claim and archive the old versions. Tag v3.1-final.
Stop rule: as in V3. Continue until every check is PASS, or BLOCKED or UNTESTED only for human-only reasons.

## 3. FINISH
Print FINAL SUMMARY with: the contract audit result (which criteria had been weakened); the table of VERIFIED, STALE and UNSUPPORTED numbers; the corrected benchmark table; the acceptance counts; the one command to run the product; the screendump list; the human-only items. Begin with R1.
