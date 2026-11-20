# Lazy OS Gateway API & WebSocket Streaming Contract
**Version:** 4.0.0-qemu  
**Status:** FROZEN  
**Target Architecture:** Zero-Trust Edge ML Inference Appliance (Track A)  
**Assigned Roles:** Role A (Provider / Backend / Core OS) & Role B (Consumer / Edge ML / HUD)  

---

## 1. REST Endpoints

### 1.1 `GET /api/metrics`
Retrieves live system telemetry calculated from kernel `/proc` filesystem entries and real storage stats. No hardcoded or static figures.

- **Request:**
  ```http
  GET /api/metrics HTTP/1.1
  Host: 127.0.0.1:8765
  Accept: application/json
  ```
- **Response (200 OK):**
  ```json
  {
    "cpu_percent": 12.4,
    "memory": {
      "used_mb": 512.4,
      "total_mb": 4096.0,
      "percent": 12.5
    },
    "disk": {
      "used_mb": 184.2,
      "total_mb": 4096.0,
      "percent": 4.5
    },
    "network": {
      "rx_kb": 342.1,
      "tx_kb": 128.6
    }
  }
  ```
- **Field Definitions:**
  - `cpu_percent` (`float`): Percentage of CPU utilized across all cores derived from consecutive `/proc/stat` samples.
  - `memory.used_mb` (`float`): Real active memory consumption computed from `/proc/meminfo` (`MemTotal - MemAvailable`).
  - `memory.total_mb` (`float`): Total physical memory reported by `/proc/meminfo`.
  - `memory.percent` (`float`): Ratio `(used_mb / total_mb) * 100`.
  - `disk.used_mb` (`float`): Disk usage computed via `os.statvfs` on `/data`.
  - `disk.total_mb` (`float`): Disk capacity on `/data`.
  - `disk.percent` (`float`): Disk usage percentage on `/data`.
  - `network.rx_kb` (`float`): Total received kilobytes accumulated on network interfaces (`/proc/net/dev`).
  - `network.tx_kb` (`float`): Total transmitted kilobytes accumulated on network interfaces (`/proc/net/dev`).

---

### 1.2 `GET /api/services`
Retrieves the real-time operational status of all 15 sandboxed `lazy-*` unprivileged systemd units.

- **Request:**
  ```http
  GET /api/services HTTP/1.1
  Host: 127.0.0.1:8765
  Accept: application/json
  ```
- **Response (200 OK):**
  ```json
  [
    {
      "unit": "lazy-gateway.service",
      "status": "running",
      "active_state": "active",
      "sub_state": "running",
      "slice": "/lazy-interactive.slice",
      "desc": "Central Gateway & Command Center"
    },
    {
      "unit": "lazy-planner.service",
      "status": "running",
      "active_state": "active",
      "sub_state": "running",
      "slice": "/lazy-interactive.slice",
      "desc": "Intent Decomposition & Planning Engine"
    },
    {
      "unit": "lazy-policy.service",
      "status": "running",
      "active_state": "active",
      "sub_state": "running",
      "slice": "/lazy-interactive.slice",
      "desc": "Tiered Capability Broker (L0-L4)"
    },
    {
      "unit": "lazy-tasks.service",
      "status": "running",
      "active_state": "active",
      "sub_state": "running",
      "slice": "/lazy-interactive.slice",
      "desc": "Task Lifecycle & Snapshot Rollback"
    },
    {
      "unit": "lazy-audit.service",
      "status": "running",
      "active_state": "active",
      "sub_state": "running",
      "slice": "/lazy-interactive.slice",
      "desc": "Cryptographic Hash-Chained Audit Ledger"
    },
    {
      "unit": "lazy-secrets.service",
      "status": "running",
      "active_state": "active",
      "sub_state": "running",
      "slice": "/lazy-interactive.slice",
      "desc": "Isolated Credential Vault"
    },
    {
      "unit": "lazy-outbox.service",
      "status": "running",
      "active_state": "active",
      "sub_state": "running",
      "slice": "/lazy-interactive.slice",
      "desc": "Outbox Hold and Approval Queue"
    },
    {
      "unit": "lazy-broker-fs.service",
      "status": "running",
      "active_state": "active",
      "sub_state": "running",
      "slice": "/lazy-interactive.slice",
      "desc": "Sandboxed Filesystem Broker"
    },
    {
      "unit": "lazy-broker-sys.service",
      "status": "running",
      "active_state": "active",
      "sub_state": "running",
      "slice": "/lazy-interactive.slice",
      "desc": "Systemd & Process Broker"
    },
    {
      "unit": "lazy-broker-hw.service",
      "status": "running",
      "active_state": "active",
      "sub_state": "running",
      "slice": "/lazy-interactive.slice",
      "desc": "Hardware & Sysfs Broker"
    },
    {
      "unit": "lazy-broker-web.service",
      "status": "running",
      "active_state": "active",
      "sub_state": "running",
      "slice": "/lazy-interactive.slice",
      "desc": "Sandboxed Web Browser Broker"
    },
    {
      "unit": "lazy-broker-comms.service",
      "status": "running",
      "active_state": "active",
      "sub_state": "running",
      "slice": "/lazy-interactive.slice",
      "desc": "Communications & Mail Broker"
    },
    {
      "unit": "lazy-routines.service",
      "status": "running",
      "active_state": "active",
      "sub_state": "running",
      "slice": "/lazy-interactive.slice",
      "desc": "Routines, Chores & Niche Feed"
    },
    {
      "unit": "lazy-llm.service",
      "status": "running",
      "active_state": "active",
      "sub_state": "running",
      "slice": "/lazy-interactive.slice",
      "desc": "Local LLM Resident Engine (Qwen2.5-1.5B-Instruct)"
    },
    {
      "unit": "lazy-warmup.service",
      "status": "exited",
      "active_state": "inactive",
      "sub_state": "dead",
      "slice": "/lazy-interactive.slice",
      "desc": "Weights Lock & Cgroup Preloader"
    }
  ]
  ```
