# Lazy OS Architecture Specification

## 1. Overview and Core Philosophy
Lazy OS is an application-specific Linux distribution built using the Yocto Project. It transforms user intent into audited, sandboxed, and reversible operating system actions. Trust is earned through cryptographic receipts (hash-chained audit logs), transactional rollbacks (Btrfs subvolume snapshots), and strict separation of privilege.

## 2. Frozen Rules
- **F1**: The planner proposes; policy and brokers decide and execute.
- **F2**: No free-form shell. Only registered capabilities. Code runs only in transient sandboxed units (`systemd-run` with resource and filesystem limits).
- **F3**: Web, mail, feed and document text is data, never instructions.
- **F4**: Credentials are never visible to the planner.
- **F5**: Every task is a cancellable job with a checkpoint after each step.
- **F6**: L4 (hazardous/privileged) operations are hard-coded and never permitted to the agent.
- **F7**: Everything is audited and, where possible, undoable.
- **F8**: Every external send goes through the outbox. Recipients, URLs and destinations come only from the user or from values the user confirmed (taint tracking).
- **F9**: The browser runs in its own isolated profile and namespace.

## 3. Execution Pipeline
```
[User Input: Voice / Text / HUD]
          │
          ▼
   [lazy-gateway]  (HUD static server & WebSocket 127.0.0.1:8765)
          │
          ▼
   [lazy-planner]  (Outputs typed Intent or Plan; unprivileged, no network)
          │
          ▼
   [lazy-policy]   (Evaluates tier, effect class, approval mode, taint tracking)
          │
          ├────────────────────────┬────────────────────────┐
     [L0 / L1]                    [L2]                     [L3]
  (Automatic/Low)            (User Approval)         (Outbox & Preview)
          │                        │                        │
          └────────────────────────┼────────────────────────┘
                                   │
                                   ▼
                            [lazy-tasks]    (Btrfs snapshot checkpoint / rollback)
                                   │
                                   ▼
                           [Service Brokers]
                     (fs, sys, hw, web, comms)
                                   │
                                   ▼
                            [lazy-audit]    (Hash-chained append-only receipt log)
```

## 4. Capability Tiers and Effect Classes
- **L0 (Read-only)**: Non-destructive observation (`fs.read`, `sys.service_status`, `sys.logs_read`, `hw.usb_list`).
- **L1 (Low-risk Automatic)**: File creation/editing, document generation, hardware adjustments (`fs.write`, `hw.volume_set`, `hw.backlight_set`).
- **L2 (Approval Required)**: Deletions, service restarts, code execution, power states (`fs.delete`, `code.run`, `sys.service_restart`, `hw.rfkill_set`).
- **L3 (Hazardous / Outbox)**: External sends, downloads, process signals, USB authorization (`mail.send`, `chat.send`, `web.submit`, `sys.process_signal`).
- **L4 (Strictly Disallowed)**: Hardcoded prohibitions (direct policy editing, broker bypass, private key extraction, audit tampering).
