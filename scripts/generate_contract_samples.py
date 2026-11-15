#!/usr/bin/env python3
"""Generates 31 valid and 31 invalid contract sample files for Lazy OS."""

import json
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
VALID_DIR = REPO_ROOT / "tests" / "fixtures" / "contracts" / "valid"
INVALID_DIR = REPO_ROOT / "tests" / "fixtures" / "contracts" / "invalid"

VALID_DIR.mkdir(parents=True, exist_ok=True)
INVALID_DIR.mkdir(parents=True, exist_ok=True)

# 1. VALID SAMPLES
valid_intents = [
    {
        "id": "intent-001",
        "ts": "2026-11-15T12:00:00Z",
        "task_id": "task-100",
        "requester": "text",
        "capability": "fs.read",
        "params": {"path": "/home/user/notes.txt"},
        "provenance": [{"source": "user_prompt", "trusted": True, "detail": "Direct CLI entry"}]
    },
    {
        "id": "intent-002",
        "ts": "2026-11-15T12:05:00Z",
        "task_id": "task-101",
        "requester": "voice",
        "capability": "hw.backlight_set",
        "params": {"brightness": 80},
        "provenance": [{"source": "voice_wake", "trusted": True}]
    },
    {
        "id": "intent-003",
        "ts": "2026-11-15T12:10:00Z",
        "task_id": "task-102",
        "requester": "hud",
        "capability": "sys.service_restart",
        "params": {"service": "bluetooth"},
        "provenance": [{"source": "hud_click", "trusted": True}]
    },
    {
        "id": "intent-004",
        "ts": "2026-11-15T12:15:00Z",
        "task_id": "task-103",
        "requester": "routine",
        "capability": "web.read",
        "params": {"url": "https://news.ycombinator.com/rss"},
        "provenance": [{"source": "morning_briefing", "trusted": True}]
    },
    {
        "id": "intent-005",
        "ts": "2026-11-15T12:20:00Z",
        "task_id": "task-104",
        "requester": "text",
        "capability": "code.write",
        "params": {"path": "/home/user/script.py", "content": "print('hello')"},
        "provenance": [{"source": "user_text", "trusted": True}]
    }
]

valid_plans = [
    {
        "id": "plan-001",
        "steps": [valid_intents[0]],
        "rationale": "Read document to extract relevant notes for user."
    },
    {
        "id": "plan-002",
        "steps": [valid_intents[1]],
        "rationale": "Adjust display brightness per voice command."
    },
    {
        "id": "plan-003",
        "steps": [valid_intents[0], valid_intents[4]],
        "rationale": "Read template and generate python script."
    },
    {
        "id": "plan-004",
        "steps": [valid_intents[3]],
        "rationale": "Fetch news feed for daily morning digest."
    }
]

valid_decisions = [
    {
        "intent_id": "intent-001",
        "verdict": "allow",
        "tier": "L0",
        "effect_class": "reversible",
        "reason": "Read-only file inspection is permitted automatically.",
        "approval_mode": "automatic"
    },
    {
        "intent_id": "intent-002",
        "verdict": "allow",
        "tier": "L1",
        "effect_class": "compensable",
        "reason": "Hardware brightness adjustment is L1 automatic.",
        "approval_mode": "automatic"
    },
    {
        "intent_id": "intent-003",
        "verdict": "ask",
        "tier": "L2",
        "effect_class": "compensable",
        "reason": "System service restart requires explicit user confirmation.",
        "approval_mode": "user_confirm"
    },
    {
        "intent_id": "intent-004",
        "verdict": "allow",
        "tier": "L0",
        "effect_class": "reversible",
        "reason": "Reading RSS feed is safe read-only retrieval.",
        "approval_mode": "automatic"
    },
    {
        "intent_id": "intent-deny-example",
        "verdict": "deny",
        "tier": "L4",
        "effect_class": "irreversible",
        "reason": "Prohibited attempt to overwrite policy engine manifests.",
        "approval_mode": "denied"
    }
]

