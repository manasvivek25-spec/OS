"""Lazy OS Niche Feed Subsystem (fetching, TF-IDF ranking, online learning, structured reader, faithfulness)."""

from lazy.niche.fetcher import FeedFetcher, FeedItem
from lazy.niche.profile import UserProfile
from lazy.niche.ranker import NicheRanker, RankedItem
from lazy.niche.reader import FeedReader, StructuredSummary
from lazy.niche.faithfulness import FaithfulnessChecker, FaithfulnessReport
from lazy.niche.service import NicheFeedService

__all__ = [
    "FeedFetcher",
    "FeedItem",
    "UserProfile",
    "NicheRanker",
    "RankedItem",
    "FeedReader",
    "StructuredSummary",
    "FaithfulnessChecker",
    "FaithfulnessReport",
    "NicheFeedService",
]
