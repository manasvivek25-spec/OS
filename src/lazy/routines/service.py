"""Routines and chores automation service for lazy-routines."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict
from lazy.common.socket_server import UnixSocketServer, parse_socket_arg
from lazy.routines.engine import RoutinesEngine


def main():
    sock = parse_socket_arg("routines")
    workspace = os.environ.get("LAZY_WORKSPACE_DIR", "/data/home/lazy")
    snapshots = os.environ.get("LAZY_SNAPSHOTS_DIR", "/data/snapshots")
    engine = RoutinesEngine(workspace_dir=workspace, snapshots_root=snapshots)

    srv = UnixSocketServer(sock, service_name="lazy-routines")

    def handle_chores(params: Dict[str, Any]) -> Dict[str, Any]:
        results = engine.run_overnight_chores()
        return {"status": "ok", "results": results}

    def handle_briefing(params: Dict[str, Any]) -> Dict[str, Any]:
        niche_items = params.get("niche_items")
        briefing = engine.generate_morning_briefing(niche_items=niche_items)
        return {"status": "ok", "briefing": briefing}

    def handle_undo(params: Dict[str, Any]) -> Dict[str, Any]:
        chore_name = params["chore_name"]
        ok = engine.undo_chore(chore_name)
        return {"status": "ok" if ok else "error"}

    srv.register_simple("routines.chores", handle_chores)
    srv.register_simple("routines.briefing", handle_briefing)
    srv.register_simple("routines.undo", handle_undo)
    srv.serve_forever()


if __name__ == "__main__":
    main()
