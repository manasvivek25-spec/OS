"""Generate recorded-intent fixtures for all 37 Lazy OS capabilities."""
import json
from pathlib import Path
import jsonschema
import yaml

from lazy.common.contracts import validate_contract

REPO_ROOT = Path(__file__).resolve().parent.parent
CAPS_DIR = REPO_ROOT / "config" / "capabilities"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "intents"
FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

# Definition of sample params and queries for all 37 capabilities
FIXTURE_DATA = {
    "chat.read": {
        "query": "read recent chats",
        "params": {"limit": 10},
        "rationale": "Read recent messages from chat service",
    },
    "chat.send": {
        "query": "send chat to alice saying hello",
        "params": {"to": "alice", "body": "hello"},
        "rationale": "Send instant message to alice",
    },
    "code.run": {
        "query": "run script in sandbox",
        "params": {"command": "python3 -c 'print(42)'", "timeout": 30},
        "rationale": "Execute transient code in sandbox",
    },
    "code.write": {
        "query": "write python script",
        "params": {"path": "/home/user/test.py", "content": "print('hello')\n"},
        "rationale": "Write script code to file",
    },
    "doc.create_docx": {
        "query": "create docx document",
        "params": {"path": "/home/user/doc.docx", "content": "# Heading\nParagraph"},
        "rationale": "Generate docx file from content",
    },
    "doc.create_markdown": {
        "query": "create markdown document",
        "params": {"path": "/home/user/notes.md", "content": "# Notes\nMeeting summary"},
        "rationale": "Create markdown document file",
    },
    "fs.copy": {
        "query": "copy file from source to dest",
        "params": {"src": "/home/user/source.txt", "dest": "/home/user/dest.txt"},
        "rationale": "Copy file to new location",
    },
    "fs.delete": {
        "query": "delete temporary file",
        "params": {"path": "/tmp/temp.txt"},
        "rationale": "Remove file from filesystem",
    },
    "fs.list": {
        "query": "list files in home directory",
        "params": {"path": "/home/user"},
        "rationale": "List directory contents",
    },
    "fs.move": {
        "query": "move file from old to new location",
        "params": {"src": "/tmp/old.txt", "dest": "/tmp/new.txt"},
        "rationale": "Move or rename file",
    },
    "fs.read": {
        "query": "read file notes.txt",
        "params": {"path": "/home/user/notes.txt"},
        "rationale": "Read file contents",
    },
    "fs.write": {
        "query": "write data to file",
        "params": {"path": "/home/user/output.txt", "content": "Processed output\n"},
        "rationale": "Write string contents to target file",
    },
    "hw.backlight_set": {
        "query": "set display brightness to 80",
        "params": {"brightness": 80},
        "rationale": "Adjust display backlight brightness percentage",
    },
    "hw.governor_set": {
        "query": "set cpu governor to performance",
        "params": {"governor": "performance"},
        "rationale": "Set CPU frequency scaling governor",
    },
    "hw.power_profile_set": {
        "query": "set power profile to balanced",
        "params": {"profile": "balanced"},
        "rationale": "Switch system power profile",
    },
    "hw.rfkill_set": {
        "query": "unblock wifi radio",
        "params": {"subsystem": "wlan", "state": "unblock"},
        "rationale": "Configure RF radio kill switch state",
    },
    "hw.usb_authorize": {
        "query": "authorize usb device 1-1",
        "params": {"device_id": "1-1"},
        "rationale": "Authorize USB device access",
    },
    "hw.usb_list": {
        "query": "list connected usb devices",
        "params": {},
        "rationale": "Enumerate connected USB devices",
    },
    "hw.volume_set": {
        "query": "set master audio volume to 50",
        "params": {"volume": 50},
        "rationale": "Adjust audio output volume percentage",
    },
    "mail.draft": {
        "query": "draft email to colleague",
        "params": {"to": "colleague@example.com", "subject": "Draft", "body": "Notes for review"},
        "rationale": "Create email draft in Maildir",
    },
    "mail.list": {
        "query": "list emails in inbox",
        "params": {"folder": "INBOX"},
        "rationale": "List messages in mail folder",
    },
    "mail.read": {
        "query": "read email message 101",
        "params": {"message_id": "msg-101"},
        "rationale": "Read email message by ID",
    },
    "mail.send": {
        "query": "send email to partner",
        "params": {"to": "partner@example.com", "subject": "Project", "body": "Milestone completed", "attachments": []},
        "rationale": "Queue email in outbox for delivery",
    },
    "outbox.cancel": {
        "query": "cancel pending outbox item",
        "params": {"item_id": "outbox-001"},
        "rationale": "Cancel pending outbox delivery before expiry",
    },
    "sys.logs_read": {
        "query": "read logs for lazy-gateway",
        "params": {"service": "lazy-gateway", "lines": 50},
        "rationale": "Fetch recent service journal logs",
    },
    "sys.process_list": {
        "query": "list running system processes",
        "params": {},
        "rationale": "Retrieve snapshot of active processes",
    },
    "sys.process_signal": {
        "query": "terminate process 4321",
        "params": {"pid": 4321, "signal": "SIGTERM"},
        "rationale": "Send signal to process",
    },
    "sys.service_restart": {
        "query": "restart lazy-policy service",
        "params": {"service": "lazy-policy"},
        "rationale": "Restart systemd unit",
    },
    "sys.service_status": {
        "query": "check status of lazy-gateway",
        "params": {"service": "lazy-gateway"},
        "rationale": "Query systemd unit active status",
    },
    "sys.setting_set": {
        "query": "set system setting timezone to UTC",
        "params": {"key": "system.timezone", "value": "UTC"},
        "rationale": "Update persistent system configuration setting",
    },
    "task.undo": {
        "query": "undo last task execution",
        "params": {"task_id": "task-test-001"},
        "rationale": "Roll back previous task using snapshot",
    },
    "web.click": {
        "query": "click submit button on page",
        "params": {"element_id": "btn-submit"},
        "rationale": "Click DOM element in isolated browser",
    },
    "web.download": {
        "query": "download file from web",
        "params": {"url": "https://example.org/archive.tar.gz", "dest_filename": "archive.tar.gz"},
        "rationale": "Download remote file into isolated quarantine",
    },
    "web.fill": {
        "query": "fill input field username",
        "params": {"element_id": "username-input", "value": "testuser"},
        "rationale": "Enter text into form field in isolated browser",
    },
    "web.navigate": {
        "query": "navigate to example.org",
        "params": {"url": "https://example.org"},
        "rationale": "Navigate isolated browser to target URL",
    },
    "web.read": {
        "query": "read webpage text",
        "params": {"url": "https://example.org"},
        "rationale": "Extract structured readable text from webpage",
    },
    "web.submit": {
        "query": "submit search form",
        "params": {"form_id": "search-form"},
        "rationale": "Submit form in isolated browser session",
    },
}

