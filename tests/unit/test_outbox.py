"""Unit tests for Lazy OS lazy-outbox service (Milestone M4.1).

Verifies:
- Strict JSON Schema contract compliance (outbox_item.schema.json).
- Delay and undo window:
  * Cancelling inside the undo window prevents dispatch.
  * Approving and dispatching after the window elapses succeeds.
- Approval state machine (pending -> approved -> sent, cancellation invariants).
- Hourly outbound rate limiting (RateLimitExceededError).
- New-recipient explicit confirmation requirement (RecipientNotApprovedError).
- Attachment safety verification (Rule F4, F6: blocks /etc/shadow, secrets, keys).
- Taint tracking rejection (Rule F8).
- Queue persistence across restarts.
"""
from __future__ import annotations

import datetime
from pathlib import Path
import pytest

from lazy.common.contracts import ContractValidationError
from lazy.outbox.models import OutboxItem, OutboxApproval
from lazy.outbox.queue import (
    OutboxQueue,
    OutboxError,
    RateLimitExceededError,
    SecurityViolationError,
    RecipientNotApprovedError,
)
from lazy.outbox.service import OutboxService


@pytest.fixture
def queue(tmp_path: Path) -> OutboxQueue:
    storage = tmp_path / "outbox_storage"
    return OutboxQueue(
        storage_dir=storage,
        default_delay_seconds=10,
        max_hourly_mail=3,
        max_hourly_chat=5,
    )


