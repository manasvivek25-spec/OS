"""Hash-chained append-only audit log implementation."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


GENESIS_HASH = "0" * 64


def canonical_json(data: Any) -> str:
    """Produce deterministic canonical JSON string."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_hash(index: int, timestamp: str, event_type: str, actor: str, payload: Any, prev_hash: str) -> str:
    """Compute SHA-256 hash over canonical representation of record contents."""
    content = {
        "index": index,
        "timestamp": timestamp,
        "event_type": event_type,
        "actor": actor,
        "payload": payload,
        "prev_hash": prev_hash,
    }
    raw = canonical_json(content).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class AuditRecord:
    """Immutable audit record within the hash-chain."""

    def __init__(
        self,
        index: int,
        timestamp: str,
        event_type: str,
        actor: str,
        payload: Any,
        prev_hash: str,
        record_hash: str,
    ):
        self.index = index
        self.timestamp = timestamp
        self.event_type = event_type
        self.actor = actor
        self.payload = payload
        self.prev_hash = prev_hash
        self.hash = record_hash

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "actor": self.actor,
            "payload": self.payload,
            "prev_hash": self.prev_hash,
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AuditRecord:
        required = ["index", "timestamp", "event_type", "actor", "payload", "prev_hash", "hash"]
        for key in required:
            if key not in data:
                raise ValueError(f"Missing required audit record field: {key}")
        return cls(
            index=data["index"],
            timestamp=data["timestamp"],
            event_type=data["event_type"],
            actor=data["actor"],
            payload=data["payload"],
            prev_hash=data["prev_hash"],
            record_hash=data["hash"],
        )


class AuditLedger:
    """Append-only audit ledger backed by a persistent hash chain file."""

    def __init__(self, log_path: Path | str):
        self.log_path = Path(log_path)
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            os.chmod(str(self.log_path.parent), 0o777)
        except Exception:
            pass
        self._last_index = -1
        self._last_hash = GENESIS_HASH
        self._init_state()

    def _init_state(self) -> None:
        """Scan existing log to establish head index and hash."""
        if not self.log_path.is_file():
            return

        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                record_data = json.loads(line)
                self._last_index = record_data["index"]
                self._last_hash = record_data["hash"]

    @property
    def last_index(self) -> int:
        return self._last_index

    @property
    def last_hash(self) -> str:
        return self._last_hash

    def append(self, event_type: str, actor: str, payload: Any, timestamp: Optional[str] = None) -> AuditRecord:
        """Append a new record to the hash chain and flush to disk."""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()

        new_index = self._last_index + 1
        new_hash = compute_hash(
            index=new_index,
            timestamp=timestamp,
            event_type=event_type,
            actor=actor,
            payload=payload,
            prev_hash=self._last_hash,
        )

        record = AuditRecord(
            index=new_index,
            timestamp=timestamp,
            event_type=event_type,
            actor=actor,
            payload=payload,
            prev_hash=self._last_hash,
            record_hash=new_hash,
        )

        line = canonical_json(record.to_dict()) + "\n"
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())

        try:
            os.chmod(str(self.log_path), 0o666)
        except Exception:
            pass

        self._last_index = new_index
        self._last_hash = new_hash
        return record

    def read_all(self) -> List[AuditRecord]:
        """Read all records from log."""
        if not self.log_path.is_file():
            return []
        records = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(AuditRecord.from_dict(json.loads(line)))
        return records
