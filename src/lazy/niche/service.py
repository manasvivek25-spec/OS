"""Niche feed coordination service for Lazy OS (fetching, ranking, structured reading, and briefing integration)."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from lazy.niche.faithfulness import FaithfulnessChecker, FaithfulnessReport
from lazy.niche.fetcher import FeedFetcher, FeedItem
from lazy.niche.profile import UserProfile
from lazy.niche.ranker import NicheRanker, RankedItem
from lazy.niche.reader import FeedReader, StructuredSummary

logger = logging.getLogger("lazy.niche.service")


class NicheFeedService:
    """High-level service coordinating niche feed aggregation, personalization, and briefing integration."""

    def __init__(
        self,
        config_path: Optional[Path | str] = None,
        profile_path: Optional[Path | str] = None,
        base_dir: Optional[Path | str] = None,
        exploration_share: float = 0.20,
        reader_mode: str = "mock",
        llm_client: Optional[Any] = None,
    ):
        self.fetcher = FeedFetcher(config_path=config_path, base_dir=base_dir)
        self.profile = UserProfile(profile_path=profile_path)
        self.ranker = NicheRanker(exploration_share=exploration_share)
        self.reader = FeedReader(mode=reader_mode, llm_client=llm_client)
        self.verifier = FaithfulnessChecker()
        self._cached_items: Dict[str, FeedItem] = {}

    def refresh_feeds(self) -> List[FeedItem]:
        """Fetch all items from feeds and update cache."""
        items = self.fetcher.fetch_all_feeds()
        for it in items:
            self._cached_items[it.id] = it
        return items

    def get_ranked_feed(
        self,
        top_k: int = 5,
        exploration_share: Optional[float] = None,
        seed: Optional[int] = 42,
    ) -> List[RankedItem]:
        """Fetch and rank feed items according to user profile interests."""
        items = self.refresh_feeds()
        return self.ranker.rank(
            items=items,
            profile=self.profile,
            top_k=top_k,
            exploration_share=exploration_share,
            seed=seed,
        )

    def record_feedback(self, item_id: str, action: str) -> bool:
        """Record user feedback ('accept' or 'dismiss') on a specific item."""
        item = self._cached_items.get(item_id)
        if not item:
            # Try fetching if cache empty
            self.refresh_feeds()
            item = self._cached_items.get(item_id)

        if not item:
            logger.warning("Feedback for unknown item_id: %s", item_id)
            return False

        self.ranker.apply_feedback(self.profile, item, action)
        return True

    def generate_briefing_section(self, limit: int = 3) -> Dict[str, Any]:
        """Compile structured niche updates with citations and faithfulness verification."""
        ranked = self.get_ranked_feed(top_k=limit)
        items = [r.item for r in ranked]
        summary = self.reader.summarize(items, max_items=limit)
        faithfulness = self.verifier.verify(summary, items)

        # Build items list compatible with BriefingGenerator
        formatted_items: List[Dict[str, Any]] = []
        for r in ranked:
            formatted_items.append({
                "id": r.item.id,
                "title": r.item.title,
                "summary": r.item.summary,
                "source_id": r.item.feed_id,
                "score": r.score,
                "is_exploration": r.is_exploration,
            })

        return {
            "summary": summary.to_dict(),
            "faithfulness": faithfulness.to_dict(),
            "items": formatted_items,
        }

    # Profile Viewer & Editor API
    def get_profile_view(self) -> Dict[str, Any]:
        """Return user profile metrics and current interest weights."""
        return self.profile.get_profile()

    def edit_term_weight(self, term: str, weight: float) -> None:
        """Manually tune an interest term weight."""
        self.profile.set_term_weight(term, weight)

    def add_interest_topic(self, topic: str, weight: float = 1.0) -> None:
        """Add an explicit interest topic."""
        self.profile.add_topic(topic, weight)

    def remove_interest_topic(self, topic: str) -> None:
        """Remove an explicit interest topic."""
        self.profile.remove_topic(topic)

    def reset_profile(self) -> None:
        """Reset profile to clean state."""
        self.profile.reset()
