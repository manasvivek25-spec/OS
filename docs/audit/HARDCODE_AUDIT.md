# Lazy OS Hardcode & Kiosk Audit Report (W1)
**Generated**: 2026-11-20  
**Audit Scope**: Kiosk Startup Path, `hud/`, `src/lazy/gateway/`, `src/lazy/planner/`, `src/lazy/llm/`  
**Standard**: Rule H1 ("No hardcoding. Every UI element reads real guest data, or shows 'unavailable'") & Rule H2 ("No mock planner in the image, in acceptance checks or in demos")

---

## 1. Kiosk Startup Path & What The Display Loads

* **Kiosk Service**: `/etc/systemd/system/lazy-kiosk.service`
  - `ExecStart`: `/usr/bin/cage -s -- /usr/bin/cog --platform=wl http://127.0.0.1:8765`
  - `Environment`: `XDG_RUNTIME_DIR=/run/kiosk`, `WLR_RENDERER=pixman`, `WLR_BACKENDS=drm,libinput`, `CAGE_OUTPUT_MODE=1920x1080`
* **Underlying Gateway Service**: `/etc/systemd/system/lazy-gateway.service`
  - `ExecStart`: `/usr/bin/python3 -m lazy.gateway.server --host 0.0.0.0 --port 8765`
  - `User`: `lazy-gw` / `Group`: `lazy-gw`
  - `Working Directory`: `/var/lib/lazy`
* **Root URL Loaded**: `http://127.0.0.1:8765/`
  - Serves static assets from `/usr/share/lazy/hud/` (or repository `hud/`):
    - `index.html` (21.4 KB)
    - `hud.css` (16.2 KB)
    - `hud.js` (24.8 KB)
* **Static Images & Visual Assets**:
  - Zero external raster images (no `.png` or `.jpg` dependencies at runtime).
  - All icons are Unicode glyphs (e.g., `⚡`, `🌐`, `🔔`, `🏠`, `🤖`, `📊`, `📁`, `🔒`, `🚀`, `⚙️`).
  - Charts are dynamically generated SVG `<path>` elements (`spark-cpu`, `spark-ram`, `spark-disk`, `spark-net`).
* **WebSocket Connection**:
  - `CONFIG.wsUrl` is defined in `hud.js:17`, but **no WebSocket client is ever instantiated** (`new WebSocket` is completely absent in `hud.js`). All interactions run via HTTP `fetch()` or pure client-side JavaScript.

---

## 2. Exhaustive UI Element Audit (`hud/` & `src/lazy/gateway/`)

