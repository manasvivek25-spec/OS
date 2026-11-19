"""Policy engine service for lazy-policy."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict
from lazy.common.socket_server import UnixSocketServer, parse_socket_arg
from lazy.policy.engine import PolicyEngine


def main():
    sock = parse_socket_arg("policy")
    cap_dir = os.environ.get("LAZY_CAPABILITIES_DIR", "/etc/lazy/capabilities")
    engine = PolicyEngine(capabilities_dir=cap_dir)

    srv = UnixSocketServer(sock, service_name="lazy-policy")

    def handle_evaluate(params: Dict[str, Any]) -> Dict[str, Any]:
        intent = params.get("intent", params)
        res = engine.evaluate_intent(intent)
        return {"status": "ok", "evaluation": res}

    def handle_approve(params: Dict[str, Any]) -> Dict[str, Any]:
        req_id = params["request_id"]
        approver = params.get("approver", "user")
        mode = params.get("mode", "hud")
        ok, reason = engine.approve_request(req_id, approver, mode)
        return {"status": "ok" if ok else "error", "reason": reason}

    def handle_deny(params: Dict[str, Any]) -> Dict[str, Any]:
        req_id = params["request_id"]
        denier = params.get("denier", "user")
        reason = params.get("reason", "denied")
        ok, err = engine.deny_request(req_id, denier, reason)
        return {"status": "ok" if ok else "error", "reason": err}

    srv.register_simple("policy.evaluate", handle_evaluate)
    srv.register_simple("policy.check", handle_evaluate)
    srv.register_simple("policy.approve", handle_approve)
    srv.register_simple("policy.deny", handle_deny)
    srv.serve_forever()


if __name__ == "__main__":
    main()