valid_events = [
    {
        "id": "event-001",
        "ts": "2026-11-15T12:00:00Z",
        "type": "audit.record_created",
        "severity": "info",
        "source": "lazy-audit",
        "data": {"seq": 1, "record_hash": "a1b2c3d4"}
    },
    {
        "id": "event-002",
        "ts": "2026-11-15T12:01:00Z",
        "type": "policy.decision_made",
        "severity": "info",
        "source": "lazy-policy",
        "data": {"intent_id": "intent-001", "verdict": "allow"}
    },
    {
        "id": "event-003",
        "ts": "2026-11-15T12:02:00Z",
        "type": "hardware.brightness_changed",
        "severity": "debug",
        "source": "lazy-broker-hw",
        "data": {"old": 50, "new": 80}
    },
    {
        "id": "event-004",
        "ts": "2026-11-15T12:03:00Z",
        "type": "tasks.snapshot_created",
        "severity": "info",
        "source": "lazy-tasks",
        "data": {"snapshot_id": "snap-001", "backend": "copy"}
    },
    {
        "id": "event-005",
        "ts": "2026-11-15T12:04:00Z",
        "type": "security.l4_attempt_blocked",
        "severity": "warning",
        "source": "lazy-policy",
        "data": {"target": "policy.yaml", "verdict": "deny"}
    }
]

valid_tasks = [
    {
        "id": "task-001",
        "status": "completed",
        "steps": [
            {
                "step_index": 0,
                "intent_id": "intent-001",
                "status": "done",
                "checkpoint_id": "snap-001",
                "result": {"status": "ok"}
            }
        ],
        "checkpoints": [
            {
                "id": "snap-001",
                "ts": "2026-11-15T12:00:00Z",
                "backend": "copy",
                "reference": "/tmp/checkpoints/snap-001",
                "pre_hash": "hash123"
            }
        ],
        "created_at": "2026-11-15T12:00:00Z",
        "updated_at": "2026-11-15T12:01:00Z"
    },
    {
        "id": "task-002",
        "status": "running",
        "steps": [],
        "checkpoints": [],
        "created_at": "2026-11-15T12:05:00Z",
        "updated_at": "2026-11-15T12:05:00Z"
    },
    {
        "id": "task-003",
        "status": "cancelled",
        "steps": [
            {
                "step_index": 0,
                "intent_id": "intent-002",
                "status": "undone",
                "checkpoint_id": "snap-002"
            }
        ],
        "checkpoints": [
            {
                "id": "snap-002",
                "ts": "2026-11-15T12:10:00Z",
                "backend": "btrfs",
                "reference": "/snapshots/snap-002"
            }
        ],
        "created_at": "2026-11-15T12:10:00Z",
        "updated_at": "2026-11-15T12:11:00Z"
    },
    {
        "id": "task-004",
        "status": "paused",
        "steps": [],
        "checkpoints": [],
        "created_at": "2026-11-15T12:15:00Z",
        "updated_at": "2026-11-15T12:15:00Z"
    }
]

valid_outbox = [
    {
        "id": "outbox-001",
        "kind": "mail",
        "to": "boss@example.com",
        "subject": "Weekly Status Update",
        "body": "Here is the summary of project milestones.",
        "attachments": ["/home/user/report.pdf"],
        "created": "2026-11-15T12:00:00Z",
        "send_after": "2026-11-15T12:05:00Z",
        "status": "pending",
        "approvals": [
            {
                "approver": "local_user",
                "ts": "2026-11-15T12:01:00Z",
                "mode": "user_hud"
            }
        ]
    },
    {
        "id": "outbox-002",
        "kind": "chat",
        "to": "@team_chat",
        "subject": "",
        "body": "Daily briefing chore executed successfully.",
        "attachments": [],
        "created": "2026-11-15T12:10:00Z",
        "send_after": "2026-11-15T12:11:00Z",
        "status": "approved",
        "approvals": []
    },
    {
        "id": "outbox-003",
        "kind": "mail",
        "to": "colleague@example.org",
        "subject": "Code Review",
        "body": "Check out the PR diff.",
        "attachments": [],
        "created": "2026-11-15T12:20:00Z",
        "send_after": "2026-11-15T12:25:00Z",
        "status": "cancelled",
        "approvals": []
    },
    {
        "id": "outbox-004",
        "kind": "chat",
        "to": "@alerts",
        "subject": "",
        "body": "System backup finished.",
        "attachments": [],
        "created": "2026-11-15T12:30:00Z",
        "send_after": "2026-11-15T12:31:00Z",
        "status": "sent",
        "approvals": [
            {
                "approver": "local_user",
                "ts": "2026-11-15T12:30:30Z",
                "mode": "user_text"
            }
        ]
    }
]