| UI Component / Element | Element ID / Selector | Stated Purpose | Actual Data Source | Source Category | File & Line |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Boot Overlay Progress** | `#boot-progress` | Boot initialization bar | Dummy timer loop (`progress += 25` every 400ms) | **Fixture** | `hud/hud.js:86-96` |
| **Boot Overlay Status** | `#boot-status` | Subsystem boot status text | Hardcoded array of 5 strings (`stages`) | **Fixture** | `hud/hud.js:78-84` |
| **Header Power Profile** | `#val-power` | Hardware power governor | Static literal text `"balanced"` | **Hardcoded** | `hud/index.html:39` |
| **Header Network State** | `#val-net` | Active interface state | Static literal text `"connected"` | **Hardcoded** | `hud/index.html:43` |
| **Header Pending Approvals**| `#badge-alerts` | Unresolved L2/L3 approvals | `fetchApprovals()` reading `/api/approvals` | **Real** (API backed) | `hud/hud.js:470` |
| **Header Clock** | `#clock-display` | Real-time system clock | Client JavaScript `new Date().toISOString()` | **Real** (Client JS) | `hud/hud.js:116-121` |
| **Briefing Date** | `#briefing-date` | Morning briefing date | `/api/briefing` (`b.date` via `time.strftime`) | **Real** (Host time) | `src/lazy/gateway/api.py:389` |
| **Briefing Headline** | `#briefing-headline` | Security & chores summary | Hardcoded literal `"All systems nominal. Zero security alerts."` | **Hardcoded** | `src/lazy/gateway/api.py:390` |
| **Briefing Overnight Chore 1**| `#briefing-chores` (li:1)| Quarantine status | Hardcoded literal `{"chore": "Quarantine Scrubber", "result": "Cleaned 0 expired objects"}` | **Hardcoded** | `src/lazy/gateway/api.py:392` |
| **Briefing Overnight Chore 2**| `#briefing-chores` (li:2)| Audit checksum status | Hardcoded literal `{"chore": "Audit Ledger Checksum", "result": "100% verified (chain valid)"}` | **Hardcoded** | `src/lazy/gateway/api.py:393` |
| **Briefing Overnight Chore 3**| `#briefing-chores` (li:3)| Log rotation status | Hardcoded literal `{"chore": "Log Rotation", "result": "Rotated /var/log/lazy-audit.log"}` | **Hardcoded** | `src/lazy/gateway/api.py:394` |
| **Briefing Feed Item 1** | `#briefing-feed` (li:1) | Curated tech feed item | Hardcoded literal `{"title": "Linux 6.8 Memory Management Enhancements", "source": "LWN.net"}` | **Hardcoded** | `src/lazy/gateway/api.py:397` |
| **Briefing Feed Item 2** | `#briefing-feed` (li:2) | Curated tech feed item | Hardcoded literal `{"title": "Embedded Systemd Slicing Architectures", "source": "Kernel.org"}` | **Hardcoded** | `src/lazy/gateway/api.py:398` |
| **Home Health CPU** | `#home-cpu` | Live CPU percentage | Hardcoded literal `4.2` returned by `/api/metrics` | **Hardcoded** | `src/lazy/gateway/api.py:211` |
| **Home Health RAM** | `#home-ram` | Memory utilization in MB | Reads `/proc/meminfo` (falls back to `68.5`) | **Real** (with fallback) | `src/lazy/gateway/api.py:201-208` |
| **Home Health Disk** | `#home-disk` | `/data` Btrfs storage used | Hardcoded literal `5.8` MB returned by `/api/metrics` | **Hardcoded** | `src/lazy/gateway/api.py:213` |
| **Quick Action Buttons** | `.btn-action` | Shortcut action triggers | Hardcoded `data-directive` attributes | **Fixture** | `hud/index.html:136-139` |
| **AI Planner Badge** | `#badge-planner-mode` | Active inference planner | Static HTML `<span class="badge-pill sim">MOCK PLANNER</span>` | **Hardcoded** | `hud/index.html:151` |
| **AI Directive "note/create"**| `#chat-transcript` | Natural language document | Hardcoded client-side JS substring match writing canned `# Execution Plan` | **Hardcoded** | `hud/hud.js:553-561` |
| **AI Directive "service"** | `#chat-transcript` | Natural language status | Hardcoded client string `"Queried sys.service_status: 15/15 units active..."` | **Hardcoded** | `hud/hud.js:562-566` |
| **AI Directive "audit"** | `#chat-transcript` | Natural language verify | Client substring match calling `POST /api/audit/verify` | **Real** (API backed) | `hud/hud.js:567-573` |
| **AI Directive "other"** | `#chat-transcript` | Fallback agent reply | Hardcoded client string `"Directive received... Evaluated by L1 policy gate."` | **Hardcoded** | `hud/hud.js:574-578` |
| **AI Undo Link** | `undoLastTask()` | Task state reversion | Hardcoded client JS string alert; does not invoke `TaskManager.rollback` | **Hardcoded** | `hud/hud.js:599-602` |
| **Plan Breakdown Stream** | `#plan-stream-box` | Live intent step stream | Dead HTML block (`display:none`); never written by JS | **Unused/Stub** | `hud/index.html:164-171` |
| **Voice Button** | `#btn-voice-speech` | Speech recognition trigger | Static HTML button with no event listener attached | **Unused/Stub** | `hud/index.html:175` |
| **System Monitor CPU Val** | `#sys-cpu-val` | Live CPU percentage | Hardcoded literal `4.2` returned by `/api/metrics` | **Hardcoded** | `src/lazy/gateway/api.py:211` |
| **System Monitor CPU Spark** | `#spark-cpu` | CPU history graph | Initialized with hardcoded array `[4, 5, 4, 6, 8, 5, 4, 7, 5, 4]` | **Hardcoded** | `hud/hud.js:25` |
| **System Monitor RAM Val** | `#sys-ram-val` | Live RAM in MB | Reads `/proc/meminfo` | **Real** | `src/lazy/gateway/api.py:201-208` |
| **System Monitor RAM Spark** | `#spark-ram` | RAM history graph | Initialized with hardcoded array `[68, 68, 69, ...]` | **Fixture** | `hud/hud.js:26` |
| **System Monitor Disk Val** | `#sys-disk-val` | Live `/data` usage | Hardcoded literal `5.8` MB (`total_mb: 128.0`) | **Hardcoded** | `src/lazy/gateway/api.py:213` |
| **System Monitor Disk Spark**| `#spark-disk` | Disk history graph | Initialized with hardcoded array `[5.8, 5.8, ...]` | **Hardcoded** | `hud/hud.js:27` |
| **System Monitor Net Val** | `#sys-net-val` | Live bandwidth | Hardcoded literal `rx_kb: 124.5, tx_kb: 89.2` | **Hardcoded** | `src/lazy/gateway/api.py:214` |
| **System Monitor Net Spark** | `#spark-net` | Net history graph | Initialized with hardcoded array `[12, 18, 14, ...]` | **Fixture** | `hud/hud.js:28` |
| **Services Supervisor Table**| `#services-tbody` | 15 Microservices state | Hardcoded list of 15 dictionaries; all status `"running"` | **Hardcoded** | `src/lazy/gateway/api.py:219-235` |
| **Pipeline Flow Visualization**| `.pipeline-node` | F1–F9 Pipeline nodes | Toggled by `setTimeout(..., 150)` in client JS | **Fixture** | `hud/hud.js:548-551` |
| **Capabilities Cards Grid** | `#agent-cards-grid` | Registered capabilities | Reads real YAML manifests from `/etc/lazy/capabilities` | **Real** | `src/lazy/gateway/api.py:373-384` |
| **File Table Directory List**| `#file-tbody` | Files in `/data` | `os.scandir(self.data_dir)` on real Btrfs mount | **Real** | `src/lazy/gateway/api.py:311-319` |
| **File Creation Action** | `#btn-new-file` | Create file on disk | `FSBroker.handle_fs_write()` with `PolicyEngine` gate | **Real** | `src/lazy/gateway/api.py:324-341` |
| **File Deletion Action** | `requestDeleteFile` | Delete file on disk | `FSBroker.handle_fs_delete()` with L2 approval gate | **Real** | `src/lazy/gateway/api.py:342-372` |
| **Audit Verification Box** | `#audit-verify-status` | Cryptographic ledger proof | `verify_audit_log()` computing genesis hash chain | **Real** | `src/lazy/gateway/api.py:285-292` |
| **Audit Log Preformatted** | `#audit-log-pre` | JSON ledger viewer | Reads raw records from `/var/log/lazy-audit.log` | **Real** | `src/lazy/gateway/api.py:273-283` |
| **App: Notes** | `.app-tile[notes]` | Note creator | Jumps to Files tab in client JS (`hud.js:717`) | **Fixture** | `hud/hud.js:717` |
| **App: Briefing** | `.app-tile[briefing]`| Morning briefing viewer | Jumps to Home tab in client JS (`hud.js:720`) | **Fixture** | `hud/hud.js:720` |
| **App: Outbox** | `.app-tile[outbox]` | Staged message queue | Opens approvals drawer in client JS (`hud.js:723`) | **Fixture** | `hud/hud.js:723` |
| **App: Web Browser** | `.app-tile.disabled` | In-guest browser | Static tile labelled `"Coming Soon"`, `"unbacked"` | **Hardcoded** | `hud/index.html:324-329` |
| **App: Email Client** | `.app-tile.disabled` | Mail client | Static tile labelled `"Coming Soon"`, `"unbacked"` | **Hardcoded** | `hud/index.html:330-335` |
| **App: Terminal Console** | `.app-tile.disabled` | Interactive shell | Static tile labelled `"Coming Soon"`, `"unbacked"` | **Hardcoded** | `hud/index.html:336-341` |
| **Settings: Reduced Motion** | `#set-reduced-motion`| UI animation toggle | Toggles `.reduced-motion` CSS class on `<body>` | **Real** (Client JS) | `hud/hud.js:701-707` |
| **Settings: Accent Color** | `#set-accent-color` | UI theme picker | Dropdown element with no JS event listener attached | **Unused/Stub** | `hud/index.html:360-365` |
| **Settings: Planner Mode** | `#set-planner-mode` | Select mock vs host LLM | Dropdown element with no JS event listener attached | **Unused/Stub** | `hud/index.html:372-376` |
| **Settings: Model Badge** | `#settings-model-badge`| Model architecture label | Static HTML `<span class="badge-pill sim">Simulated</span>` | **Hardcoded** | `hud/index.html:379` |
| **Settings: About Text** | `About Lazy OS` | Documentation snippet | Static descriptive paragraph in HTML | **Static Content**| `hud/index.html:384-386` |
| **Approvals Drawer List** | `#approvals-list` | L2 confirmation list | Populated from `self.pending_approvals` dictionary | **Real** | `src/lazy/gateway/api.py:250-252` |
| **Command Palette Options** | `.cmd-option` | Navigation jump menu | Static tab jump triggers in client JS | **Real** (Client JS) | `hud/hud.js:683-692` |
| **Identity Footer Hostname** | `#foot-identity` | Hostname, kernel, uptime | `os.uname()`, `/proc/sys/kernel/random/boot_id`, `/proc/uptime` | **Real** | `src/lazy/gateway/api.py:135-155` |
| **Identity Badges** | `#foot-badges` | System capability pills | `/api/build-info` returns hardcoded dictionary | **Hardcoded** | `src/lazy/gateway/api.py:177-194` |

