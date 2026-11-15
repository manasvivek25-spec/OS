# Lazy OS v2 Live Demonstration Runbook

This runbook guides evaluators and instructors through booting, exploring, and verifying **Lazy OS v2 Command Center** with real, empirical evidence.

---

## 1. System Requirements & Architecture

- **Host Environment**: Linux / WSL2 (Ubuntu 22.04 or 24.04 recommended)
- **CPU / RAM**: $\ge 2$ vCPUs, $\ge 2.0$ GB free RAM ($\le \frac{1}{2}$ host RAM allocated to VM; default 1024 MB)
- **Virtual Disk**: 256 MB raw GPT image (`build/v2/lazy-disk.img`) with formatted Btrfs partition 3
- **Network Port**: Forwarded host port `8766` to in-guest gateway `8765`
- **Graphical Console**: WSLg / X11 on `DISPLAY=:0` for GTK console (optional; fallback to headless)

---

## 2. Booting Lazy OS v2

Lazy OS provides an operational management script that automatically checks hardware acceleration, memory safety, display availability, and boot status:

```bash
# Boot the operating system (interactive GTK or headless)
./scripts/run-lazy.sh

# Or force headless background mode:
./scripts/run-lazy.sh --headless
```

### Script Execution Profile:
1. Validates kernel `/boot/vmlinuz-6.8.0-149-generic`, initrd `build/v2/lazy-os-boot.cpio.gz`, and disk `build/v2/lazy-disk.img`.
2. Checks KVM hardware acceleration availability (`/dev/kvm`).
3. Launches QEMU with virtio block and virtio network devices, logging PID to `/tmp/lazy-os.pid` and output to `build-logs/qemu.log`.
4. Polls in-guest REST identity endpoint (`http://127.0.0.1:8766/api/identity`) until userspace and gateway are fully operational.
5. Displays access URL: `http://127.0.0.1:8766/`.

To stop the virtual machine:
```bash
./scripts/stop-lazy.sh
```

---

## 3. Automated End-to-End Verification

To execute all 8 canonical demonstration steps automatically and produce machine-verifiable JSON logs:

```bash
python3 scripts/demo-e2e.py
```

Raw test evidence is written to [`docs/demo/demo_e2e_results.json`](file:///c:/Users/len/OS/docs/demo/demo_e2e_results.json).

---

## 4. Manual Interactive Walkthrough (The 8 Canonical Steps)

Open your web browser and navigate to:
**[http://127.0.0.1:8766/](http://127.0.0.1:8766/)**

### Step 1: System Identity & Honest Subsystem Labelling
- **Visual Check**: Look at the Command Center bottom identity footer:
  - System Identity: `lazy-os [6.8.0-149-generic]`
  - Real Mounts: Shows `/dev/vda3` on `/data` with `fstype: btrfs`.
  - Badges: `Kernel: Real (Ubuntu 6.8)` | `Storage: Real (Btrfs)` | `Audit: Real (SHA-256)` | `Snapshots: Real (CoW)` | `LLM: Simulated (Heuristic)` | `Voice: Simulated (Web Speech)`.
- **CLI Proof**:
  ```bash
  curl -s http://127.0.0.1:8766/api/identity | jq .
  curl -s http://127.0.0.1:8766/api/build-info | jq .
  ```

### Step 2: L1 Directive Execution (Note Creation)
- **Visual Check**: In the **AI Command Center** tab (or **Home** quick commands), enter:
  > `create a note called plan.md with a three-item checklist`
- **Behavior**:
  - Intent planner translates text into `doc.create_markdown` capability.
  - Policy engine classifies capability as **L1 (Reversible, low risk)**.
  - Automatic approval is granted with user provenance.
  - Filesystem broker creates `/data/plan.md`.
- **CLI Proof**:
  ```bash
  curl -s http://127.0.0.1:8766/api/fs?path=/data/plan.md | jq .
  ```

### Step 3: L2 Protected Request with User Approval (File Deletion)
- **Visual Check**: In the **File Manager** tab, click the trash icon next to `/data/plan.md`.
- **Behavior**:
  - Policy engine classifies `fs.delete` as **L2 (Irreversible user data mutation)**.
  - The request pauses and emits a slide-out prompt in the **Approvals Drawer**.
  - Click **Approve**.
  - The file is deleted; File Manager refreshes to show the file is removed.
- **CLI Proof**:
  ```bash
  # Returns 404 Not Found after approved deletion
  curl -i http://127.0.0.1:8766/api/fs?path=/data/plan.md
  ```

### Step 4: L2 Request Denied (Safety Invariant)
- **Visual Check**: Request deletion of a sensitive file (e.g. `/data/safe_doc.txt`). When the approval prompt slides out, click **Deny**.
- **Behavior**:
  - The broker aborts execution immediately.
  - A notification toast confirms rejection.
  - The target file remains completely unmodified on the persistent Btrfs partition.

### Step 5: Agent Center & Component Health
- **Visual Check**: Switch to the **Agent Center** tab:
  - Real status cards for all 15 services (`lazy-gateway`, `lazy-planner`, `lazy-policy`, `lazy-tasks`, `lazy-audit`, `lazy-secrets`, `lazy-outbox`, `lazy-broker-fs`, `lazy-broker-sys`, `lazy-broker-hw`, `lazy-broker-web`, `lazy-broker-comms`, `lazy-routines`, `lazy-llm`, `lazy-warmup`).
  - Interactive 5-stage pipeline: `Intent -> Policy (L0-L4) -> Tasks -> Broker -> Audit Ledger`.

### Step 6: System Monitor Live Resource Telemetry
- **Visual Check**: Switch to the **System Monitor** tab:
  - Real-time SVG sparklines displaying CPU %, RAM usage (MB and %), Btrfs disk utilization, and network traffic.
  - Process list sorted by memory consumption directly from guest `/proc`.

### Step 7: Cryptographic Audit Ledger & Tamper Detection
- **Visual Check**: Switch to the **Security Center** tab:
  - View the append-only SHA-256 hash-chained log.
  - Click **Verify Chain**: Evaluates every cryptographic link from the genesis block (`0000...`) to the head.
  - Tamper Simulation: If an attacker modifies an entry or reorders a record, the verification immediately fails and flags the exact record index.

### Step 8: Task Snapshot Undo & Tree Restoration
- **Visual Check**: In the **Security Center** rollback history:
  - Demonstrates instant zero-loss rollback using copy-on-write directory trees and Btrfs snapshots.
  - Mutation erased; directory returns to identical pre-task SHA-256 tree hash.