- **Field Definitions:**
  - `unit` (`string`): Full systemd unit name.
  - `status` (`string`): Simplified health string (`"running"`, `"exited"`, `"failed"`, `"inactive"`, `"unavailable"`).
  - `active_state` (`string`): Direct `ActiveState` property from `systemctl is-active`.
  - `sub_state` (`string`): Direct `SubState` property from systemd introspection.
  - `slice` (`string`): Cgroup slice where the unit runs.
  - `desc` (`string`): Human-readable capability description.

---

### 1.3 `GET /api/briefing`
Returns dynamic wake-up briefing assembled from live task files (`/data/tasks.md`), chore execution logs (`/var/log/lazy-chores.log`), and local feed updates.

- **Request:**
  ```http
  GET /api/briefing HTTP/1.1
  Host: 127.0.0.1:8765
  Accept: application/json
  ```
- **Response (200 OK):**
  ```json
  {
    "title": "Lazy OS Daily Briefing",
    "date": "Friday, November 20, 2026",
    "status": "All systems nominal. 14 sandboxed units active.",
    "tasks_pending": [
      {"id": "t-001", "task": "Review daily system security hash chain", "priority": "high"},
      {"id": "t-002", "task": "Verify Qwen 1.5B edge inference benchmarks", "priority": "medium"}
    ],
    "overnight_chores": [
      {"chore": "Quarantine Scrubber", "result": "Cleaned 0 expired objects", "timestamp": "2026-11-20T04:00:00Z"},
      {"chore": "Audit Ledger Checksum", "result": "100% verified (chain valid)", "timestamp": "2026-11-20T04:05:00Z"},
      {"chore": "Log Rotation", "result": "Rotated /var/log/lazy-audit.log", "timestamp": "2026-11-20T04:10:00Z"}
    ],
    "niche_feed": [
      {"title": "Linux 6.6.21 Virtio-GPU Acceleration", "source": "Kernel.org", "relevance": 0.96},
      {"title": "Zero-Trust Sandboxing with systemd slices", "source": "LWN.net", "relevance": 0.91}
    ]
  }
  ```

---

### 1.4 `POST /api/tasks/undo`
Initiates an immediate rollback of the last state-mutating task by restoring its pre-execution Btrfs snapshot, updating the task ledger, and recording a cryptographically verified receipt into the audit log.

- **Request:**
  ```http
  POST /api/tasks/undo HTTP/1.1
  Host: 127.0.0.1:8765
  Content-Type: application/json

  {
    "task_id": "task-001"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "success": true,
    "task_id": "task-001",
    "status": "rolled_back",
    "snapshot_restored": "snap-task-001-pre",
    "rolled_back_at": "2026-11-20T21:45:00Z",
    "audit_entry_id": 482,
    "chain_hash": "a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0"
  }
  ```
- **Error Response (400 Bad Request / 404 Not Found):**
  ```json
  {
    "success": false,
    "error": "No rollback snapshot available for task 'task-001'"
  }
  ```

---

### 1.5 `POST /api/command`
Submits a natural language or structured command for processing through the Zero-Trust execution pipeline (`lazy-planner` -> `lazy-policy` -> `lazy-tasks` -> `brokers` -> `lazy-audit`). The AI never receives a raw shell.

- **Request:**
  ```http
  POST /api/command HTTP/1.1
  Host: 127.0.0.1:8765
  Content-Type: application/json

  {
    "prompt": "write a one-page document about edge computing advantages",
    "session_id": "sess-default",
    "interactive": false
  }
  ```
