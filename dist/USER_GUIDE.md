# Lazy OS v3 User Guide & Manual

Welcome to **Lazy OS**, a custom autonomous operating system designed to give users supervisory control while the OS performs tasks: creating files and documents, running software tools, managing services and processes, controlling hardware, sandboxed web browsing, local mail, and terminal operations.

---

## 1. Quick Start: Booting the Operating System

Lazy OS is packaged to run in a standalone virtual machine or bare-metal environment with a single command.

### Launching on Linux / WSL2
```bash
# Graphical display mode (WSLg / X11 / Wayland)
./dist/run-lazy-os.sh

# Headless / background daemon mode (HUD accessible via browser)
./dist/run-lazy-os.sh --headless
```

### Launching on Windows PowerShell
```powershell
.\dist\run-windows.ps1
```

Once booted, the **Command Center** graphical interface opens automatically in the guest window, or at `http://127.0.0.1:8766/` when running in headless mode.

To cleanly shut down the virtual machine:
```bash
./scripts/stop-lazy.sh
```

---

## 2. Navigating the Command Center

The Command Center provides a unified, desktop-like dashboard split into 11 specialized views accessible via the sidebar or the global search bar (**Ctrl+K**):

1. **Home & Briefing**: Displays the daily wake-up card, system health metrics, recent tasks, and quick directives.
2. **AI Command Center**: The primary natural-language interaction console. Type requests, view streaming plans step-by-step, review inline approval requests, and trigger zero-loss task undo.
3. **System Monitor**: Live SVG sparklines showing real-time CPU, RAM, Disk, and Network telemetry alongside the runtime status of all 15 Lazy OS microservices.
4. **Agent Center**: Real-time event activity monitor and animated 5-stage execution pipeline (Input $\to$ Gateway $\to$ Policy $\to$ Broker $\to$ Audit).
5. **File Manager**: Interactive explorer for the persistent Btrfs `/data` partition. Browse folders, create files, view/edit text documents, and delete files (governed by Tier L2 approvals).
6. **Security Center**: Interactive security management hub. Displays the capability tier matrix (L0–L4), pending approval queue, and a cryptographic **Verify Chain** button that inspects the SHA-256 audit ledger for tampering.
7. **App Launcher**: Tile grid of registered system applications (Markdown Notes, System Briefing, Mail Outbox, Terminal, and Settings).
8. **Settings**: Customize the Command Center theme (Cyan, Emerald, Amber, Violet), enable the **Reduced Motion** accessibility mode, adjust planner model parameters, and view guest build provenance.
9. **Terminal**: Interactive shell terminal operating under the unprivileged `lazy` user account for human tasks. (Rule F2: The AI agent is strictly barred from spawning arbitrary shells).
10. **Browser**: Isolated browser client for allowlisted web navigation and form processing.
11. **Help & Documentation**: On-screen guide detailing capability tiers, rollback safety, and keyboard shortcuts.

---

## 3. Security Architecture: Capability Tiers & Approvals

Lazy OS operates on strict capability-based authorization. Every action requested by the user or proposed by the planner is categorized into one of five tiers:

| Tier | Name | Description | Example Operations |
| :---: | :--- | :--- | :--- |
| **L0** | **Read-Only** | Information queries with zero state mutation. Auto-permitted. | `fs.read`, `sys.service_status`, `hw.usb_list`, `mail.list` |
| **L1** | **Low-Risk** | Standard constructive actions with automatic execution. | `fs.write`, `doc.create_markdown`, `hw.backlight_set`, `mail.draft` |
| **L2** | **Supervised** | Potentially destructive actions requiring interactive user approval. | `fs.delete`, `code.run`, `sys.service_restart`, `hw.rfkill_set` |
| **L3** | **Hazardous** | Irreversible external communications held in the Outbox delay window. | `mail.send`, `chat.send`, `web.submit`, `web.download` |
| **L4** | **Forbidden** | Administrative core invariants. Unconditionally rejected. | Direct policy edits, audit ledger modification, raw credential access |

### Approving or Rejecting L2/L3 Actions
When an action requires confirmation:
1. The **Approvals Drawer** slides open with an amber badge indicating the requested capability, target path, and reason.
2. Click **Approve** to execute the action, or **Deny** to discard it.
3. Denied requests produce zero filesystem or system changes.

---

## 4. Transactional Rollback & Undo

Lazy OS guarantees state integrity through transactional checkpoints:
- Every state-changing task automatically creates a copy-on-write snapshot on `/data`.
- If an operation fails, is interrupted, or produces undesirable output, clicking **Undo Task** in the AI Command Center or Security Center instantly rolls back the directory tree to its exact pre-task cryptographic hash.
- Data on `/data` is backed by a dedicated Btrfs partition and persists across virtual machine reboots.

---

## 5. Offline Operation & Hardware Integration

- **Offline by Default**: Lazy OS does not require internet connectivity to boot, plan, or execute local system administration tasks.
- **Hardware Integration**: System volume, Wi-Fi radio (rfkill), and USB devices are mapped directly to Linux kernel subsystem interfaces. On virtual machines, interfaces lacking hypervisor hardware emulation (e.g. laptop backlight or battery) are transparently labeled `VM-UNAVAILABLE` and can be validated on bare-metal hardware via `scripts/hw-selftest.sh`.

---

## 6. Keyboard Shortcuts

- `Ctrl + K`: Open Command Bar search dialog.
- `Escape`: Close active modal or drawer.
- `Tab` / `Shift + Tab`: Navigate interface controls with high-visibility focus indicators.
