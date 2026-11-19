"""Planner microservice for lazy-planner."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict
from lazy.common.socket_server import UnixSocketServer, parse_socket_arg
from lazy.planner.llm_planner import LLMPlanner
from lazy.planner.mock import MockPlanner


def main():
    sock = parse_socket_arg("planner")
    try:
        planner = LLMPlanner()
    except Exception:
        planner = MockPlanner()

    srv = UnixSocketServer(sock, service_name="lazy-planner")

    def handle_plan(params: Dict[str, Any]) -> Dict[str, Any]:
        query = params.get("query", "")
        context = params.get("context")
        res = planner.plan(query, context=context)
        return {"status": "ok", "plan": res}

    def handle_propose(params: Dict[str, Any]) -> Dict[str, Any]:
        query = params.get("query", "")
        context = params.get("context")
        res = planner.propose_intent(query, context=context)
        return {"status": "ok", "intent": res}

    srv.register_simple("planner.plan", handle_plan)
    srv.register_simple("planner.propose", handle_propose)
    srv.register_simple("planner.propose_intent", handle_propose)
    srv.serve_forever()


if __name__ == "__main__":
    main()
