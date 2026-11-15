NEXT_ACTION: make verify-M1.3

## Current Milestone
M1.3: lazy-tasks: snapshot backends (btrfs, overlay, copy) and undo. [discard returns the tree to its pre-task hash; commit persists; cancel mid-task works]

## Last 10 Completed Steps
1. Pinned Yocto LTS scarthgap commits in DECISIONS.md.
2. Verified M0.3 QEMU boot test and login status in tests/results/M0.3.log (tag m-M0.3).
3. Implemented lazy-audit hash-chain and verifier, verified M1.1 (tag m-M1.1).
4. Authored all 37 capability YAML manifests in config/capabilities/ conforming to capability_manifest.schema.json.
5. Implemented manifest loader and validator in src/lazy/policy/manifest.py.
6. Implemented taint tracking and Rule F4/F8 protection in src/lazy/policy/taint.py.
7. Implemented sliding-window rate limiter in src/lazy/policy/rate_limiter.py.
8. Implemented approval state machine with voice rejection for L3 in src/lazy/policy/state_machine.py.
9. Implemented core PolicyEngine with hardcoded L4 denylist in src/lazy/policy/engine.py.
10. Executed `make verify-M1.2` (162/162 tests passed, 93% line coverage, logged in tests/results/M1.2.log).

## Open Problems
None.

## Human Actions Pending
None.
