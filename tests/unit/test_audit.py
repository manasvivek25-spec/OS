"""Unit tests for lazy-audit hash chain and verifier (Rule F7).

Exit criteria M1.1: hash chain, verifier, tamper tests (modify, delete, reorder, truncate) - all detected.
"""

import json
from pathlib import Path
import pytest

from lazy.audit import AuditLedger, verify_audit_log


@pytest.fixture
def temp_ledger(tmp_path: Path) -> AuditLedger:
    log_file = tmp_path / "test_audit.log"
    return AuditLedger(log_file)


def test_audit_hash_chain_append_and_verify(temp_ledger: AuditLedger):
    """[F7] Test standard append-only hash chain construction and successful verification."""
    r0 = temp_ledger.append("intent.proposed", "planner", {"intent_id": "i-001"})
    r1 = temp_ledger.append("policy.decision", "policy", {"verdict": "allow"})
    r2 = temp_ledger.append("broker.fs", "broker-fs", {"action": "write", "path": "/test.txt"})

    assert r0.index == 0
    assert r1.index == 1
    assert r2.index == 2

    assert r1.prev_hash == r0.hash
    assert r2.prev_hash == r1.hash

    result = verify_audit_log(temp_ledger.log_path, expected_count=3)
    assert result.is_valid
    assert result.total_records == 3
    assert result.failed_index is None


def test_tamper_detect_modify(temp_ledger: AuditLedger):
    """[F7] Exit criterion: Altering any field in an existing record must be detected."""
    temp_ledger.append("intent.proposed", "planner", {"intent_id": "i-001"})
    temp_ledger.append("policy.decision", "policy", {"verdict": "deny"})
    temp_ledger.append("broker.fs", "broker-fs", {"path": "/etc/shadow"})

    # Tamper: change verdict from 'deny' to 'allow' in record 1
    lines = temp_ledger.log_path.read_text(encoding="utf-8").splitlines()
    data = json.loads(lines[1])
    data["payload"]["verdict"] = "allow"
    lines[1] = json.dumps(data)
    temp_ledger.log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = verify_audit_log(temp_ledger.log_path)
    assert not result.is_valid
    assert result.failed_index in (0, 1)
    assert "Tampering detected at index 1" in result.reason


def test_tamper_detect_delete_middle(temp_ledger: AuditLedger):
    """[F7] Exit criterion: Deleting a record from the middle must break index and hash chain."""
    temp_ledger.append("intent.0", "planner", {})
    temp_ledger.append("intent.1", "planner", {})
    temp_ledger.append("intent.2", "planner", {})

    # Delete index 1
    lines = temp_ledger.log_path.read_text(encoding="utf-8").splitlines()
    del lines[1]
    temp_ledger.log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = verify_audit_log(temp_ledger.log_path)
    assert not result.is_valid
    assert "Deletion/Gap detected" in result.reason or "Hash link broken" in result.reason


def test_tamper_detect_delete_first(temp_ledger: AuditLedger):
    """[F7] Exit criterion: Deleting genesis record must be detected."""
    temp_ledger.append("intent.0", "planner", {})
    temp_ledger.append("intent.1", "planner", {})

    lines = temp_ledger.log_path.read_text(encoding="utf-8").splitlines()
    del lines[0]
    temp_ledger.log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = verify_audit_log(temp_ledger.log_path)
    assert not result.is_valid
    assert result.failed_index in (0, 1)


def test_tamper_detect_reorder(temp_ledger: AuditLedger):
    """[F7] Exit criterion: Swapping two records must be detected immediately."""
    temp_ledger.append("step.0", "system", {"seq": 0})
    temp_ledger.append("step.1", "system", {"seq": 1})
    temp_ledger.append("step.2", "system", {"seq": 2})

    lines = temp_ledger.log_path.read_text(encoding="utf-8").splitlines()
    # Swap record 1 and 2
    lines[1], lines[2] = lines[2], lines[1]
    temp_ledger.log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = verify_audit_log(temp_ledger.log_path)
    assert not result.is_valid
    assert any(term in result.reason for term in ["Reordering", "Gap", "Hash link", "Tampering"])


def test_tamper_detect_truncate(temp_ledger: AuditLedger):
    """[F7] Exit criterion: Truncating the log when expected count is known must be detected."""
    for i in range(5):
        temp_ledger.append(f"event.{i}", "agent", {"i": i})

    # File truncated to 3 records
    lines = temp_ledger.log_path.read_text(encoding="utf-8").splitlines()
    temp_ledger.log_path.write_text("\n".join(lines[:3]) + "\n", encoding="utf-8")

    result = verify_audit_log(temp_ledger.log_path, expected_count=5)
    assert not result.is_valid
    assert "Truncation detected" in result.reason


def test_tamper_detect_insertion(temp_ledger: AuditLedger):
    """[F7] Exit criterion: Inserting an unauthorized fabricated record breaks hash link."""
    temp_ledger.append("event.0", "agent", {})
    temp_ledger.append("event.1", "agent", {})

    lines = temp_ledger.log_path.read_text(encoding="utf-8").splitlines()
    fabricated = json.dumps({
        "index": 1,
        "timestamp": "2026-11-15T12:00:00Z",
        "event_type": "fake",
        "actor": "attacker",
        "payload": {},
        "prev_hash": "a" * 64,
        "hash": "b" * 64,
    })
    lines.insert(1, fabricated)
    temp_ledger.log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = verify_audit_log(temp_ledger.log_path)
    assert not result.is_valid


def test_tamper_detect_corrupt_syntax(temp_ledger: AuditLedger):
    """[F7] Malformed JSON lines must be caught with line corruption errors."""
    temp_ledger.append("event.0", "agent", {})
    with open(temp_ledger.log_path, "a", encoding="utf-8") as f:
        f.write("{NOT_VALID_JSON}\n")

    result = verify_audit_log(temp_ledger.log_path)
    assert not result.is_valid
    assert "Syntax/schema corruption" in result.reason