valid_manifests = [
    {
        "name": "fs.read",
        "description": "Read file contents safely",
        "params_schema": {
            "type": "object",
            "required": ["path"],
            "properties": {"path": {"type": "string"}}
        },
        "tier": "L0",
        "effect_class": "reversible",
        "approval_mode": "automatic",
        "sandbox_profile": "read_only",
        "undo_method": "none",
        "taint_rules": {"disallow_untrusted_keys": [], "require_user_confirmation": False}
    },
    {
        "name": "fs.write",
        "description": "Write or overwrite file contents",
        "params_schema": {
            "type": "object",
            "required": ["path", "content"],
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}}
        },
        "tier": "L1",
        "effect_class": "reversible",
        "approval_mode": "automatic",
        "sandbox_profile": "writable_data",
        "undo_method": "snapshot_revert",
        "taint_rules": {"disallow_untrusted_keys": ["path"], "require_user_confirmation": False}
    },
    {
        "name": "sys.service_restart",
        "description": "Restart systemd service",
        "params_schema": {
            "type": "object",
            "required": ["service"],
            "properties": {"service": {"type": "string"}}
        },
        "tier": "L2",
        "effect_class": "compensable",
        "approval_mode": "user_confirm",
        "sandbox_profile": "system_admin",
        "undo_method": "service_restore_previous_state",
        "taint_rules": {"disallow_untrusted_keys": ["service"], "require_user_confirmation": True}
    },
    {
        "name": "mail.send",
        "description": "Send email via outbox delay",
        "params_schema": {
            "type": "object",
            "required": ["to", "subject", "body"],
            "properties": {
                "to": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"}
            }
        },
        "tier": "L3",
        "effect_class": "irreversible",
        "approval_mode": "outbox_delay",
        "sandbox_profile": "comms_isolated",
        "undo_method": "outbox_cancel",
        "taint_rules": {"disallow_untrusted_keys": ["to"], "require_user_confirmation": True}
    }
]

# Write valid samples
valid_count = 0
for i, item in enumerate(valid_intents, 1):
    (VALID_DIR / f"valid_intent_{i:02d}.json").write_text(json.dumps(item, indent=2), encoding="utf-8")
    valid_count += 1

for i, item in enumerate(valid_plans, 1):
    (VALID_DIR / f"valid_plan_{i:02d}.json").write_text(json.dumps(item, indent=2), encoding="utf-8")
    valid_count += 1

for i, item in enumerate(valid_decisions, 1):
    (VALID_DIR / f"valid_decision_{i:02d}.json").write_text(json.dumps(item, indent=2), encoding="utf-8")
    valid_count += 1

for i, item in enumerate(valid_events, 1):
    (VALID_DIR / f"valid_event_{i:02d}.json").write_text(json.dumps(item, indent=2), encoding="utf-8")
    valid_count += 1

for i, item in enumerate(valid_tasks, 1):
    (VALID_DIR / f"valid_task_{i:02d}.json").write_text(json.dumps(item, indent=2), encoding="utf-8")
    valid_count += 1

for i, item in enumerate(valid_outbox, 1):
    (VALID_DIR / f"valid_outbox_{i:02d}.json").write_text(json.dumps(item, indent=2), encoding="utf-8")
    valid_count += 1

for i, item in enumerate(valid_manifests, 1):
    (VALID_DIR / f"valid_manifest_{i:02d}.yaml").write_text(yaml.dump(item), encoding="utf-8")
    valid_count += 1

