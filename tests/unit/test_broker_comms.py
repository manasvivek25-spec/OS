"""Unit tests for Lazy OS communications broker (lazy-broker-comms, Milestone M4.2).

Verifies:
- Maildir driver (inbox, drafts, sent, RFC 822 parsing, Rule F3 labelled data).
- SMTP sink driver (delivery capture for offline testing).
- Local chat fixture driver (channel messaging, Rule F3 labelled data).
- External drivers disabled by default (IMAP/SMTP, Telegram raise DisabledDriverError).
- CommsBroker capabilities:
  * L0: mail.list, mail.read, chat.read
  * L1: mail.draft
  * L3: mail.send, chat.send (strictly routed through lazy-outbox queue, Rule F8)
- End-to-end outbox approval and delivery via dispatch callback.
- Taint tracking rejection for outbound communications (Rule F8).
"""
from __future__ import annotations

import datetime
from pathlib import Path
import pytest

from lazy.brokers.comms_broker import (
    CommsBroker,
    MaildirDriver,
    SMTPSinkDriver,
    LocalChatDriver,
    DisabledDriverError,
)
from lazy.outbox.queue import OutboxQueue, SecurityViolationError


@pytest.fixture
def comms_env(tmp_path: Path):
    maildir_path = tmp_path / "maildir"
    outbox_storage = tmp_path / "outbox"
    outbox = OutboxQueue(storage_dir=outbox_storage, default_delay_seconds=5)
    broker = CommsBroker(maildir_root=maildir_path, outbox=outbox, enable_real_comms=False)
    return broker, maildir_path, outbox


class TestMaildirDriver:
    def test_deliver_and_list_messages(self, tmp_path: Path):
        driver = MaildirDriver(tmp_path / "mail")
        driver.deliver_message(
            to="user@lazyos.local",
            subject="Welcome to Lazy OS",
            body="Your system is configured and ready.",
            sender="admin@lazyos.local",
        )

        messages = driver.list_messages("inbox")
        assert len(messages) == 1
        assert messages[0]["subject"] == "Welcome to Lazy OS"
        assert messages[0]["from"] == "admin@lazyos.local"

    def test_read_message_and_rule_f3_labelling(self, tmp_path: Path):
        driver = MaildirDriver(tmp_path / "mail")
        msg_id = driver.deliver_message(
            to="user@lazyos.local",
            subject="Security Notice",
            body="Check your audit log integrity.",
            sender="security@lazyos.local",
        )

        msg = driver.read_message(msg_id, "inbox")
        assert msg["subject"] == "Security Notice"
        assert "Check your audit log integrity." in msg["body"]

        # Rule F3 check
        assert msg["untrusted_data"] is True
        assert "=== BEGIN UNTRUSTED EMAIL" in msg["labelled_text"]
        assert "=== END UNTRUSTED EMAIL ==="

    def test_save_draft(self, tmp_path: Path):
        driver = MaildirDriver(tmp_path / "mail")
        draft_id = driver.save_draft(
            to="professor@university.edu",
            subject="Track A Submission",
            body="Here is the final artifact.",
        )

        drafts = driver.list_messages("drafts")
        assert len(drafts) == 1
        assert drafts[0]["subject"] == "Track A Submission"


class TestLocalChatDriver:
    def test_post_and_read_messages(self):
        chat = LocalChatDriver()
        chat.post_message(channel="#dev", body="Starting M4.2 comms verification", author="alice")
        chat.post_message(channel="#dev", body="Tests look clean", author="bob")

        msgs = chat.read_messages(channel="#dev", limit=10)
        assert len(msgs) == 2
        assert msgs[0]["author"] == "alice"
        assert msgs[1]["body"] == "Tests look clean"

        # Rule F3 check
        assert msgs[0]["untrusted_data"] is True
        assert "=== BEGIN UNTRUSTED CHAT" in msgs[0]["labelled_text"]


class TestDisabledDriversByDefault:
    def test_imap_and_telegram_disabled_by_default(self, comms_env):
        broker, _, _ = comms_env
        with pytest.raises(DisabledDriverError, match="disabled by default"):
            broker.imap_driver.check_enabled()

        with pytest.raises(DisabledDriverError, match="disabled by default"):
            broker.telegram_driver.check_enabled()