class TestOutboxContract:
    def test_schema_valid_outbox_item(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        item = OutboxItem(
            id="outbox-abc12345",
            kind="mail",
            to="supervisor@university.edu",
            subject="OS Project Track A Report",
            body="Here is the final evaluation report.",
            attachments=[],
            created=now.isoformat(),
            send_after=(now + datetime.timedelta(seconds=10)).isoformat(),
            status="pending",
            approvals=[],
        )
        # Should not raise
        item.validate()

    def test_schema_invalid_status_rejected(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        item = OutboxItem(
            id="outbox-bad001",
            kind="mail",
            to="user@test.org",
            subject="Test",
            body="Test",
            attachments=[],
            created=now.isoformat(),
            send_after=now.isoformat(),
            status="flying",  # Invalid status!
            approvals=[],
        )
        with pytest.raises(ContractValidationError):
            item.validate()


class TestDelayAndUndoWindow:
    def test_cancel_inside_window_prevents_dispatch(self, queue: OutboxQueue):
        """Exit test requirement: cancel inside the window is tested."""
        t0 = datetime.datetime(2026, 11, 15, 12, 0, 0, tzinfo=datetime.timezone.utc)

        # 1. Enqueue with 10s delay
        item = queue.enqueue(
            kind="mail",
            to="colleague@domain.com",
            subject="Draft proposal",
            body="Check out this draft",
            delay_seconds=10,
            now_dt=t0,
        )
        assert item.status == "pending"

        # 2. Cancel at t = 3s (inside 10s window)
        t_cancel = t0 + datetime.timedelta(seconds=3)
        cancelled_item = queue.cancel(item.id)
        assert cancelled_item.status == "cancelled"

        # 3. Advance time to t = 20s (well past send_after)
        t_past = t0 + datetime.timedelta(seconds=20)
        dispatched = queue.process_ready(current_time=t_past)

        # Cancelled message must NEVER be dispatched!
        assert len(dispatched) == 0
        refreshed = queue.get_item(item.id)
        assert refreshed.status == "cancelled"

    def test_send_after_window_elapses(self, queue: OutboxQueue):
        """Exit test requirement: send after the window is tested."""
        t0 = datetime.datetime(2026, 11, 15, 12, 0, 0, tzinfo=datetime.timezone.utc)

        # 1. Enqueue with 10s delay
        item = queue.enqueue(
            kind="mail",
            to="advisor@university.edu",
            subject="Release notification",
            body="Lazy OS v0 ready",
            delay_seconds=10,
            now_dt=t0,
        )
        assert item.status == "pending"

        # 2. Approve message at t = 2s
        queue.approve(item.id, approver="human_user", mode="user_hud", confirm_new_recipient=True, now_dt=t0)
        assert queue.get_item(item.id).status == "approved"

        # 3. Attempt process_ready at t = 5s (still within 10s undo window)
        t_early = t0 + datetime.timedelta(seconds=5)
        early_dispatched = queue.process_ready(current_time=t_early)
        assert len(early_dispatched) == 0  # Not yet ready!

        # 4. Advance time past window: t = 11s
        t_ready = t0 + datetime.timedelta(seconds=11)
        dispatched = queue.process_ready(current_time=t_ready)

        assert len(dispatched) == 1
        assert dispatched[0].id == item.id
        assert dispatched[0].status == "sent"

        # 5. Cannot cancel after sending
        with pytest.raises(OutboxError, match="already sent"):
            queue.cancel(item.id)


class TestApprovalStateMachine:
    def test_unapproved_pending_items_not_sent(self, queue: OutboxQueue):
        t0 = datetime.datetime(2026, 11, 15, 10, 0, 0, tzinfo=datetime.timezone.utc)
        item = queue.enqueue(kind="chat", to="@room:matrix.org", subject="", body="hi", delay_seconds=5, now_dt=t0)

        # Time passes past delay, but item is still 'pending' (not approved)
        t_future = t0 + datetime.timedelta(seconds=30)
        dispatched = queue.process_ready(current_time=t_future)
        assert len(dispatched) == 0
        assert queue.get_item(item.id).status == "pending"

    def test_cannot_approve_cancelled_item(self, queue: OutboxQueue):
        item = queue.enqueue(kind="chat", to="@user", subject="", body="msg")
        queue.cancel(item.id)
        with pytest.raises(OutboxError, match="Cannot approve cancelled"):
            queue.approve(item.id, confirm_new_recipient=True)


class TestRateLimiting:
    def test_hourly_send_rate_limit(self, queue: OutboxQueue):
        t0 = datetime.datetime(2026, 11, 15, 14, 0, 0, tzinfo=datetime.timezone.utc)
        # max_hourly_mail is configured to 3 in fixture
        for i in range(3):
            queue.enqueue(kind="mail", to=f"recip{i}@test.org", subject="Sub", body="Body", now_dt=t0)

        # 4th message within the same hour exceeds limit
        with pytest.raises(RateLimitExceededError, match="Hourly rate limit exceeded"):
            queue.enqueue(kind="mail", to="recip4@test.org", subject="Sub", body="Body", now_dt=t0)


class TestNewRecipientPolicy:
    def test_unconfirmed_recipient_requires_confirmation(self, queue: OutboxQueue):
        item = queue.enqueue(kind="mail", to="stranger@suspicious.net", subject="Hello", body="Msg")

        # Approving without confirmation raises RecipientNotApprovedError
        with pytest.raises(RecipientNotApprovedError, match="not in known contacts"):
            queue.approve(item.id, confirm_new_recipient=False)

        # Approving with explicit confirmation succeeds
        approved = queue.approve(item.id, confirm_new_recipient=True)
        assert approved.status == "approved"
        # Subsequent sends to this recipient do not require extra confirmation
        assert queue.is_known_recipient("stranger@suspicious.net")


class TestAttachmentRules:
    def test_valid_attachment_allowed(self, queue: OutboxQueue, tmp_path: Path):
        report_file = tmp_path / "report.pdf"
        report_file.write_text("dummy pdf binary content", encoding="utf-8")

        item = queue.enqueue(
            kind="mail",
            to="user@test.org",
            subject="Report",
            body="See attached",
            attachments=[str(report_file)],
        )
        assert len(item.attachments) == 1

    def test_forbidden_sensitive_paths_blocked(self, queue: OutboxQueue):
        # Attempting to attach /etc/shadow or secret keys (Rule F4, F6)
        with pytest.raises(SecurityViolationError, match="Attachment prohibited"):
            queue.enqueue(
                kind="mail",
                to="exfil@evil.org",
                subject="Shadow",
                body="Secret",
                attachments=["/etc/shadow"],
            )

        with pytest.raises(SecurityViolationError, match="Attachment prohibited"):
            queue.enqueue(
                kind="mail",
                to="exfil@evil.org",
                subject="Audit",
                body="Log",
                attachments=["/var/log/lazy/audit.log"],
            )

    def test_missing_attachment_raises(self, queue: OutboxQueue, tmp_path: Path):
        nonexistent = tmp_path / "ghost.png"
        with pytest.raises(FileNotFoundError):
            queue.enqueue(
                kind="mail",
                to="user@test.org",
                subject="Sub",
                body="Body",
                attachments=[str(nonexistent)],
            )


class TestTaintTrackingIntegration:
    def test_tainted_parameters_rejected(self, queue: OutboxQueue):
        # Rule F8: tainted recipients/destinations cannot be queued
        with pytest.raises(SecurityViolationError, match="tainted"):
            queue.enqueue(
                kind="mail",
                to="injected@attacker.com",
                subject="Leaked",
                body="Tainted text",
                is_tainted=True,
            )


class TestPersistenceAndService:
    def test_queue_persistence(self, tmp_path: Path):
        storage = tmp_path / "outbox_disk"
        q1 = OutboxQueue(storage_dir=storage)
        item = q1.enqueue(kind="mail", to="persisted@domain.com", subject="Persist", body="Body")
        q1.approve(item.id, confirm_new_recipient=True)

        # Reload queue from same directory
        q2 = OutboxQueue(storage_dir=storage)
        reloaded = q2.get_item(item.id)
        assert reloaded is not None
        assert reloaded.status == "approved"
        assert reloaded.to == "persisted@domain.com"
        assert q2.is_known_recipient("persisted@domain.com")

    def test_service_rpc_interface(self, tmp_path: Path):
        service = OutboxService(storage_dir=tmp_path / "rpc_storage")
        enq_res = service.handle_enqueue({
            "kind": "chat",
            "to": "#general",
            "body": "Hello team",
        })
        assert enq_res["status"] == "ok"
        item_id = enq_res["item"]["id"]

        # Approve
        app_res = service.handle_approve({
            "item_id": item_id,
            "confirm_new_recipient": True,
        })
        assert app_res["status"] == "ok"
        assert app_res["item"]["status"] == "approved"

        # List
        list_res = service.handle_list({"status": "approved"})
        assert len(list_res["items"]) == 1
