# Deck Input - Task 2: System Architecture & Frozen Rules (F1-F9)

## Slide Metadata
- **Slide Title**: Privilege Separation & Frozen Security Invariants
- **Topic**: Architectural Foundations & Capability State Machine
- **Time Allocation**: 2 Minutes

---

## Slide Content & Bullets

### 1. Frozen Invariants (Rules F1 to F9)
- **Rule F1**: The planner proposes; policy and brokers decide and execute.
- **Rule F2**: No free-form shell. Only typed, registered capabilities executed via transient sandboxed units.
- **Rule F3**: Untrusted text (web, mail, feeds, documents) is labelled quoted data, never instructions.
- **Rule F4**: Credentials are vault-isolated via Linux `SO_PEERCRED`; unreachable by the planner.
- **Rule F5**: Every task is a cancellable job with a checkpoint snapshot after each step.
- **Rule F6**: Tier L4 (privileged operations, broker internals, keys, audit) is hard-coded forbidden.
- **Rule F7**: Everything is audited with SHA-256 hash chains and undoable.
- **Rule F8**: External sends route strictly through the outbox with verified taint clearance.
- **Rule F9**: Browser runs in an isolated namespace and profile with quarantined downloads.

### 2. Execution Pipeline
```
[User Command] ──> [lazy-gateway] ──> [lazy-planner] ──> [lazy-policy] ──> [lazy-tasks] ──> [Brokers] ──> [lazy-audit]
```

---

## Speaker Talking Points
1. "The architecture separates the brain from the hands. The LLM planner is completely unprivileged: it has no network access, no shell access, and cannot execute commands directly."
2. "Notice Rule F3: any content fetched from the web or email is stripped and wrapped as quoted untrusted data before reaching the planner. This structurally defeats prompt injection attacks."
3. "All inter-process communication takes place over local Unix domain sockets in `/run/lazy/` with JSON-RPC 2.0, eliminating TCP network attack surfaces."

---

## Evidence & Verification References
- [docs/ARCHITECTURE.md](file:///c:/Users/len/OS/docs/ARCHITECTURE.md): Full component and pipeline diagrams.
- [src/lazy/policy/engine.py](file:///c:/Users/len/OS/src/lazy/policy/engine.py): Implementation of Rule F1, F4, F6, and F8.
- [tests/results/M1.2.log](file:///c:/Users/len/OS/tests/results/M1.2.log): 162/162 policy unit tests passing (93% coverage).
- [tests/results/M3.5.log](file:///c:/Users/len/OS/tests/results/M3.5.log): Systemd sandboxing unit audit (10.0/10.0 hardening score).