---

## 3. Backend Hardcoding, Mock Flags & Fixtures Audit

### A. `src/lazy/gateway/api.py`
1. **`_get_metrics()` (Lines 210–215)**:
   - `cpu_percent` is hardcoded to `4.2`.
   - `disk` is hardcoded to `used_mb: 5.8`, `total_mb: 128.0`, `percent: 4.5`.
   - `network` is hardcoded to `rx_kb: 124.5`, `tx_kb: 89.2`.
   - **Remediation**: Must read `/proc/stat` (for real CPU utilization), `os.statvfs("/data")` (for real Btrfs disk metrics), and `/proc/net/dev` (for delta network bandwidth).
2. **`_get_services()` (Lines 218–236)**:
   - Returns a hardcoded Python array of 15 service dictionaries.
   - Every service is stamped with `"status": "running"` and `"slice": "/lazy-interactive.slice"` regardless of whether the unit is actually running, stopped, or failed.
   - **Remediation**: Must query `systemctl is-active <unit>` or introspect `/run/systemd/system/` and `/sys/fs/cgroup/`.
3. **`_get_briefing()` (Lines 386–401)**:
   - Hardcoded status `"All systems nominal. Zero security alerts."`.
   - Hardcoded chores: `"Quarantine Scrubber"`, `"Audit Ledger Checksum"`, `"Log Rotation"`.
   - Hardcoded niche feed: `"Linux 6.8 Memory Management Enhancements"`, `"Embedded Systemd Slicing Architectures"`.
   - **Remediation**: Must invoke `BriefingGenerator.generate_briefing()` with real `/data/tasks.md`, real chore execution receipts from `/var/log/lazy-chores.log`, and live niche feed items from `/data/niche/feed.json`.
