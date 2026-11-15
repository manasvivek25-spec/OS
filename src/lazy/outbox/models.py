"""Data model and contract compliance for Lazy OS OutboxItem."""
from __future__ import annotations

from dataclasses import dataclass, field
import datetime
import uuid
from typing import Any, Dict, List, Literal, Optional

from lazy.common.contracts import validate_contract

KindType = Literal["mail", "chat"]
StatusType = Literal["pending", "approved", "cancelled", "sent"]
ApprovalMode = Literal["user_hud", "user_text", "user_voice_override"]


@dataclass
class OutboxApproval:
    """Approval record for an outbox message."""
    approver: str
    ts: str
    mode: ApprovalMode

    def to_dict(self) -> Dict[str, Any]:
        return {
            "approver": self.approver,
            "ts": self.ts,
            "mode": self.mode,
        }


@dataclass
class OutboxItem:
    """Represents a queued outbound message with delay, undo window, and approvals."""
    id: str
    kind: KindType
    to: str
    subject: str
    body: str
    attachments: List[str]
    created: str
    send_after: str
    status: StatusType
    approvals: List[OutboxApproval] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "to": self.to,
            "subject": self.subject,
            "body": self.body,
            "attachments": list(self.attachments),
            "created": self.created,
            "send_after": self.send_after,
            "status": self.status,
            "approvals": [a.to_dict() for a in self.approvals],
        }

    def validate(self) -> None:
        """Validate against JSON schema contract docs/contracts/outbox_item.schema.json."""
        validate_contract("outbox_item", self.to_dict(), strict=True)
