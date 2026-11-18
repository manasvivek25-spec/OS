# Lazy OS v3 Quick Start Guide

Welcome to Lazy OS! Get up and running in under 60 seconds.

---

## 1. Booting the Operating System

### On Linux or Windows WSL2:
```bash
# Launch with full graphical display (WSLg / X11 / Wayland)
./dist/run-lazy-os.sh

# Or launch in background headless mode
./dist/run-lazy-os.sh --headless
```

### On Windows PowerShell:
```powershell
.\dist\run-windows.ps1
```

---

## 2. Accessing the Command Center

- **Graphical Session**: Automatically opens inside the QEMU display window.
- **Web Browser (Headless Mode)**: Open **http://127.0.0.1:8766/** in Chrome, Firefox, or Edge.

---

## 3. Essential Directives

Try typing any of these into the **AI Command Center** prompt bar:

1. **System Health**:
   > *"Give me a summary of running services and memory usage"*
2. **File Creation (Tier L1)**:
   > *"Create a file called /data/todo.md with my tasks for today"*
3. **Protected File Deletion (Tier L2 - Requires User Approval)**:
   > *"Delete /data/todo.md"* $\implies$ Click **Approve** in the Approvals Drawer.
4. **Instant Undo**:
   > Click **Undo Task** in the AI Command Center to instantly roll back changes.

---

## 4. Stopping the Operating System

In your terminal:
```bash
./scripts/stop-lazy.sh
```
Or click **Shutdown** in the Command Center top status bar. All files saved to `/data` persist across reboots!
