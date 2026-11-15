NEXT_ACTION: make verify-M2.1

## Current Milestone
M2.1: Planner interface, mock mode, recorded-intent fixtures for every capability.

## Last 10 Completed Steps
1. Implemented snapshot backends (Copy, Overlay, Btrfs) and TaskManager in src/lazy/tasks/.
2. Verified task cancellation rollback to exact pre-task hash and undo, verified M1.3 (tag m-M1.3).
3. Implemented FSBroker covering fs.*, doc.*, code.* operations in src/lazy/brokers/fs_broker.py.
4. Implemented SysBroker with FakeSystemdClient abstraction in src/lazy/brokers/sys_broker.py.
5. Implemented HWBroker with injectable sysfs fixture support in src/lazy/brokers/hw_broker.py.
6. Verified all 22 broker capabilities with automated tests in tests/unit/test_brokers.py (tag m-M1.4).
7. Designed and implemented SecretVault with peer-credential enforcement and 0700 permissions in src/lazy/secrets/vault.py.
8. Implemented SecretsService Unix domain socket server with Linux SO_PEERCRED inspection in src/lazy/secrets/service.py.
9. Proved negative security assertion: planner user is strictly rejected from reading secrets (Rule F4) in tests/unit/test_secrets.py, verified M1.5 (tag m-M1.5).
10. Built lazy-gateway: HUDTokenManager with constant-time verification, RPCBus JSON-RPC 2.0 router, RFC 6455 WebSocket protocol server, verified M1.6 with 21 unit tests (tag m-M1.6).

## Open Problems
None.

## Human Actions Pending
None.
