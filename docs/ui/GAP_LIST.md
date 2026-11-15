# Lazy OS Command Center UI Gap Analysis (V2.C1)

**Audit Date:** 2026-11-16T01:40:30+05:30  
**Auditor:** Antigravity Autonomous Systems Engineer

---

## 1. Existing HUD vs. Command Center Requirements

| Area / Feature | Existing HUD (`hud/index.html` v1) | V2 Command Center Requirement | Status / Action Needed |
| :--- | :--- | :--- | :--- |
| **Technology** | Static HTML5 + CSS + vanilla JS (20.5 KB total) | Static single-page app (no build step, no CDN, works offline) | **Keep base technology:** zero external dependencies |
| **Shell & Layout** | Basic single-view grid with 6 cards | Desktop-first shell: top status bar, left nav, workspace, notifications, footer | **Implement:** Build modular shell with 8 view panels |
| **Identity Footer**| Absent (simple title only) | Real in-guest identity string from `GET /api/identity` + badges | **Implement:** Identity footer with live API binding |
| **Honest Badges**  | Absent | Badges for each subsystem from `GET /api/build-info` | **Implement:** Status pills (Real, Simulated, Absent) |
| **Command Bar**    | Simple bottom chat input box | Global `Ctrl+K` quick switcher & prompt palette | **Implement:** Keyboard listener & modal overlay |
| **Approvals Drawer**| Modal dialog for approvals | Dedicated slide-out approvals drawer with countdown | **Implement:** Staged queue with Approve / Reject |
| **Module 1: Home** | Static text cards | Wake-up briefing, system health summary, recent tasks | **Implement:** Bind to `/api/briefing`, `/api/metrics` |
| **Module 2: AI Command**| WebSocket send only | Natural language, streaming plan, step status, inline approval, task ID & undo link | **Implement:** Task lifecycle view with undo action |
| **Module 3: Sys Monitor**| Hardcoded telemetry gauges | Live CPU, RAM, Disk, Net, process table, SVG sparklines | **Implement:** Real `/api/metrics` with SVG graphs |
| **Module 4: Agent Center**| Static capability list | Component cards with request counts & live pipeline lighting | **Implement:** Interactive broker cards & pipeline map |
| **Module 5: File Manager**| Absent | Browse, create, read, edit, delete with breadcrumbs & undo | **Implement:** Bind to `/api/fs` with L2 delete approval |
| **Module 6: Security**| Tier legend only | Tier legend, audit ledger viewer, "Verify Chain" button | **Implement:** Bind to `/api/audit` and `/api/audit/verify` |
| **Module 7: App Launcher**| Absent | Grid of real capability-backed utility tiles (Notes, Briefing) | **Implement:** Interactive launcher with active tiles |
| **Module 8: Settings**| Absent | Appearance, reduced motion, accent color, agent mode | **Implement:** LocalStorage & `/api/settings` integration |
