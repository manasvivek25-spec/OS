NEXT_ACTION: make verify-M0.3

## Current Milestone
M0.3: Yocto bootstrap: record release and layer commits in DECISIONS.md; kas files; a minimal image boots in QEMU with ssh.

## Last 10 Completed Steps
1. Initialized git repository on main branch in workspace root.
2. Created complete directory layout per section 3 specification.
3. Created docs/BUILD_PROMPT.md and docs/SPEC.md verbatim.
4. Created docs/PLAN.md, docs/STATE.md, docs/DECISIONS.md, docs/ASSUMPTIONS.md, docs/KNOWN_ISSUES.md, docs/LICENCES.md, docs/PACKAGES.md, docs/ARCHITECTURE.md, docs/HARDWARE-CONTROL.md.
5. Implemented scripts/check-env.sh and Makefile.
6. Executed `make verify-M0.1` and committed M0.1 (tag m-M0.1).
7. Authored JSON Schemas for Intent, Plan, Decision, Event, Task, OutboxItem, and CapabilityManifest.
8. Implemented contract validation engine and CLI in src/lazy/common/contracts.py with offline schema store and ISO datetime checker.
9. Generated 31 valid and 31 invalid sample fixtures across all contract types.
10. Executed `make verify-M0.2` (all 6 tests passed, logged in tests/results/M0.2.log).

## Open Problems
None.

## Human Actions Pending
None.
