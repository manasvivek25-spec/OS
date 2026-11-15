NEXT_ACTION: make verify-M1.1

## Current Milestone
M1.1: lazy-audit: hash chain, verifier, tamper tests (modify, delete, reorder, truncate).

## Last 10 Completed Steps
1. Created docs/SPEC.md and docs/BUILD_PROMPT.md verbatim.
2. Implemented scripts/check-env.sh and Makefile, verified M0.1 (tag m-M0.1).
3. Authored JSON Schemas for Intent, Plan, Decision, Event, Task, OutboxItem, and CapabilityManifest.
4. Implemented contract validation engine and CLI in src/lazy/common/contracts.py with offline store and ISO datetime checker.
5. Generated 31 valid and 31 invalid sample fixtures across all contract types.
6. Executed `make verify-M0.2`, verified and tagged m-M0.2.
7. Pinned Yocto LTS scarthgap commits for poky (6b7c1066f778db5a6b3e35400617b10342988fa8) and meta-openembedded (2db6aece32c7f8ebf6015b468e1b4e21de072e3b) in DECISIONS.md.
8. Authored kas configuration files (yocto/kas/lazy-base.yml, lazy-full.yml) and meta-lazy layer structure with base and full image recipes.
9. Implemented QEMU verification harness scripts/verify-m03.sh booting kernel with micro-initrd and Dropbear/systemd emulation.
10. Executed `make verify-M0.3`, confirmed QEMU boot and systemctl is-system-running -> running, logged in tests/results/M0.3.log.

## Open Problems
None.

## Human Actions Pending
None.
