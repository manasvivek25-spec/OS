"""Niche feed service runner for lazy-fetcher."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict
from lazy.common.socket_server import UnixSocketServer, parse_socket_arg
from lazy.niche.service import NicheFeedService


def main():
    sock = parse_socket_arg("fetcher")
    base_dir = os.environ.get("LAZY_NICHE_DIR", "/data/niche")
    service = NicheFeedService(base_dir=base_dir)

    srv = UnixSocketServer(sock, service_name="lazy-fetcher")

    def handle_feed(params: Dict[str, Any]) -> Dict[str, Any]:
        top_k = params.get("top_k", 5)
        ranked = service.get_ranked_feed(top_k=top_k)
        return {
            "status": "ok",
            "items": [
                {
                    "id": r.item.id,
                    "title": r.item.title,
                    "summary": r.item.summary,
                    "source_id": r.item.feed_id,
                    "score": r.score,
                    "is_exploration": r.is_exploration,
                }
                for r in ranked
            ],
        }

    def handle_feedback(params: Dict[str, Any]) -> Dict[str, Any]:
        ok = service.record_feedback(params["item_id"], params["action"])
        return {"status": "ok" if ok else "error"}

    def handle_briefing(params: Dict[str, Any]) -> Dict[str, Any]:
        limit = params.get("limit", 3)
        return {"status": "ok", "section": service.generate_briefing_section(limit=limit)}

    srv.register_simple("niche.feed", handle_feed)
    srv.register_simple("niche.feedback", handle_feedback)
    srv.register_simple("niche.briefing", handle_briefing)
    srv.register_simple("fetch.feed", handle_feed)
    srv.serve_forever()


if __name__ == "__main__":
    main()
