# Lazy OS Command Center Data Sources Specification

Each Command Center module names and documents its exact data source per Rule T4:

| Module | Panel / Element | Real Data Source / Endpoint | Fallback / Unavailable Behavior |
| :--- | :--- | :--- | :--- |
| **Shell: Top Bar** | Clock & Network status | Browser local time & WebSocket connection heartbeat | Shows `offline` badge on disconnect |
| **Shell: Footer** | Guest Identity String | `GET /api/identity` (`hostname`, `kernel`, `boot_id`, `uptime`) | Shows `identity unavailable` |
| **Shell: Footer** | Subsystem Badges | `GET /api/build-info` (`kernel`, `storage`, `audit`, `llm`, etc.) | Shows `status unavailable` |
| **Module 1: Home** | Wake-Up Briefing Card | `GET /api/briefing` | Shows `Briefing unavailable` |
| **Module 1: Home** | System Health Summary | `GET /api/metrics` | Shows `Telemetry unavailable` |
| **Module 2: AI Command**| Plan Stream & Execution | WebSocket event stream (`plan_proposed`, `step_complete`) | Emits error alert |
| **Module 2: AI Command**| Task Undo Action | `POST /api/approvals` / `task.undo` capability via policy | Displays transaction receipt |
| **Module 3: Sys Monitor**| CPU, RAM, Disk, Net | `GET /api/metrics` (from `/proc/meminfo`, `/proc/stat`) | Shows `unavailable` |
| **Module 3: Sys Monitor**| Process & Service Table | `GET /api/services` (from guest service definitions) | Shows empty list |
| **Module 4: Agent Center**| Broker Activity & Counters | `GET /api/services` & WebSocket event stream | Shows zero counts |
| **Module 5: File Manager**| File Tree & Directory | `GET /api/fs?path=...` (from `FSBroker` on `/data`) | Shows error banner |
| **Module 5: File Manager**| File Write / Edit | `POST /api/fs` (policy evaluated intent `fs.write`) | Denied with policy reason |
| **Module 5: File Manager**| File Delete | `DELETE /api/fs` (creates pending approval for `fs.delete`) | Requires user confirmation |
| **Module 6: Security** | Audit Ledger Viewer | `GET /api/audit` (from `/var/log/lazy-audit.log`) | Shows empty ledger |
| **Module 6: Security** | Verify Chain Button | `POST /api/audit/verify` (calls `verify_audit_log()`) | Displays verified record count & status |
| **Module 7: App Launcher**| Application Tiles | `GET /api/capabilities` (active capabilities) | Unbacked tiles show 'coming soon' |
| **Module 8: Settings** | System Preferences | `GET /api/settings` and `POST /api/settings` | Stored in settings dictionary |