4. **`_post_plan()` (Lines 436–470)**:
   - Contains a substring keyword blocklist for prompt injection (`"ignore previous instructions"`, etc.).
   - Returns a canned, single-step plan: `{"capability": "doc.create_markdown", "params": {"path": "/data/plan.md", "content": "# Generated Plan\n- Step 1"}}`.
   - Does not query `llama-server` or any LLM model.
   - **Remediation**: Must delegate planning to the real `LLMPlanner` producing grammar-constrained JSON plans.
5. **`_get_build_info()` (Lines 177–195)**:
   - Returns hardcoded status dictionaries: `storage` (`"real"`), `audit` (`"real"`), `voice` (`"simulated"`), `web_driver` (`"real"`), `comms` (`"real"`).
   - **Remediation**: Check real subsystem health and mount status at runtime.

### B. `src/lazy/gateway/host_bridge.py`
- Lines 20–32: Hardcodes `"intents": [{"capability": "doc.create_markdown", "params": {"path": "plan.md", "content": "# Plan\n- [ ] Task 1\n- [ ] Task 2\n"}}]`.

### C. `src/lazy/planner/mock.py`
- Lines 15–145: Maps user input strings directly to pre-recorded fixture JSON files in `tests/fixtures/intents/` (38 canned JSON files).
- Used as the default fallback in `src/lazy/llm/client.py:27-32` whenever `llama-server` is not answering.