- **Response (200 OK or 202 Accepted):**
  ```json
  {
    "task_id": "t-1732135600",
    "status": "executing",
    "intent": {
      "capability": "fs.file_write",
      "policy_tier": "L1",
      "target_path": "/data/Documents/edge_computing_advantages.md"
    },
    "requires_approval": false,
    "message": "Task queued and executing via fs_broker"
  }
  ```

---

## 2. WebSocket Streaming Protocol (`CONFIG.wsUrl`)

WebSocket connection provides low-latency, bidirectional streaming for real-time AI token streaming, GBNF action planning, policy approval gating, and execution telemetry.

### 2.1 Connection & Handshake
- **URL:** `ws://127.0.0.1:8765/?token=<session_token>` or via initial auth frame.
- **Client Auth Frame:**
  ```json
  {
    "type": "auth",
    "payload": {
      "token": "lazy-token-default"
    }
  }
  ```
- **Server Auth Confirmation:**
  ```json
  {
    "type": "auth_ok",
    "payload": {
      "session_id": "sess-9a8b7c6d",
      "model": "Qwen2.5-1.5B-Instruct-Q4_K_M",
      "inference_engine": "llama.cpp",
      "policy_tiers_active": ["L0", "L1", "L2", "L3", "L4"]
    }
  }
  ```

---

### 2.2 User Directives / Commands
- **Client Frame (`type: "user_input"`):**
  ```json
  {
    "type": "user_input",
    "payload": {
      "text": "write a summary of system architecture in /data/Documents/summary.md",
      "mode": "document"
    }
  }
  ```

---

### 2.3 Live Token Streaming Chunks (`type: "token_stream"`)
Emitted as the local LLM generates tokens in real time.
- **Server Frame:**
  ```json
  {
    "type": "token_stream",
    "payload": {
      "task_id": "t-1732135600",
      "chunk": "Edge computing provides ",
      "index": 1,
      "model": "Qwen2.5-1.5B-Instruct-Q4_K_M",
      "tokens_per_second": 32.4
    }
  }
  ```

---

### 2.4 Structured Plan Proposal (`type: "plan_proposal"`)
Emitted when `lazy-planner` parses user intent with GBNF grammar constraints into a structured plan conforming to capability schemas.
- **Server Frame:**
  ```json
  {
    "type": "plan_proposal",
    "payload": {
      "task_id": "t-1732135600",
      "intent_id": "i-9821",
      "capability": "fs.file_write",
      "policy_tier": "L1",
      "params": {
        "path": "/data/Documents/summary.md",
        "content_length": 1420
      },
      "risk_level": "low",
      "requires_approval": false
    }
  }
  ```

---

### 2.5 Policy Tier Status (`type: "policy_eval"`)
Evaluates the plan against `lazy-policy` capability manifests and taint tracking rules.
- **Server Frame:**
  ```json
  {
    "type": "policy_eval",
    "payload": {
      "intent_id": "i-9821",
      "verdict": "allow",
      "tier": "L1",
      "taint_level": "clean",
      "reason": "Whitelisted capability within user data partition"
    }
  }
  ```

---

### 2.6 Pending Approval Gating (`type: "approval_required"` & `type: "approval_response"`)
For actions classified as L2 (reversible system modifications) or L3 (irreversible mutations/comms):
- **Server Frame (`type: "approval_required"`):**
  ```json
  {
    "type": "approval_required",
    "payload": {
      "approval_id": "appr-0492",
      "task_id": "t-1732135601",
      "capability": "fs.file_delete",
      "policy_tier": "L2",
      "description": "Delete existing file '/data/Documents/old_report.md'",
      "params": {
        "path": "/data/Documents/old_report.md"
      }
    }
  }
  ```
- **Client Frame (`type: "approval_response"`):**
  ```json
  {
    "type": "approval_response",
    "payload": {
      "approval_id": "appr-0492",
      "approved": true
    }
  }
  ```

---

### 2.7 Execution Receipt & Audit Lock (`type: "task_receipt"`)
Emitted upon task completion or failure. Confirms hash-chained audit logging and snapshot availability.
- **Server Frame:**
  ```json
  {
    "type": "task_receipt",
    "payload": {
      "task_id": "t-1732135600",
      "status": "completed",
      "capability": "fs.file_write",
      "target": "/data/Documents/summary.md",
      "btrfs_snapshot_id": "snap-t-1732135600",
      "rollback_available": true,
      "audit_entry_id": 512,
      "chain_hash": "c4d5e6f7890123456789abcdef0123456789abcdef0123456789abcdef012345",
      "execution_time_ms": 142.5
    }
  }
  ```

---

## 3. Conformance Verification
Both Role A (gateway implementation) and Role B (HUD & LLM integration) must adhere strictly to these schemas. Any field omitting actual runtime values must explicitly return `"unavailable"` rather than empty, mock, or hardcoded constants.
