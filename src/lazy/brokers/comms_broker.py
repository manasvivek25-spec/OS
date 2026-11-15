"""Communications broker for Lazy OS (lazy-broker-comms): maildir, SMTP sink, local chat, and outbox routing."""
from __future__ import annotations

import datetime
import email
from email.message import EmailMessage
import mailbox
import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
import uuid

from lazy.brokers.base import BaseBroker, BrokerExecutionError
from lazy.outbox.models import OutboxItem
from lazy.outbox.queue import OutboxQueue, SecurityViolationError


class DisabledDriverError(BrokerExecutionError):
    """Raised when an external driver is disabled by policy (Rule F4, F8)."""


class MaildirDriver:
    """Handles local maildir email storage (inbox, drafts, sent)."""

    def __init__(self, root_dir: Path | str):
        self.root_dir = Path(root_dir)
        self.inbox_dir = self.root_dir / "inbox"
        self.drafts_dir = self.root_dir / "drafts"
        self.sent_dir = self.root_dir / "sent"

        for d in [self.inbox_dir, self.drafts_dir, self.sent_dir]:
            self._init_maildir(d)

    def _init_maildir(self, d: Path) -> None:
        for sub in ["tmp", "new", "cur"]:
            (d / sub).mkdir(parents=True, exist_ok=True)

    def _get_box(self, folder: str) -> mailbox.Maildir:
        folder_clean = folder.lower().strip()
        if folder_clean in ("inbox", ""):
            self._init_maildir(self.inbox_dir)
            return mailbox.Maildir(str(self.inbox_dir))
        elif folder_clean in ("drafts", "draft"):
            self._init_maildir(self.drafts_dir)
            return mailbox.Maildir(str(self.drafts_dir))
        elif folder_clean in ("sent", "outbox"):
            self._init_maildir(self.sent_dir)
            return mailbox.Maildir(str(self.sent_dir))
        else:
            custom_dir = self.root_dir / folder_clean
            self._init_maildir(custom_dir)
            return mailbox.Maildir(str(custom_dir), create=True)

    def list_messages(self, folder: str = "inbox") -> List[Dict[str, Any]]:
        """List email headers in the specified maildir folder."""
        box = self._get_box(folder)
        messages: List[Dict[str, Any]] = []

        for key, msg in box.items():
            subject = str(msg.get("subject", "(No Subject)"))
            sender = str(msg.get("from", "unknown"))
            recipient = str(msg.get("to", "unknown"))
            date_str = str(msg.get("date", ""))

            messages.append({
                "message_id": key,
                "folder": folder,
                "from": sender,
                "to": recipient,
                "subject": subject,
                "date": date_str,
            })
        return messages

    def read_message(self, message_id: str, folder: str = "inbox") -> Dict[str, Any]:
        """Read a message and extract text body, strictly tagging as untrusted data (Rule F3)."""
        box = self._get_box(folder)
        if message_id not in box:
            raise FileNotFoundError(f"Message ID '{message_id}' not found in folder '{folder}'")

        msg = box.get(message_id)
        subject = str(msg.get("subject", ""))
        sender = str(msg.get("from", ""))
        recipient = str(msg.get("to", ""))
        date_str = str(msg.get("date", ""))

        body = ""
        attachments: List[str] = []

        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                cdisp = str(part.get("Content-Disposition", ""))
                if ctype == "text/plain" and "attachment" not in cdisp:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body += payload.decode("utf-8", errors="replace")
                elif "attachment" in cdisp or part.get_filename():
                    fname = part.get_filename() or "attachment"
                    attachments.append(fname)
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode("utf-8", errors="replace")
            else:
                body = str(msg.get_payload() or "")

        return {
            "message_id": message_id,
            "folder": folder,
            "from": sender,
            "to": recipient,
            "subject": subject,
            "date": date_str,
            "body": body,
            "attachments": attachments,
            "untrusted_data": True,  # Rule F3
            "labelled_text": (
                f"=== BEGIN UNTRUSTED EMAIL [id={message_id}, from={sender}] ===\n"
                f"Subject: {subject}\n"
                f"Date: {date_str}\n\n"
                f"{body}\n"
                f"=== END UNTRUSTED EMAIL ==="
            ),
        }

    def save_draft(self, to: str, subject: str, body: str) -> str:
        """Create and store an email draft in drafts folder."""
        box = self._get_box("drafts")
        msg = EmailMessage()
        msg["To"] = to
        msg["From"] = "user@lazyos.local"
        msg["Subject"] = subject
        msg["Date"] = email.utils.formatdate(localtime=True)
        msg.set_content(body)

        key = box.add(msg)
        box.flush()
        return key

    def deliver_message(self, to: str, subject: str, body: str, folder: str = "inbox", sender: str = "external@domain.com") -> str:
        """Deliver an inbound message into the specified folder (for testing/fixtures)."""
        box = self._get_box(folder)
        msg = EmailMessage()
        msg["To"] = to
        msg["From"] = sender
        msg["Subject"] = subject
        msg["Date"] = email.utils.formatdate(localtime=True)
        msg.set_content(body)

        key = box.add(msg)
        box.flush()
        return key


class SMTPSinkDriver:
    """Local SMTP sink for testing and offline outbox deliveries."""

    def __init__(self):
        self.delivered_messages: List[Dict[str, Any]] = []

    def send(self, to: str, subject: str, body: str, attachments: Optional[List[str]] = None) -> bool:
        """Deliver outgoing email to the sink."""
        self.delivered_messages.append({
            "to": to,
            "subject": subject,
            "body": body,
            "attachments": attachments or [],
            "timestamp": time.time(),
        })
        return True