### D. `src/lazy/llm/client.py`
- Lines 27–32, 82–108: `mock_fallback=True` silently diverts LLM prompts to `MockPlanner` without raising an error or notifying the user that inference failed.

### E. `src/lazy/routines/briefing.py`
- Lines 33–46: `collect_system_status()` returns hardcoded `{"cpu_percent": 3.5, "memory_used_mb": 450, "memory_total_mb": 8192}`.

---

## 4. Audit Summary Statistics

* **Total User-Visible UI Elements Audited**: 54
  - **Truly Dynamic / Real Guest Data**: 16 elements (29.6%)
    *(File table, file create/delete, audit ledger verification, audit log pre, memory usage, uptime/boot_id/hostname, pending approvals queue, command palette navigation, reduced motion setting).*
  - **Hardcoded Literals & Static Text**: 25 elements (46.3%)
    *(CPU %, Disk used/total, Network rx/tx, all 15 services in services table, briefing headline & chores & feed items, power & net header chips, planner & model badges, disabled app tiles).*
  - **Fixtures & Stubs (Client-Side Simulation)**: 13 elements (24.1%)
    *(Boot progress & status stages, sparkline initial histograms, quick command triggers, client-side regex keyword intent parsing for `note`/`service`/`audit`, fake `undoLastTask()` string, dead plan stream box, dead speech button).*

* **Total Backend Endpoints Audited**: 12
  - **Real Endpoints**: 6 (`/api/identity`, `/api/fs` [GET/POST/DELETE], `/api/audit`, `/api/audit/verify`, `/api/capabilities`, `/api/approvals`).
  - **Hardcoded / Mock Endpoints**: 6 (`/api/metrics`, `/api/services`, `/api/briefing`, `/api/plan`, `/api/build-info`, `/api/settings` [accent & planner mode]).

---

## 5. Required Action Plan for Milestone W2 & W3

1. **Purge Client-Side Substring Matching in `hud.js`**:
   - Delete lines 553–578 of `hud.js`. Connect the AI Command Center input form to real WebSocket / HTTP `/api/plan` and streaming execution.
   - Implement real `undoLastTask()` that invokes `POST /api/tasks/{id}/rollback` or `TaskManager.rollback_to_checkpoint()`.
2. **Replace Hardcoded Metrics in `src/lazy/gateway/api.py`**:
   - Compute real CPU load from `/proc/stat` delta.
   - Compute real disk usage from `os.statvfs("/data")`.
   - Compute real network I/O from `/proc/net/dev` delta.
3. **Replace Hardcoded Services in `src/lazy/gateway/api.py`**:
   - Check real status of each unit using `systemctl is-active <unit>` or direct `/sys/fs/cgroup/system.slice` inspection.
4. **Wire Real Briefing in `src/lazy/gateway/api.py`**:
   - Call `BriefingGenerator` reading real `/data/tasks.md`, `/var/log/lazy-chores.log`, and real niche items.
5. **Eliminate Mock Planner in Image (Rule H2)**:
   - Wire `LLMPlanner` with grammar constraints to official 1.5B–4B parameter instruct model with WebSocket token streaming.
   - Add planner badge showing active model name and real tokens per second.
