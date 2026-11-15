#!/usr/bin/env python3
"""Generates all capability YAML manifests for Lazy OS in config/capabilities/."""

from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CAP_DIR = REPO_ROOT / "config" / "capabilities"
CAP_DIR.mkdir(parents=True, exist_ok=True)

CAPABILITIES = [
    # L0 Read-only
    {
        "name": "fs.read",
        "description": "Read file contents",
        "params_schema": {"type": "object", "required": ["path"], "properties": {"path": {"type": "string"}}},
        "tier": "L0",
        "effect_class": "reversible",
        "approval_mode": "automatic",
        "sandbox_profile": "read_only",
        "undo_method": "none",
        "taint_rules": {"disallow_untrusted_keys": [], "require_user_confirmation": False}
    },
    {
        "name": "fs.list",
        "description": "List directory contents",
        "params_schema": {"type": "object", "required": ["path"], "properties": {"path": {"type": "string"}}},
        "tier": "L0",
        "effect_class": "reversible",
        "approval_mode": "automatic",
        "sandbox_profile": "read_only",
        "undo_method": "none",
        "taint_rules": {"disallow_untrusted_keys": [], "require_user_confirmation": False}
    },
    {
        "name": "sys.service_status",
        "description": "Query status of a systemd service",
        "params_schema": {"type": "object", "required": ["service"], "properties": {"service": {"type": "string"}}},
        "tier": "L0",
        "effect_class": "reversible",
        "approval_mode": "automatic",
        "sandbox_profile": "system_query",
        "undo_method": "none",
        "taint_rules": {"disallow_untrusted_keys": [], "require_user_confirmation": False}
    },
    {
        "name": "sys.logs_read",
        "description": "Read service journal logs",
        "params_schema": {"type": "object", "properties": {"service": {"type": "string"}, "lines": {"type": "integer", "minimum": 1, "maximum": 500}}},
        "tier": "L0",
        "effect_class": "reversible",
        "approval_mode": "automatic",
        "sandbox_profile": "system_query",
        "undo_method": "none",
        "taint_rules": {"disallow_untrusted_keys": [], "require_user_confirmation": False}
    },
    {
        "name": "sys.process_list",
        "description": "List running processes",
        "params_schema": {"type": "object", "properties": {}},
        "tier": "L0",
        "effect_class": "reversible",
        "approval_mode": "automatic",
        "sandbox_profile": "system_query",
        "undo_method": "none",
        "taint_rules": {"disallow_untrusted_keys": [], "require_user_confirmation": False}
    },
    {
        "name": "hw.usb_list",
        "description": "List connected USB devices",
        "params_schema": {"type": "object", "properties": {}},
        "tier": "L0",
        "effect_class": "reversible",
        "approval_mode": "automatic",
        "sandbox_profile": "hw_query",
        "undo_method": "none",
        "taint_rules": {"disallow_untrusted_keys": [], "require_user_confirmation": False}
    },
    {
        "name": "web.read",
        "description": "Fetch and extract text content from webpage or RSS feed",
        "params_schema": {"type": "object", "required": ["url"], "properties": {"url": {"type": "string"}}},
        "tier": "L0",
        "effect_class": "reversible",
        "approval_mode": "automatic",
        "sandbox_profile": "web_sandbox",
        "undo_method": "none",
        "taint_rules": {"disallow_untrusted_keys": [], "require_user_confirmation": False}
    },
    {
        "name": "mail.list",
        "description": "List messages in maildir",
        "params_schema": {"type": "object", "properties": {"folder": {"type": "string"}}},
        "tier": "L0",
        "effect_class": "reversible",
        "approval_mode": "automatic",
        "sandbox_profile": "comms_query",
        "undo_method": "none",
        "taint_rules": {"disallow_untrusted_keys": [], "require_user_confirmation": False}
    },
    {
        "name": "mail.read",
        "description": "Read specific email by message id",
        "params_schema": {"type": "object", "required": ["message_id"], "properties": {"message_id": {"type": "string"}}},
        "tier": "L0",
        "effect_class": "reversible",
        "approval_mode": "automatic",
        "sandbox_profile": "comms_query",
        "undo_method": "none",
        "taint_rules": {"disallow_untrusted_keys": [], "require_user_confirmation": False}
    },
    {
        "name": "chat.read",
        "description": "Read recent chat messages",
        "params_schema": {"type": "object", "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 100}}},
        "tier": "L0",
        "effect_class": "reversible",
        "approval_mode": "automatic",
        "sandbox_profile": "comms_query",
        "undo_method": "none",
        "taint_rules": {"disallow_untrusted_keys": [], "require_user_confirmation": False}
    },
    {
        "name": "task.undo",
        "description": "Rollback a task to its pre-execution checkpoint (user only)",
        "params_schema": {"type": "object", "required": ["task_id"], "properties": {"task_id": {"type": "string"}}},
        "tier": "L0",
        "effect_class": "reversible",
        "approval_mode": "user_confirm",
        "sandbox_profile": "task_admin",
        "undo_method": "none",
        "taint_rules": {"disallow_untrusted_keys": ["task_id"], "require_user_confirmation": True}
    },
    {
        "name": "outbox.cancel",
        "description": "Cancel a pending outbox item during undo window (user only)",
        "params_schema": {"type": "object", "required": ["item_id"], "properties": {"item_id": {"type": "string"}}},
        "tier": "L0",
        "effect_class": "reversible",
        "approval_mode": "user_confirm",
        "sandbox_profile": "outbox_admin",
        "undo_method": "none",
        "taint_rules": {"disallow_untrusted_keys": ["item_id"], "require_user_confirmation": True}
    },

    # L1 Low-risk automatic
    {
        "name": "fs.write",
        "description": "Create or write file within writable data directory",
        "params_schema": {"type": "object", "required": ["path", "content"], "properties": {"path": {"type": "string"}, "content": {"type": "string"}}},
        "tier": "L1",
        "effect_class": "reversible",
        "approval_mode": "automatic",
        "sandbox_profile": "writable_data",
        "undo_method": "snapshot_revert",
        "taint_rules": {"disallow_untrusted_keys": ["path"], "require_user_confirmation": False}
    },
    {
        "name": "fs.copy",
        "description": "Copy file within writable directory",
        "params_schema": {"type": "object", "required": ["src", "dest"], "properties": {"src": {"type": "string"}, "dest": {"type": "string"}}},
        "tier": "L1",
        "effect_class": "reversible",
        "approval_mode": "automatic",
        "sandbox_profile": "writable_data",
        "undo_method": "snapshot_revert",
        "taint_rules": {"disallow_untrusted_keys": ["dest"], "require_user_confirmation": False}
    },
    {
        "name": "fs.move",
        "description": "Move/rename file within writable directory",
        "params_schema": {"type": "object", "required": ["src", "dest"], "properties": {"src": {"type": "string"}, "dest": {"type": "string"}}},
        "tier": "L1",
        "effect_class": "reversible",
        "approval_mode": "automatic",
        "sandbox_profile": "writable_data",
        "undo_method": "snapshot_revert",
        "taint_rules": {"disallow_untrusted_keys": ["dest"], "require_user_confirmation": False}
    },
    {
        "name": "doc.create_markdown",
        "description": "Create markdown document",
        "params_schema": {"type": "object", "required": ["path", "content"], "properties": {"path": {"type": "string"}, "content": {"type": "string"}}},
        "tier": "L1",
        "effect_class": "reversible",
        "approval_mode": "automatic",
        "sandbox_profile": "writable_data",
        "undo_method": "snapshot_revert",
        "taint_rules": {"disallow_untrusted_keys": ["path"], "require_user_confirmation": False}
    },
    {
        "name": "doc.create_docx",
        "description": "Create formatted docx document",
        "params_schema": {"type": "object", "required": ["path", "content"], "properties": {"path": {"type": "string"}, "content": {"type": "string"}}},
        "tier": "L1",
        "effect_class": "reversible",
        "approval_mode": "automatic",
        "sandbox_profile": "writable_data",
        "undo_method": "snapshot_revert",
        "taint_rules": {"disallow_untrusted_keys": ["path"], "require_user_confirmation": False}
    },
    {
        "name": "code.write",
        "description": "Write source code file",
        "params_schema": {"type": "object", "required": ["path", "content"], "properties": {"path": {"type": "string"}, "content": {"type": "string"}}},
        "tier": "L1",
        "effect_class": "reversible",
        "approval_mode": "automatic",
        "sandbox_profile": "writable_data",
        "undo_method": "snapshot_revert",
        "taint_rules": {"disallow_untrusted_keys": ["path"], "require_user_confirmation": False}
    },
    {
        "name": "hw.backlight_set",
        "description": "Set laptop screen brightness",
        "params_schema": {"type": "object", "required": ["brightness"], "properties": {"brightness": {"type": "integer", "minimum": 0, "maximum": 100}}},
        "tier": "L1",
        "effect_class": "compensable",
        "approval_mode": "automatic",
        "sandbox_profile": "hw_control",
        "undo_method": "restore_backlight",
        "taint_rules": {"disallow_untrusted_keys": [], "require_user_confirmation": False}
    },
    {
        "name": "hw.volume_set",
        "description": "Set audio output volume",
        "params_schema": {"type": "object", "required": ["volume"], "properties": {"volume": {"type": "integer", "minimum": 0, "maximum": 100}}},
        "tier": "L1",
        "effect_class": "compensable",
        "approval_mode": "automatic",
        "sandbox_profile": "hw_control",
        "undo_method": "restore_volume",
        "taint_rules": {"disallow_untrusted_keys": [], "require_user_confirmation": False}
    },
    {
        "name": "mail.draft",
        "description": "Create email draft without sending",
        "params_schema": {"type": "object", "required": ["to", "subject", "body"], "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}}},
        "tier": "L1",
        "effect_class": "reversible",
        "approval_mode": "automatic",
        "sandbox_profile": "comms_draft",
        "undo_method": "delete_draft",
        "taint_rules": {"disallow_untrusted_keys": [], "require_user_confirmation": False}
    },
    {
        "name": "web.navigate",
        "description": "Navigate isolated browser to URL (L1 for allowlist, L2 for new domain)",
        "params_schema": {"type": "object", "required": ["url"], "properties": {"url": {"type": "string"}}},
        "tier": "L1",
        "effect_class": "reversible",
        "approval_mode": "automatic",
        "sandbox_profile": "web_isolated",
        "undo_method": "browser_back",
        "taint_rules": {"disallow_untrusted_keys": ["url"], "require_user_confirmation": True}
    },

    # L2 Approval required
    {
        "name": "fs.delete",
        "description": "Delete file or directory within writable volume",
        "params_schema": {"type": "object", "required": ["path"], "properties": {"path": {"type": "string"}}},
        "tier": "L2",
        "effect_class": "reversible",
        "approval_mode": "user_confirm",
        "sandbox_profile": "writable_data",
        "undo_method": "snapshot_revert",
        "taint_rules": {"disallow_untrusted_keys": ["path"], "require_user_confirmation": True}
    },
    {
        "name": "code.run",
        "description": "Execute script inside transient systemd-run sandbox",
        "params_schema": {"type": "object", "required": ["command"], "properties": {"command": {"type": "string"}, "timeout": {"type": "integer", "minimum": 1, "maximum": 300}}},
        "tier": "L2",
        "effect_class": "reversible",
        "approval_mode": "user_confirm",
        "sandbox_profile": "systemd_run_transient",
        "undo_method": "snapshot_revert",
        "taint_rules": {"disallow_untrusted_keys": ["command"], "require_user_confirmation": True}
    },
    {
        "name": "sys.service_restart",
        "description": "Restart systemd service",
        "params_schema": {"type": "object", "required": ["service"], "properties": {"service": {"type": "string"}}},
        "tier": "L2",
        "effect_class": "compensable",
        "approval_mode": "user_confirm",
        "sandbox_profile": "system_admin",
        "undo_method": "restore_service_state",
        "taint_rules": {"disallow_untrusted_keys": ["service"], "require_user_confirmation": True}
    },
    {
        "name": "sys.setting_set",
        "description": "Adjust system configuration key",
        "params_schema": {"type": "object", "required": ["key", "value"], "properties": {"key": {"type": "string"}, "value": {"type": "string"}}},
        "tier": "L2",
        "effect_class": "compensable",
        "approval_mode": "user_confirm",
        "sandbox_profile": "system_admin",
        "undo_method": "restore_setting",
        "taint_rules": {"disallow_untrusted_keys": ["key", "value"], "require_user_confirmation": True}
    },
    {
        "name": "hw.rfkill_set",
        "description": "Toggle RFKill state (wifi, bluetooth)",
        "params_schema": {"type": "object", "required": ["subsystem", "state"], "properties": {"subsystem": {"type": "string", "enum": ["wlan", "bluetooth", "all"]}, "state": {"type": "string", "enum": ["block", "unblock"]}}},
        "tier": "L2",
        "effect_class": "compensable",
        "approval_mode": "user_confirm",
        "sandbox_profile": "hw_control",
        "undo_method": "restore_rfkill",
        "taint_rules": {"disallow_untrusted_keys": [], "require_user_confirmation": True}
    },
    {
        "name": "hw.power_profile_set",
        "description": "Set ACPI platform power profile",
        "params_schema": {"type": "object", "required": ["profile"], "properties": {"profile": {"type": "string", "enum": ["low-power", "balanced", "performance"]}}},
        "tier": "L2",
        "effect_class": "compensable",
        "approval_mode": "user_confirm",
        "sandbox_profile": "hw_control",
        "undo_method": "restore_power_profile",
        "taint_rules": {"disallow_untrusted_keys": [], "require_user_confirmation": True}
    },
    {
        "name": "hw.governor_set",
        "description": "Set CPU frequency scaling governor",
        "params_schema": {"type": "object", "required": ["governor"], "properties": {"governor": {"type": "string", "enum": ["powersave", "performance", "schedutil"]}}},
        "tier": "L2",
        "effect_class": "compensable",
        "approval_mode": "user_confirm",
        "sandbox_profile": "hw_control",
        "undo_method": "restore_governor",
        "taint_rules": {"disallow_untrusted_keys": [], "require_user_confirmation": True}
    },
    {
        "name": "web.click",
        "description": "Click element on active webpage",
        "params_schema": {"type": "object", "required": ["element_id"], "properties": {"element_id": {"type": "string"}}},
        "tier": "L2",
        "effect_class": "reversible",
        "approval_mode": "user_confirm",
        "sandbox_profile": "web_isolated",
        "undo_method": "browser_back",
        "taint_rules": {"disallow_untrusted_keys": ["element_id"], "require_user_confirmation": True}
    },
    {
        "name": "web.fill",
        "description": "Fill form field on active webpage",
        "params_schema": {"type": "object", "required": ["element_id", "value"], "properties": {"element_id": {"type": "string"}, "value": {"type": "string"}}},
        "tier": "L2",
        "effect_class": "reversible",
        "approval_mode": "user_confirm",
        "sandbox_profile": "web_isolated",
        "undo_method": "browser_clear_field",
        "taint_rules": {"disallow_untrusted_keys": ["element_id", "value"], "require_user_confirmation": True}
    },

    # L3 Hazardous (External / Hardware Auth / Process Signal)
    {
        "name": "web.submit",
        "description": "Submit web form to external server",
        "params_schema": {"type": "object", "required": ["form_id"], "properties": {"form_id": {"type": "string"}}},
        "tier": "L3",
        "effect_class": "irreversible",
        "approval_mode": "outbox_delay",
        "sandbox_profile": "web_isolated",
        "undo_method": "outbox_cancel",
        "taint_rules": {"disallow_untrusted_keys": ["form_id"], "require_user_confirmation": True}
    },
    {
        "name": "web.download",
        "description": "Download external file into quarantine",
        "params_schema": {"type": "object", "required": ["url", "dest_filename"], "properties": {"url": {"type": "string"}, "dest_filename": {"type": "string"}}},
        "tier": "L3",
        "effect_class": "irreversible",
        "approval_mode": "user_confirm",
        "sandbox_profile": "quarantine_sandbox",
        "undo_method": "delete_quarantined_file",
        "taint_rules": {"disallow_untrusted_keys": ["url", "dest_filename"], "require_user_confirmation": True}
    },
    {
        "name": "mail.send",
        "description": "Queue email send via outbox with delay and preview",
        "params_schema": {"type": "object", "required": ["to", "subject", "body"], "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}, "attachments": {"type": "array", "items": {"type": "string"}}}},
        "tier": "L3",
        "effect_class": "irreversible",
        "approval_mode": "outbox_delay",
        "sandbox_profile": "comms_outbox",
        "undo_method": "outbox_cancel",
        "taint_rules": {"disallow_untrusted_keys": ["to", "subject", "body", "attachments"], "require_user_confirmation": True}
    },
    {
        "name": "chat.send",
        "description": "Queue chat message send via outbox",
        "params_schema": {"type": "object", "required": ["to", "body"], "properties": {"to": {"type": "string"}, "body": {"type": "string"}}},
        "tier": "L3",
        "effect_class": "irreversible",
        "approval_mode": "outbox_delay",
        "sandbox_profile": "comms_outbox",
        "undo_method": "outbox_cancel",
        "taint_rules": {"disallow_untrusted_keys": ["to", "body"], "require_user_confirmation": True}
    },
    {
        "name": "sys.process_signal",
        "description": "Send signal (SIGTERM, SIGKILL) to a process",
        "params_schema": {"type": "object", "required": ["pid", "signal"], "properties": {"pid": {"type": "integer", "minimum": 1}, "signal": {"type": "string", "enum": ["SIGTERM", "SIGKILL", "SIGHUP"]}}},
        "tier": "L3",
        "effect_class": "irreversible",
        "approval_mode": "user_confirm",
        "sandbox_profile": "system_admin",
        "undo_method": "none",
        "taint_rules": {"disallow_untrusted_keys": ["pid"], "require_user_confirmation": True}
    },
    {
        "name": "hw.usb_authorize",
        "description": "Authorize untrusted USB device for connection",
        "params_schema": {"type": "object", "required": ["device_id"], "properties": {"device_id": {"type": "string"}}},
        "tier": "L3",
        "effect_class": "irreversible",
        "approval_mode": "user_confirm",
        "sandbox_profile": "hw_admin",
        "undo_method": "usb_deauthorize",
        "taint_rules": {"disallow_untrusted_keys": ["device_id"], "require_user_confirmation": True}
    }
]

for cap in CAPABILITIES:
    filename = f"{cap['name']}.yaml"
    out_path = CAP_DIR / filename
    out_path.write_text(yaml.dump(cap, sort_keys=False), encoding="utf-8")

print(f"Generated {len(CAPABILITIES)} capability manifests in {CAP_DIR}")