class LocalChatDriver:
    """Fixture chat service providing channel messaging and Rule F3 safety."""

    def __init__(self):
        self.messages: Dict[str, List[Dict[str, Any]]] = {}

    def post_message(self, channel: str, body: str, author: str = "user") -> Dict[str, Any]:
        """Post a chat message to a channel."""
        ch = channel.strip()
        if ch not in self.messages:
            self.messages[ch] = []

        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        msg = {
            "id": f"chat-{uuid.uuid4().hex[:8]}",
            "channel": ch,
            "author": author,
            "body": body,
            "timestamp": now,
            "untrusted_data": True,  # Rule F3
            "labelled_text": (
                f"=== BEGIN UNTRUSTED CHAT [channel={ch}, author={author}] ===\n"
                f"{body}\n"
                f"=== END UNTRUSTED CHAT ==="
            ),
        }
        self.messages[ch].append(msg)
        return msg

    def read_messages(self, channel: str = "#general", limit: int = 50) -> List[Dict[str, Any]]:
        """Read recent chat messages from a channel."""
        ch = channel.strip()
        channel_msgs = self.messages.get(ch, [])
        return channel_msgs[-limit:]


class IMAPSMTPDriver:
    """Real IMAP/SMTP driver (disabled by default per assignment policy)."""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled

    def check_enabled(self) -> None:
        if not self.enabled:
            raise DisabledDriverError(
                "Real IMAP/SMTP driver is disabled by default. "
                "Real external accounts require explicit human configuration in docs/LICENCES.md."
            )


class TelegramDriver:
    """Telegram Bot API driver (disabled by default per assignment policy)."""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled

    def check_enabled(self) -> None:
        if not self.enabled:
            raise DisabledDriverError(
                "Telegram Bot driver is disabled by default. "
                "Real messaging requires explicit human configuration in docs/LICENCES.md."
            )


class CommsBroker(BaseBroker):
    """Handles communications capabilities: mail.list, mail.read, mail.draft, mail.send, chat.read, chat.send."""

    def __init__(
        self,
        maildir_root: Optional[Path | str] = None,
        outbox: Optional[OutboxQueue] = None,
        enable_real_comms: bool = False,
    ):
        super().__init__("lazy-broker-comms")
        self.maildir_root = Path(maildir_root) if maildir_root else Path("tests/fixtures/maildir")
        self.maildir_driver = MaildirDriver(self.maildir_root)
        self.smtp_sink = SMTPSinkDriver()
        self.chat_driver = LocalChatDriver()

        # Real drivers (disabled by default)
        self.imap_driver = IMAPSMTPDriver(enabled=enable_real_comms)
        self.telegram_driver = TelegramDriver(enabled=enable_real_comms)

        # Outbox queue (Rule F8)
        self.outbox = outbox if outbox else OutboxQueue()

        self._register_handlers()

    def _register_handlers(self) -> None:
        self.register("mail.list", self.handle_mail_list)
        self.register("mail.read", self.handle_mail_read)
        self.register("mail.draft", self.handle_mail_draft)
        self.register("mail.send", self.handle_mail_send)
        self.register("chat.read", self.handle_chat_read)
        self.register("chat.send", self.handle_chat_send)

    def handle_mail_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """L0: List email headers in maildir folder."""
        folder = params.get("folder", "inbox")
        messages = self.maildir_driver.list_messages(folder)
        return {"folder": folder, "count": len(messages), "messages": messages}

    def handle_mail_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """L0: Read specific email by message_id."""
        msg_id = params["message_id"]
        folder = params.get("folder", "inbox")
        msg_data = self.maildir_driver.read_message(msg_id, folder)
        return msg_data

    def handle_mail_draft(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """L1: Create an email draft in drafts folder."""
        to = params["to"]
        subject = params["subject"]
        body = params["body"]
        draft_id = self.maildir_driver.save_draft(to=to, subject=subject, body=body)
        return {"status": "ok", "draft_id": draft_id, "folder": "drafts", "to": to, "subject": subject}

    def handle_mail_send(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """L3: Route outgoing email through outbox queue (Rule F8)."""
        to = params["to"]
        subject = params["subject"]
        body = params["body"]
        attachments = params.get("attachments", [])
        is_tainted = params.get("is_tainted", False)

        item = self.outbox.enqueue(
            kind="mail",
            to=to,
            subject=subject,
            body=body,
            attachments=attachments,
            is_tainted=is_tainted,
        )
        return {
            "status": "queued_in_outbox",
            "outbox_item_id": item.id,
            "send_after": item.send_after,
            "requires_approval": True,
        }

    def handle_chat_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """L0: Read recent chat messages."""
        channel = params.get("channel", "#general")
        limit = params.get("limit", 50)
        msgs = self.chat_driver.read_messages(channel=channel, limit=limit)
        return {"channel": channel, "count": len(msgs), "messages": msgs}

    def handle_chat_send(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """L3: Route outgoing chat message through outbox queue (Rule F8)."""
        to = params["to"]
        body = params["body"]
        is_tainted = params.get("is_tainted", False)

        item = self.outbox.enqueue(
            kind="chat",
            to=to,
            subject="",
            body=body,
            is_tainted=is_tainted,
        )
        return {
            "status": "queued_in_outbox",
            "outbox_item_id": item.id,
            "send_after": item.send_after,
            "requires_approval": True,
        }

    def dispatch_outbox_item(self, item: OutboxItem) -> bool:
        """Callback dispatching approved and matured outbox items to sinks."""
        if item.kind == "mail":
            return self.smtp_sink.send(
                to=item.to,
                subject=item.subject,
                body=item.body,
                attachments=item.attachments,
            )
        elif item.kind == "chat":
            self.chat_driver.post_message(channel=item.to, body=item.body, author="assistant")
            return True
        return False
