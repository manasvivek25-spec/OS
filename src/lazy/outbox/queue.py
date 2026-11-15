"""Outbox queue implementation with delay, undo window, approval state machine, rate limits, and attachment rules."""
from __future__ import annotations

import datetime
import json
import logging
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set
import uuid

from lazy.outbox.models import OutboxApproval, OutboxItem, KindType, StatusType, ApprovalMode

logger = logging.getLogger("lazy.outbox.queue")

FORBIDDEN_ATTACHMENT_PATTERNS = [
    "/etc/shadow",
    "/etc/sudoers",
    "/etc/lazy/keys",
    "/var/lib/lazy/secrets",
    "audit.log",
    "/root",
    "id_rsa",
    "id_ed25519",
]

MAX_ATTACHMENT_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB


class OutboxError(Exception):
    """Base exception for outbox operations."""


class RateLimitExceededError(OutboxError):
    """Raised when outbound hourly send limit is exceeded."""


class SecurityViolationError(OutboxError):
    """Raised when an outbox operation violates security policies (Rule F4, F6, F8)."""


class RecipientNotApprovedError(OutboxError):
    """Raised when sending to an unconfirmed recipient without explicit user approval."""


class OutboxQueue:
    """Queue managing outbound emails and chat messages with delay, approval, and rate limits."""

    def __init__(
        self,
        storage_dir: Optional[Path | str] = None,
        default_delay_seconds: int = 10,
        max_hourly_mail: int = 20,
        max_hourly_chat: int = 30,
    ):
        self.storage_dir = Path(storage_dir) if storage_dir else None
        self.default_delay_seconds = default_delay_seconds
        self.max_hourly_mail = max_hourly_mail
        self.max_hourly_chat = max_hourly_chat

        self._items: Dict[str, OutboxItem] = {}
        self._known_recipients: Set[str] = set()
        self._sent_timestamps: Dict[KindType, List[float]] = {"mail": [], "chat": []}

        if self.storage_dir:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            self._load_state()

    def add_known_recipient(self, recipient: str) -> None:
        """Register a known, trusted recipient address or handle."""
        self._known_recipients.add(recipient.strip().lower())

    def is_known_recipient(self, recipient: str) -> bool:
        """Check if recipient has been previously confirmed by the user."""
        return recipient.strip().lower() in self._known_recipients

    def _check_rate_limit(self, kind: KindType, current_epoch: float) -> None:
        """Enforce hourly outbound rate limits."""
        cutoff = current_epoch - 3600.0
        # Clean older timestamps
        self._sent_timestamps[kind] = [ts for ts in self._sent_timestamps[kind] if ts >= cutoff]

        limit = self.max_hourly_mail if kind == "mail" else self.max_hourly_chat
        if len(self._sent_timestamps[kind]) >= limit:
            raise RateLimitExceededError(
                f"Hourly rate limit exceeded for {kind} (maximum {limit} sends per hour)"
            )

    def validate_attachments(self, attachments: List[str]) -> None:
        """Validate safety and accessibility of message attachments."""
        for att in attachments:
            att_path = Path(att).resolve()
            att_str = str(att_path)

            # Check sensitive paths (Rule F4, F6)
            for forbidden in FORBIDDEN_ATTACHMENT_PATTERNS:
                if forbidden in att_str:
                    raise SecurityViolationError(
                        f"Attachment prohibited: '{att_str}' contains forbidden pattern '{forbidden}'"
                    )

            if not att_path.is_file():
                raise FileNotFoundError(f"Attachment file not found: {att_path}")

            if att_path.stat().st_size > MAX_ATTACHMENT_SIZE_BYTES:
                raise SecurityViolationError(
                    f"Attachment '{att_str}' exceeds maximum allowed size of 25MB"
                )

    def enqueue(
        self,
        kind: KindType,
        to: str,
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None,
        delay_seconds: Optional[int] = None,
        is_tainted: bool = False,
        now_dt: Optional[datetime.datetime] = None,
    ) -> OutboxItem:
        """Enqueue an outbound message with delay and initial pending status."""
        # Rule F8: Check taint tracking
        if is_tainted:
            raise SecurityViolationError(
                "Cannot enqueue outbound message: recipient or parameters are tainted (Rule F8)"
            )

        now = now_dt if now_dt else datetime.datetime.now(datetime.timezone.utc)
        self._check_rate_limit(kind, now.timestamp())
        self._sent_timestamps[kind].append(now.timestamp())

        att_list = attachments or []
        if att_list:
            self.validate_attachments(att_list)

        delay = delay_seconds if delay_seconds is not None else self.default_delay_seconds
        send_after_dt = now + datetime.timedelta(seconds=delay)

        item_id = f"outbox-{uuid.uuid4().hex[:12]}"
        created_str = now.isoformat()
        send_after_str = send_after_dt.isoformat()

        item = OutboxItem(
            id=item_id,
            kind=kind,
            to=to,
            subject=subject,
            body=body,
            attachments=att_list,
            created=created_str,
            send_after=send_after_str,
            status="pending",
            approvals=[],
        )

        # Validate schema contract
        item.validate()

        self._items[item_id] = item
        self._save_state()
        return item

    def approve(
        self,
        item_id: str,
        approver: str = "user",
        mode: ApprovalMode = "user_hud",
        confirm_new_recipient: bool = False,
        now_dt: Optional[datetime.datetime] = None,
    ) -> OutboxItem:
        """Approve a pending outbox item for dispatch after the undo window."""
        item = self._items.get(item_id)
        if not item:
            raise KeyError(f"Outbox item not found: {item_id}")

        if item.status == "cancelled":
            raise OutboxError(f"Cannot approve cancelled outbox item: {item_id}")
        if item.status == "sent":
            raise OutboxError(f"Outbox item already sent: {item_id}")

        # Check new-recipient approval policy
        if not self.is_known_recipient(item.to) and not confirm_new_recipient:
            raise RecipientNotApprovedError(
                f"Recipient '{item.to}' is not in known contacts; requires explicit confirmation"
            )

        # Auto-register as known recipient once confirmed
        self.add_known_recipient(item.to)

        ts = (now_dt if now_dt else datetime.datetime.now(datetime.timezone.utc)).isoformat()
        item.approvals.append(OutboxApproval(approver=approver, ts=ts, mode=mode))
        item.status = "approved"

        item.validate()
        self._save_state()
        return item

    def cancel(self, item_id: str, reason: str = "user_cancelled") -> OutboxItem:
        """Cancel an outbound message during its undo window (capability outbox.cancel)."""
        item = self._items.get(item_id)
        if not item:
            raise KeyError(f"Outbox item not found: {item_id}")

        if item.status == "sent":
            raise OutboxError(f"Cannot cancel item {item_id}: already sent outside undo window")

        item.status = "cancelled"
        item.validate()
        self._save_state()
        return item

    def process_ready(
        self,
        current_time: Optional[datetime.datetime] = None,
        dispatch_callback: Optional[Callable[[OutboxItem], bool]] = None,
    ) -> List[OutboxItem]:
        """Dispatch items that are approved and whose undo window has elapsed."""
        now = current_time if current_time else datetime.datetime.now(datetime.timezone.utc)
        dispatched: List[OutboxItem] = []

        for item in list(self._items.values()):
            if item.status != "approved":
                continue

            send_after_dt = datetime.datetime.fromisoformat(item.send_after)
            # Check if undo window has passed
            if now >= send_after_dt:
                success = True
                if dispatch_callback:
                    try:
                        success = bool(dispatch_callback(item))
                    except Exception as e:
                        logger.error("Failed to dispatch outbox item %s: %s", item.id, e)
                        success = False

                if success:
                    item.status = "sent"
                    item.validate()
                    self._sent_timestamps[item.kind].append(now.timestamp())
                    dispatched.append(item)

        if dispatched:
            self._save_state()

        return dispatched

    def get_item(self, item_id: str) -> Optional[OutboxItem]:
        """Fetch item by ID."""
        return self._items.get(item_id)

    def list_items(self, status: Optional[StatusType] = None) -> List[OutboxItem]:
        """List items, optionally filtered by status."""
        if status:
            return [it for it in self._items.values() if it.status == status]
        return list(self._items.values())

    def _save_state(self) -> None:
        """Persist outbox state to disk."""
        if not self.storage_dir:
            return
        state_file = self.storage_dir / "outbox.json"
        data = {
            "items": {item_id: item.to_dict() for item_id, item in self._items.items()},
            "known_recipients": list(self._known_recipients),
        }
        state_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _load_state(self) -> None:
        """Load outbox state from disk."""
        if not self.storage_dir:
            return
        state_file = self.storage_dir / "outbox.json"
        if not state_file.is_file():
            return
        try:
            data = json.loads(state_file.read_text(encoding="utf-8"))
            self._known_recipients = set(data.get("known_recipients", []))
            for item_id, raw in data.get("items", {}).items():
                approvals = [
                    OutboxApproval(approver=a["approver"], ts=a["ts"], mode=a["mode"])
                    for a in raw.get("approvals", [])
                ]
                self._items[item_id] = OutboxItem(
                    id=raw["id"],
                    kind=raw["kind"],
                    to=raw["to"],
                    subject=raw["subject"],
                    body=raw["body"],
                    attachments=raw.get("attachments", []),
                    created=raw["created"],
                    send_after=raw["send_after"],
                    status=raw["status"],
                    approvals=approvals,
                )
        except Exception as e:
            logger.error("Failed to load outbox state: %s", e)
