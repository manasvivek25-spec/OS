"""JSON-RPC service interface for lazy-outbox."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from lazy.outbox.queue import OutboxQueue

logger = logging.getLogger("lazy.outbox.service")


class OutboxService:
    """Service wrapping OutboxQueue for IPC calls."""

    def __init__(self, queue: Optional[OutboxQueue] = None, storage_dir: Optional[Path | str] = None):
        self.queue = queue if queue else OutboxQueue(storage_dir=storage_dir)

    def handle_enqueue(self, params: Dict[str, Any]) -> Dict[str, Any]:
        item = self.queue.enqueue(
            kind=params["kind"],
            to=params["to"],
            subject=params.get("subject", ""),
            body=params.get("body", ""),
            attachments=params.get("attachments", []),
            delay_seconds=params.get("delay_seconds"),
            is_tainted=params.get("is_tainted", False),
        )
        return {"status": "ok", "item": item.to_dict()}

    def handle_approve(self, params: Dict[str, Any]) -> Dict[str, Any]:
        item = self.queue.approve(
            item_id=params["item_id"],
            approver=params.get("approver", "user"),
            mode=params.get("mode", "user_hud"),
            confirm_new_recipient=params.get("confirm_new_recipient", False),
        )
        return {"status": "ok", "item": item.to_dict()}

    def handle_cancel(self, params: Dict[str, Any]) -> Dict[str, Any]:
        item = self.queue.cancel(
            item_id=params["item_id"],
            reason=params.get("reason", "user_cancelled"),
        )
        return {"status": "ok", "item": item.to_dict()}

    def handle_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        item = self.queue.get_item(params["item_id"])
        if not item:
            return {"status": "error", "error": "Item not found"}
        return {"status": "ok", "item": item.to_dict()}

    def handle_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        status = params.get("status")
        items = self.queue.list_items(status=status)
        return {"status": "ok", "items": [it.to_dict() for it in items]}


def main():
    import os
    from lazy.common.socket_server import UnixSocketServer, parse_socket_arg
    sock = parse_socket_arg("outbox")
    storage = os.environ.get("LAZY_OUTBOX_DIR", "/data/system/lazy/outbox")
    service = OutboxService(storage_dir=storage)
    srv = UnixSocketServer(sock, service_name="lazy-outbox")
    srv.register_simple("outbox.enqueue", service.handle_enqueue)
    srv.register_simple("outbox.approve", service.handle_approve)
    srv.register_simple("outbox.cancel", service.handle_cancel)
    srv.register_simple("outbox.get", service.handle_get)
    srv.register_simple("outbox.list", service.handle_list)
    srv.serve_forever()


if __name__ == "__main__":
    main()
