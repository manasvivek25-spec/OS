"""Audit microservice for Lazy OS (lazy-audit)."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

from lazy.audit.ledger import AuditLedger
from lazy.audit.verifier import verify_audit_log
from lazy.common.socket_server import UnixSocketServer, parse_socket_arg


def create_audit_server(socket_path: Path | str, ledger_path: Path | str | None = None) -> UnixSocketServer:
    if ledger_path is None:
        ledger_path = Path(os.environ.get("LAZY_AUDIT_PATH", "/data/.audit/lazy-audit.log"))
    ledger_path = Path(ledger_path)
    try:
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        os.chmod(str(ledger_path.parent), 0o777)
    except Exception:
        pass
    ledger = AuditLedger(ledger_path)

    server = UnixSocketServer(socket_path, service_name="lazy-audit")

    def handle_log(params: Dict[str, Any]) -> Dict[str, Any]:
        event_type = params.get("event_type", "generic")
        actor = params.get("actor", "unknown")
        payload = params.get("payload", {})
        record = ledger.append(event_type=event_type, actor=actor, payload=payload)
        return {"status": "ok", "record": record.to_dict()}

    def handle_verify(params: Dict[str, Any]) -> Dict[str, Any]:
        expected = params.get("expected_count")
        res = verify_audit_log(ledger_path, expected_count=expected)
        return {
            "status": "ok" if res.is_valid else "error",
            "is_valid": res.is_valid,
            "total_records": res.total_records,
            "reason": res.reason,
            "failed_index": res.failed_index,
        }

    def handle_read(params: Dict[str, Any]) -> Dict[str, Any]:
        records = ledger.read_all()
        limit = params.get("limit")
        if limit and isinstance(limit, int):
            records = records[-limit:]
        return {"status": "ok", "records": [r.to_dict() for r in records]}

    server.register_simple("audit.log", handle_log)
    server.register_simple("audit.append", handle_log)
    server.register_simple("audit.verify", handle_verify)
    server.register_simple("audit.read", handle_read)
    server.register_simple("audit.get_all", handle_read)
    return server


def main():
    sock = parse_socket_arg("audit")
    srv = create_audit_server(sock)
    srv.serve_forever()


if __name__ == "__main__":
    main()