def generate_and_validate():
    manifest_files = sorted(CAPS_DIR.glob("*.yaml"))
    assert len(manifest_files) == 37, f"Expected 37 manifests, found {len(manifest_files)}"
    assert len(FIXTURE_DATA) == 37, f"Expected 37 fixture entries, found {len(FIXTURE_DATA)}"

    created = 0
    for mf in manifest_files:
        cap_name = mf.stem
        with open(mf, "r", encoding="utf-8") as f:
            manifest = yaml.safe_load(f)

        assert cap_name in FIXTURE_DATA, f"Missing fixture data for {cap_name}"
        data = FIXTURE_DATA[cap_name]
        params = data["params"]

        # Validate params against capability manifest schema
        params_schema = manifest.get("params_schema", {})
        jsonschema.validate(instance=params, schema=params_schema)

        # Build Intent step
        intent = {
            "id": f"intent-{cap_name.replace('.', '-')}-fix",
            "ts": "2026-11-15T12:00:00Z",
            "task_id": "task-fixture-001",
            "requester": "text",
            "capability": cap_name,
            "params": params,
            "provenance": [
                {
                    "source": "user",
                    "trusted": True,
                    "detail": f"Recorded fixture for {cap_name}",
                }
            ],
        }
        validate_contract("intent", intent, strict=True)

        # Build Plan
        plan = {
            "id": f"plan-{cap_name.replace('.', '-')}-fix",
            "steps": [intent],
            "rationale": data["rationale"],
        }
        validate_contract("plan", plan, strict=True)

        fixture_obj = {
            "capability": cap_name,
            "query": data["query"],
            "plan": plan,
        }

        out_path = FIXTURES_DIR / f"{cap_name}.json"
        out_path.write_text(json.dumps(fixture_obj, indent=2), encoding="utf-8")
        created += 1

    print(f"Successfully generated and validated {created} fixtures in {FIXTURES_DIR}")

if __name__ == "__main__":
    generate_and_validate()
