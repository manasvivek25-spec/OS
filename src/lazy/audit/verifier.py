"""Cryptographic verifier for Lazy OS audit hash-chains."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Tuple

from lazy.audit.ledger import GENESIS_HASH, AuditRecord, compute_hash


class VerificationResult:
    """Outcome of an audit log verification run."""

    def __init__(self, is_valid: bool, reason: Optional[str] = None, failed_index: Optional[int] = None, total_records: int = 0):
        self.is_valid = is_valid
        self.reason = reason
        self.failed_index = failed_index
        self.total_records = total_records

    def __bool__(self) -> bool:
        return self.is_valid


def verify_audit_log(log_path: Path | str, expected_count: Optional[int] = None) -> VerificationResult:
    """Verify integrity of the audit log file against hash-chain rules.

    Detects modifications, deletions, reorderings, truncations, and invalid syntax.
    """
    path = Path(log_path)
    if not path.is_file():
        if expected_count is not None and expected_count > 0:
            return VerificationResult(False, "Audit log file does not exist but records were expected", 0, 0)
        return VerificationResult(True, "Empty log is valid", None, 0)

    expected_index = 0
    expected_prev_hash = GENESIS_HASH
    line_number = 0

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line_number += 1
            raw = line.strip()
            if not raw:
                continue

            try:
                record_data = json.loads(raw)
                record = AuditRecord.from_dict(record_data)
            except Exception as err:
                return VerificationResult(
                    False,
                    f"Syntax/schema corruption at line {line_number}: {str(err)}",
                    expected_index,
                    line_number - 1,
                )

            # Check 1: Sequence index
            if record.index != expected_index:
                if record.index < expected_index:
                    return VerificationResult(
                        False,
                        f"Reordering/Duplication detected: expected index {expected_index}, found {record.index}",
                        record.index,
                        line_number - 1,
                    )
                else:
                    return VerificationResult(
                        False,
                        f"Deletion/Gap detected: expected index {expected_index}, found {record.index}",
                        expected_index,
                        line_number - 1,
                    )

            # Check 2: Prev hash link
            if record.prev_hash != expected_prev_hash:
                return VerificationResult(
                    False,
                    f"Hash link broken at index {record.index}: prev_hash mismatch. Expected {expected_prev_hash}, got {record.prev_hash}",
                    record.index,
                    line_number - 1,
                )

            # Check 3: Content hash integrity
            recalculated = compute_hash(
                index=record.index,
                timestamp=record.timestamp,
                event_type=record.event_type,
                actor=record.actor,
                payload=record.payload,
                prev_hash=record.prev_hash,
            )
            if record.hash != recalculated:
                return VerificationResult(
                    False,
                    f"Tampering detected at index {record.index}: content hash mismatch. Recorded {record.hash}, calculated {recalculated}",
                    record.index,
                    line_number - 1,
                )

            expected_prev_hash = record.hash
            expected_index += 1

    # Check 4: Truncation check against expected count if specified
    if expected_count is not None and expected_index != expected_count:
        return VerificationResult(
            False,
            f"Truncation detected: expected {expected_count} records, found {expected_index}",
            expected_index,
            expected_index,
        )

    return VerificationResult(True, None, None, expected_index)
