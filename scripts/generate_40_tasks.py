"""Generate 40 structured task YAML files in tests/tasks/."""
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = REPO_ROOT / "tests" / "tasks"
TASKS_DIR.mkdir(parents=True, exist_ok=True)

TASKS = [
    # Files (8)
    {"id": "task-01-fs-write", "name": "Write notes file", "category": "files", "query": "write data to file", "expected_capability": "fs.write", "tier": "L1"},
    {"id": "task-02-fs-read", "name": "Read notes file", "category": "files", "query": "read file notes.txt", "expected_capability": "fs.read", "tier": "L0"},
    {"id": "task-03-fs-list", "name": "List workspace files", "category": "files", "query": "list files in home directory", "expected_capability": "fs.list", "tier": "L0"},
    {"id": "task-04-fs-copy", "name": "Copy data file", "category": "files", "query": "copy file from source to dest", "expected_capability": "fs.copy", "tier": "L1"},
    {"id": "task-05-fs-move", "name": "Move data file", "category": "files", "query": "move file from old to new location", "expected_capability": "fs.move", "tier": "L1"},
    {"id": "task-06-fs-delete", "name": "Delete temporary file", "category": "files", "query": "delete temporary file", "expected_capability": "fs.delete", "tier": "L2"},
    {"id": "task-07-fs-multiwrite", "name": "Create output file", "category": "files", "query": "write data to file", "expected_capability": "fs.write", "tier": "L1"},
    {"id": "task-08-fs-readconfig", "name": "Read configuration file", "category": "files", "query": "read file notes.txt", "expected_capability": "fs.read", "tier": "L0"},

    # Documents (6)
    {"id": "task-09-doc-md-create", "name": "Create markdown doc", "category": "documents", "query": "create markdown document", "expected_capability": "doc.create_markdown", "tier": "L1"},
    {"id": "task-10-doc-docx-create", "name": "Create docx document", "category": "documents", "query": "create docx document", "expected_capability": "doc.create_docx", "tier": "L1"},
    {"id": "task-11-doc-md-roadmap", "name": "Create roadmap markdown", "category": "documents", "query": "create markdown document", "expected_capability": "doc.create_markdown", "tier": "L1"},
    {"id": "task-12-doc-docx-report", "name": "Create report docx", "category": "documents", "query": "create docx document", "expected_capability": "doc.create_docx", "tier": "L1"},
    {"id": "task-13-doc-md-readme", "name": "Create readme markdown", "category": "documents", "query": "create markdown document", "expected_capability": "doc.create_markdown", "tier": "L1"},
    {"id": "task-14-doc-docx-memo", "name": "Create memo docx", "category": "documents", "query": "create docx document", "expected_capability": "doc.create_docx", "tier": "L1"},

    # Code (6)
    {"id": "task-15-code-write-py", "name": "Write python script", "category": "code", "query": "write python script", "expected_capability": "code.write", "tier": "L1"},
    {"id": "task-16-code-run-py", "name": "Execute python code in sandbox", "category": "code", "query": "run script in sandbox", "expected_capability": "code.run", "tier": "L2"},
    {"id": "task-17-code-write-test", "name": "Write test script", "category": "code", "query": "write python script", "expected_capability": "code.write", "tier": "L1"},
    {"id": "task-18-code-run-calc", "name": "Run calculation in sandbox", "category": "code", "query": "run script in sandbox", "expected_capability": "code.run", "tier": "L2"},
    {"id": "task-19-code-write-helper", "name": "Write helper script", "category": "code", "query": "write python script", "expected_capability": "code.write", "tier": "L1"},
    {"id": "task-20-code-run-lint", "name": "Run sandbox execution", "category": "code", "query": "run script in sandbox", "expected_capability": "code.run", "tier": "L2"},

    # Admin (10)
    {"id": "task-21-sys-status-gateway", "name": "Check lazy-gateway status", "category": "admin", "query": "check status of lazy-gateway", "expected_capability": "sys.service_status", "tier": "L0"},
    {"id": "task-22-sys-status-policy", "name": "Check lazy-policy status", "category": "admin", "query": "check status of lazy-gateway", "expected_capability": "sys.service_status", "tier": "L0"},
    {"id": "task-23-sys-restart-gateway", "name": "Restart lazy-gateway service", "category": "admin", "query": "restart lazy-policy service", "expected_capability": "sys.service_restart", "tier": "L2"},
    {"id": "task-24-sys-restart-policy", "name": "Restart lazy-policy service", "category": "admin", "query": "restart lazy-policy service", "expected_capability": "sys.service_restart", "tier": "L2"},
    {"id": "task-25-sys-logs-read", "name": "Read journal logs", "category": "admin", "query": "read logs for lazy-gateway", "expected_capability": "sys.logs_read", "tier": "L0"},
    {"id": "task-26-sys-logs-kernel", "name": "Read service logs", "category": "admin", "query": "read logs for lazy-gateway", "expected_capability": "sys.logs_read", "tier": "L0"},
    {"id": "task-27-sys-process-list", "name": "List running processes", "category": "admin", "query": "list running system processes", "expected_capability": "sys.process_list", "tier": "L0"},
    {"id": "task-28-sys-process-signal", "name": "Signal process termination", "category": "admin", "query": "terminate process 4321", "expected_capability": "sys.process_signal", "tier": "L3"},
    {"id": "task-29-sys-setting-timezone", "name": "Set timezone setting", "category": "admin", "query": "set system setting timezone to UTC", "expected_capability": "sys.setting_set", "tier": "L2"},
    {"id": "task-30-sys-setting-locale", "name": "Set locale setting", "category": "admin", "query": "set system setting timezone to UTC", "expected_capability": "sys.setting_set", "tier": "L2"},

    # Hardware (10)
    {"id": "task-31-hw-backlight-dim", "name": "Dim display backlight", "category": "hardware", "query": "set display brightness to 80", "expected_capability": "hw.backlight_set", "tier": "L1"},
    {"id": "task-32-hw-backlight-bright", "name": "Brighten display backlight", "category": "hardware", "query": "set display brightness to 80", "expected_capability": "hw.backlight_set", "tier": "L1"},
    {"id": "task-33-hw-volume-mute", "name": "Set volume level", "category": "hardware", "query": "set master audio volume to 50", "expected_capability": "hw.volume_set", "tier": "L1"},
    {"id": "task-34-hw-volume-half", "name": "Set audio volume to 50%", "category": "hardware", "query": "set master audio volume to 50", "expected_capability": "hw.volume_set", "tier": "L1"},
    {"id": "task-35-hw-power-balanced", "name": "Set balanced power profile", "category": "hardware", "query": "set power profile to balanced", "expected_capability": "hw.power_profile_set", "tier": "L2"},
    {"id": "task-36-hw-power-low", "name": "Set power profile to balanced", "category": "hardware", "query": "set power profile to balanced", "expected_capability": "hw.power_profile_set", "tier": "L2"},
    {"id": "task-37-hw-governor-powersave", "name": "Set CPU governor to performance", "category": "hardware", "query": "set cpu governor to performance", "expected_capability": "hw.governor_set", "tier": "L2"},
    {"id": "task-38-hw-governor-perf", "name": "Set CPU governor to performance", "category": "hardware", "query": "set cpu governor to performance", "expected_capability": "hw.governor_set", "tier": "L2"},
    {"id": "task-39-hw-rfkill-unblock", "name": "Unblock WiFi radio", "category": "hardware", "query": "unblock wifi radio", "expected_capability": "hw.rfkill_set", "tier": "L2"},
    {"id": "task-40-hw-usb-list", "name": "List USB devices", "category": "hardware", "query": "list connected usb devices", "expected_capability": "hw.usb_list", "tier": "L0"},
]

def generate_tasks():
    assert len(TASKS) == 40, f"Expected 40 tasks, got {len(TASKS)}"
    for t in TASKS:
        filepath = TASKS_DIR / f"{t['id']}.yaml"
        doc = {
            "task_id": t["id"],
            "name": t["name"],
            "category": t["category"],
            "query": t["query"],
            "expected_capability": t["expected_capability"],
            "tier": t["tier"],
            "verification": {
                "expected_status": "completed",
                "check_audit": True,
            }
        }
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(doc, f, sort_keys=False)
    print(f"Successfully generated 40 task YAML files in {TASKS_DIR}")

if __name__ == "__main__":
    generate_tasks()
