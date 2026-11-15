NEXT_ACTION: make verify-M1.5

## Current Milestone
M1.5: lazy-secrets with peer-credential checks. [the planner user cannot read secrets]

## Last 10 Completed Steps
1. Pinned Yocto LTS scarthgap commits in DECISIONS.md.
2. Verified M0.3 QEMU boot test and login status in tests/results/M0.3.log (tag m-M0.3).
3. Implemented lazy-audit hash-chain and verifier, verified M1.1 (tag m-M1.1).
4. Implemented lazy-policy engine, 37 manifests, taint tracking, and 162 passing tests with 93% line coverage (tag m-M1.2).
5. Implemented snapshot backends (Copy, Overlay, Btrfs) and TaskManager checkpointing in src/lazy/tasks/.
6. Verified task cancellation rollback to exact pre-task hash and task undo, verified M1.3 (tag m-M1.3).
7. Implemented BaseBroker abstract dispatch engine in src/lazy/brokers/base.py.
8. Implemented FSBroker covering fs.*, doc.*, code.* operations with path validation in src/lazy/brokers/fs_broker.py.
9. Implemented SysBroker with FakeSystemdClient abstraction in src/lazy/brokers/sys_broker.py.
10. Implemented HWBroker with injectable sysfs fixture support in src/lazy/brokers/hw_broker.py and verified M1.4 (8/8 tests passed, logged in tests/results/M1.4.log).

## Open Problems
None.

## Human Actions Pending
None.
