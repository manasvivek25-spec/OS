NEXT_ACTION: make verify-M1.4

## Current Milestone
M1.4: Brokers fs, sys (systemd D-Bus wrapper plus a fake for tests) and hw (sysfs with an injectable root and fake sysfs fixtures).

## Last 10 Completed Steps
1. Pinned Yocto LTS scarthgap commits in DECISIONS.md.
2. Verified M0.3 QEMU boot test and login status in tests/results/M0.3.log (tag m-M0.3).
3. Implemented lazy-audit hash-chain and verifier, verified M1.1 (tag m-M1.1).
4. Implemented lazy-policy engine, 37 capability manifests, taint tracking, and 162 passing tests with 93% line coverage, verified M1.2 (tag m-M1.2).
5. Designed and implemented snapshot backends (CopyBackend, OverlayBackend, BtrfsBackend) and TreeHasher in src/lazy/tasks/backend.py.
6. Implemented TaskManager checkpointing, transactional commit, cancel rollback, and task undo in src/lazy/tasks/manager.py.
7. Verified rollback to exact pre-task hash upon task cancellation and undo.
8. Validated Task contract compliance against docs/contracts/task.schema.json.
9. Achieved 90% test coverage across lazy.tasks in tests/unit/test_tasks.py.
10. Executed `make verify-M1.3` (16/16 tests passed, logged in tests/results/M1.3.log).

## Open Problems
None.

## Human Actions Pending
None.
