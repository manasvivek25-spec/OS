"""Feed fetcher for Lazy OS niche news feeds (sandboxed fetch, Rule F3 labelled data)."""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.parse
import urllib.request
import yaml

logger = logging.getLogger("lazy.niche.fetcher")


@dataclass
class FeedItem:
    """Individual news or announcement feed item."""
    id: str
    title: str
    summary: str
    url: str
    published: str
    content: str
    feed_id: str
    untrusted_data: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_labelled_data(self) -> str:
        """Format item as explicitly labelled quoted data per Rule F3."""
        return (
            f"=== BEGIN UNTRUSTED DATA [feed_id={self.feed_id}, item_id={self.id}] ===\n"
            f"Title: {self.title}\n"
            f"Published: {self.published}\n"
            f"URL: {self.url}\n"
            f"Summary: {self.summary}\n"
            f"Content: {self.content}\n"
            f"=== END UNTRUSTED DATA ==="
        )


class FeedFetcher:
    """Fetches and parses configured niche feeds (local fixtures and remote endpoints)."""

    def __init__(self, config_path: Optional[Path | str] = None, base_dir: Optional[Path | str] = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.config_path = Path(config_path) if config_path else self.base_dir / "config" / "feeds.yaml"
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load feeds configuration from YAML."""
        if not self.config_path.is_file():
            logger.warning("Feeds config not found at %s, using empty config", self.config_path)
            return {"feeds": [], "settings": {}}

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data if isinstance(data, dict) else {"feeds": [], "settings": {}}
        except Exception as e:
            logger.error("Failed to parse feeds config: %s", e)
            return {"feeds": [], "settings": {}}

    def fetch_feed(self, feed_cfg: Dict[str, Any]) -> List[FeedItem]:
        """Fetch and parse a single feed definition."""
        feed_id = feed_cfg.get("id", "unknown-feed")
        url = feed_cfg.get("url", "")
        if not feed_cfg.get("enabled", True):
            return []

        try:
            raw_text = self._read_source(url)
            data = json.loads(raw_text)
            items_data = data.get("items", [])
            items: List[FeedItem] = []
            for raw in items_data:
                item = FeedItem(
                    id=str(raw.get("id", f"{feed_id}-{len(items)+1}")),
                    title=str(raw.get("title", "")),
                    summary=str(raw.get("summary", "")),
                    url=str(raw.get("url", "")),
                    published=str(raw.get("published", "")),
                    content=str(raw.get("content", "")),
                    feed_id=feed_id,
                    untrusted_data=True,
                    metadata={"topic": feed_cfg.get("topic", "general")},
                )
                items.append(item)
            return items
        except Exception as e:
            logger.error("Error fetching feed %s from %s: %s", feed_id, url, e)
            return []

    def _read_source(self, url: str) -> str:
        """Read data from file:// URL or local path, or HTTP URL."""
        if url.startswith("file://"):
            raw_path = url[len("file://"):]
            # Check for Windows file:///C:/path or Unix file:///path
            if raw_path.startswith("/"):
                # Check for Windows drive letter like /C:/
                if os.name == "nt" and len(raw_path) > 3 and raw_path[2] == ":":
                    target = Path(raw_path[1:])
                else:
                    target = Path(raw_path)
            else:
                # Relative path like file://tests/fixtures/...
                target = self.base_dir / raw_path

            if not target.is_absolute():
                target = self.base_dir / target
            return target.read_text(encoding="utf-8", errors="replace")
        elif url.startswith("http://") or url.startswith("https://"):
            # Sandboxed fetch: in offline/test environments, restrict or mock
            req = urllib.request.Request(url, headers={"User-Agent": "LazyOS-Fetcher/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.read().decode("utf-8", errors="replace")
        else:
            # Treat as local relative path
            target = Path(url)
            if not target.is_absolute():
                target = self.base_dir / target
            return target.read_text(encoding="utf-8", errors="replace")

    def fetch_all_feeds(self) -> List[FeedItem]:
        """Fetch items from all configured feeds."""
        all_items: List[FeedItem] = []
        for feed_cfg in self.config.get("feeds", []):
            items = self.fetch_feed(feed_cfg)
            all_items.extend(items)
        return all_items