class TestCommsBrokerCapabilities:
    def test_mail_list_and_read(self, comms_env):
        broker, _, _ = comms_env
        broker.maildir_driver.deliver_message(
            to="user@lazyos.local",
            subject="Kernel release 6.6 LTS",
            body="New Btrfs fixes available.",
        )

        list_res = broker.execute("mail.list", {"folder": "inbox"})
        assert list_res["status"] == "ok"
        assert list_res["result"]["count"] == 1
        msg_id = list_res["result"]["messages"][0]["message_id"]

        read_res = broker.execute("mail.read", {"message_id": msg_id, "folder": "inbox"})
        assert read_res["status"] == "ok"
        assert read_res["result"]["subject"] == "Kernel release 6.6 LTS"
        assert read_res["result"]["untrusted_data"] is True

    def test_mail_draft(self, comms_env):
        broker, _, _ = comms_env
        res = broker.execute("mail.draft", {
            "to": "team@lazyos.local",
            "subject": "Sprint plan",
            "body": "Phase 4 starts today.",
        })
        assert res["status"] == "ok"
        assert res["result"]["folder"] == "drafts"

    def test_mail_send_routes_through_outbox(self, comms_env):
        """Rule F8: mail.send (Tier L3) must route through lazy-outbox queue."""
        broker, _, outbox = comms_env
        res = broker.execute("mail.send", {
            "to": "recipient@domain.org",
            "subject": "Important update",
            "body": "Please review changes.",
        })

        assert res["status"] == "ok"
        assert res["result"]["status"] == "queued_in_outbox"
        assert res["result"]["requires_approval"] is True
        item_id = res["result"]["outbox_item_id"]

        # Check in Outbox queue
        item = outbox.get_item(item_id)
        assert item is not None
        assert item.status == "pending"
        assert item.kind == "mail"
        assert item.to == "recipient@domain.org"

    def test_chat_read_and_send_routes_through_outbox(self, comms_env):
        """Rule F8: chat.send (Tier L3) must route through lazy-outbox queue."""
        broker, _, outbox = comms_env
        broker.chat_driver.post_message(channel="#general", body="Hello world", author="sys")

        read_res = broker.execute("chat.read", {"channel": "#general", "limit": 5})
        assert read_res["status"] == "ok"
        assert read_res["result"]["count"] == 1

        send_res = broker.execute("chat.send", {
            "to": "#general",
            "body": "Assistant online and monitored.",
        })
        assert send_res["status"] == "ok"
        assert send_res["result"]["status"] == "queued_in_outbox"
        item_id = send_res["result"]["outbox_item_id"]

        item = outbox.get_item(item_id)
        assert item is not None
        assert item.kind == "chat"
        assert item.status == "pending"


class TestEndToEndOutboxDelivery:
    def test_email_outbox_approval_and_smtp_delivery(self, comms_env):
        broker, _, outbox = comms_env

        # 1. Enqueue mail via broker
        res = broker.execute("mail.send", {
            "to": "client@partner.com",
            "subject": "Invoice 1042",
            "body": "Thank you for your business.",
        })
        assert res["status"] == "ok"
        item_id = res["result"]["outbox_item_id"]

        # 2. Approve in Outbox
        outbox.approve(item_id, approver="user", mode="user_hud", confirm_new_recipient=True)
        item = outbox.get_item(item_id)
        assert item.status == "approved"

        # 3. Deliver after undo window has elapsed
        send_after_dt = datetime.datetime.fromisoformat(item.send_after)
        t_after = send_after_dt + datetime.timedelta(seconds=2)
        dispatched = outbox.process_ready(
            current_time=t_after,
            dispatch_callback=broker.dispatch_outbox_item,
        )

        assert len(dispatched) == 1
        assert dispatched[0].id == item_id
        assert dispatched[0].status == "sent"

        # 4. Confirm message landed in SMTP sink
        assert len(broker.smtp_sink.delivered_messages) == 1
        sink_msg = broker.smtp_sink.delivered_messages[0]
        assert sink_msg["to"] == "client@partner.com"
        assert sink_msg["subject"] == "Invoice 1042"

    def test_tainted_email_rejected_at_broker(self, comms_env):
        broker, _, _ = comms_env
        res = broker.execute("mail.send", {
            "to": "injected@attacker.com",
            "subject": "Exfil",
            "body": "Secret payload",
            "is_tainted": True,
        })
        assert res["status"] == "error"
        assert "tainted" in res["error"].lower()