print(f"Generated {valid_count} valid contract samples in {VALID_DIR}")

# 2. INVALID SAMPLES
invalid_samples = [
    # Intent invalids (5)
    ("intent", "invalid_intent_01.json", {"ts": "2026-11-15T12:00:00Z", "task_id": "t1", "requester": "text", "capability": "fs.read", "params": {}, "provenance": []}), # missing id
    ("intent", "invalid_intent_02.json", {"id": "i1", "ts": "not-a-timestamp", "task_id": "t1", "requester": "text", "capability": "fs.read", "params": {}, "provenance": []}), # invalid ts
    ("intent", "invalid_intent_03.json", {"id": "i1", "ts": "2026-11-15T12:00:00Z", "task_id": "t1", "requester": "telepathy", "capability": "fs.read", "params": {}, "provenance": []}), # invalid requester
    ("intent", "invalid_intent_04.json", {"id": "i1", "ts": "2026-11-15T12:00:00Z", "task_id": "t1", "requester": "text", "capability": "INVALID_CAP", "params": {}, "provenance": []}), # invalid capability pattern
    ("intent", "invalid_intent_05.json", {"id": "i1", "ts": "2026-11-15T12:00:00Z", "task_id": "t1", "requester": "text", "capability": "fs.read", "params": {}, "provenance": [], "unexpected_field": True}), # additionalProperty

    # Plan invalids (4)
    ("plan", "invalid_plan_01.json", {"steps": [], "rationale": "no id"}), # missing id
    ("plan", "invalid_plan_02.json", {"id": "p1", "steps": "not-a-list", "rationale": "bad steps"}), # steps not array
    ("plan", "invalid_plan_03.json", {"id": "p1", "steps": [{"bad": "step"}], "rationale": "bad step structure"}), # step does not match intent schema
    ("plan", "invalid_plan_04.json", {"id": "p1", "steps": [], "rationale": 123}), # rationale not string

    # Decision invalids (5)
    ("decision", "invalid_decision_01.json", {"intent_id": "i1", "verdict": "maybe", "tier": "L0", "effect_class": "reversible", "reason": "ok", "approval_mode": "automatic"}), # invalid verdict
    ("decision", "invalid_decision_02.json", {"intent_id": "i1", "verdict": "allow", "tier": "L99", "effect_class": "reversible", "reason": "ok", "approval_mode": "automatic"}), # invalid tier
    ("decision", "invalid_decision_03.json", {"intent_id": "i1", "verdict": "allow", "tier": "L1", "effect_class": "destructive", "reason": "ok", "approval_mode": "automatic"}), # invalid effect_class
    ("decision", "invalid_decision_04.json", {"intent_id": "i1", "verdict": "allow", "tier": "L1", "effect_class": "reversible", "reason": "ok", "approval_mode": "secret_bypass"}), # invalid approval_mode
    ("decision", "invalid_decision_05.json", {"verdict": "allow", "tier": "L0", "effect_class": "reversible", "reason": "missing intent_id", "approval_mode": "automatic"}), # missing intent_id

    # Event invalids (5)
    ("event", "invalid_event_01.json", {"id": "e1", "ts": "2026-11-15T12:00:00Z", "type": "test", "severity": "catastrophic", "source": "src", "data": {}}), # invalid severity
    ("event", "invalid_event_02.json", {"id": "e1", "ts": "2026-11-15T12:00:00Z", "severity": "info", "source": "src", "data": {}}), # missing type
    ("event", "invalid_event_03.json", {"id": "e1", "type": "test", "severity": "info", "source": "src", "data": {}}), # missing ts
    ("event", "invalid_event_04.json", {"id": "e1", "ts": "invalid_date", "type": "test", "severity": "info", "source": "src", "data": {}}), # bad date-time
    ("event", "invalid_event_05.json", {"id": "e1", "ts": "2026-11-15T12:00:00Z", "type": "test", "severity": "info", "source": "src"}), # missing data

    # Task invalids (4)
    ("task", "invalid_task_01.json", {"id": "t1", "status": "unknown_status", "steps": [], "checkpoints": [], "created_at": "2026-11-15T12:00:00Z", "updated_at": "2026-11-15T12:00:00Z"}), # invalid status
    ("task", "invalid_task_02.json", {"id": "t1", "status": "running", "steps": [{"step_index": -1, "intent_id": "i1", "status": "pending"}], "checkpoints": [], "created_at": "2026-11-15T12:00:00Z", "updated_at": "2026-11-15T12:00:00Z"}), # negative step_index
    ("task", "invalid_task_03.json", {"id": "t1", "status": "running", "steps": [], "checkpoints": [{"id": "c1", "ts": "2026-11-15T12:00:00Z", "backend": "ntfs", "reference": "/ref"}], "created_at": "2026-11-15T12:00:00Z", "updated_at": "2026-11-15T12:00:00Z"}), # invalid backend
    ("task", "invalid_task_04.json", {"id": "t1", "status": "running", "steps": [], "checkpoints": [], "created_at": "2026-11-15T12:00:00Z"}), # missing updated_at

    # OutboxItem invalids (4)
    ("outbox_item", "invalid_outbox_01.json", {"id": "o1", "kind": "pigeon", "to": "x", "subject": "", "body": "", "attachments": [], "created": "2026-11-15T12:00:00Z", "send_after": "2026-11-15T12:05:00Z", "status": "pending", "approvals": []}), # invalid kind
    ("outbox_item", "invalid_outbox_02.json", {"id": "o1", "kind": "mail", "subject": "", "body": "", "attachments": [], "created": "2026-11-15T12:00:00Z", "send_after": "2026-11-15T12:05:00Z", "status": "pending", "approvals": []}), # missing to
    ("outbox_item", "invalid_outbox_03.json", {"id": "o1", "kind": "mail", "to": "x", "subject": "", "body": "", "attachments": [], "created": "2026-11-15T12:00:00Z", "send_after": "2026-11-15T12:05:00Z", "status": "in_flight", "approvals": []}), # invalid status
    ("outbox_item", "invalid_outbox_04.json", {"id": "o1", "kind": "mail", "to": "x", "subject": "", "body": "", "attachments": [], "send_after": "2026-11-15T12:05:00Z", "status": "pending", "approvals": []}), # missing created

    # CapabilityManifest invalids (4)
    ("capability_manifest", "invalid_manifest_01.yaml", {"name": "fs.read", "params_schema": {}, "tier": "L99", "effect_class": "reversible", "approval_mode": "automatic", "sandbox_profile": "ro", "undo_method": "none", "taint_rules": {}}), # invalid tier
    ("capability_manifest", "invalid_manifest_02.yaml", {"name": "BAD-CAP-NAME", "params_schema": {}, "tier": "L0", "effect_class": "reversible", "approval_mode": "automatic", "sandbox_profile": "ro", "undo_method": "none", "taint_rules": {}}), # invalid name pattern
    ("capability_manifest", "invalid_manifest_03.yaml", {"name": "fs.read", "tier": "L0", "effect_class": "reversible", "approval_mode": "automatic", "sandbox_profile": "ro", "undo_method": "none", "taint_rules": {}}), # missing params_schema
    ("capability_manifest", "invalid_manifest_04.yaml", {"name": "fs.read", "params_schema": {}, "tier": "L0", "effect_class": "reversible", "approval_mode": "automatic", "sandbox_profile": "ro", "taint_rules": {}}), # missing undo_method
]

invalid_count = 0
manifest_metadata = []
for schema_type, filename, payload in invalid_samples:
    out_path = INVALID_DIR / filename
    if filename.endswith(".yaml"):
        out_path.write_text(yaml.dump(payload), encoding="utf-8")
    else:
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    manifest_metadata.append({"filename": filename, "expected_schema": schema_type})
    invalid_count += 1

(INVALID_DIR / "manifest.json").write_text(json.dumps(manifest_metadata, indent=2), encoding="utf-8")
print(f"Generated {invalid_count} invalid contract samples in {INVALID_DIR}")
