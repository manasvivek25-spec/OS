"""Pure Python TF-IDF cosine ranking with online feedback learning and exploration share."""
from __future__ import annotations

from dataclasses import dataclass, field
import math
import random
from typing import Any, Dict, List, Optional, Set

from lazy.niche.fetcher import FeedItem
from lazy.niche.profile import UserProfile, tokenize


@dataclass
class RankedItem:
    """A scored feed item with exploration attribution."""
    item: FeedItem
    score: float
    is_exploration: bool = False
    tokens: List[str] = field(default_factory=list)


class NicheRanker:
    """Ranks feed items using pure Python TF-IDF cosine similarity and exploration share."""

    def __init__(self, exploration_share: float = 0.20, default_seed: Optional[int] = 42):
        self.exploration_share = exploration_share
        self.default_seed = default_seed

    def _extract_item_tokens(self, item: FeedItem) -> List[str]:
        """Combine title, summary, and content into token stream."""
        text = f"{item.title} {item.summary} {item.content}"
        return tokenize(text)

    def compute_tfidf(self, items: List[FeedItem]) -> List[Dict[str, float]]:
        """Compute TF-IDF vectors for a collection of feed items."""
        num_docs = len(items)
        if num_docs == 0:
            return []

        doc_tokens_list = [self._extract_item_tokens(it) for it in items]

        # Calculate document frequency (df) for each term
        df: Dict[str, int] = {}
        for doc_tokens in doc_tokens_list:
            unique_terms = set(doc_tokens)
            for t in unique_terms:
                df[t] = df.get(t, 0) + 1

        # Smooth IDF: ln((1 + N) / (1 + df)) + 1.0
        idf: Dict[str, float] = {}
        for t, freq in df.items():
            idf[t] = math.log((1.0 + num_docs) / (1.0 + freq)) + 1.0

        # Compute TF-IDF vectors
        vectors: List[Dict[str, float]] = []
        for doc_tokens in doc_tokens_list:
            total_terms = len(doc_tokens)
            if total_terms == 0:
                vectors.append({})
                continue

            tf: Dict[str, float] = {}
            for t in doc_tokens:
                tf[t] = tf.get(t, 0.0) + 1.0

            vec: Dict[str, float] = {}
            for t, count in tf.items():
                norm_tf = count / total_terms
                vec[t] = norm_tf * idf.get(t, 1.0)
            vectors.append(vec)

        return vectors

    def cosine_similarity(self, vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
        """Calculate cosine similarity between two sparse weight dictionaries."""
        if not vec_a or not vec_b:
            return 0.0

        dot_product = 0.0
        for k, v in vec_a.items():
            if k in vec_b:
                dot_product += v * vec_b[k]

        norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
        norm_b = math.sqrt(sum(v * v for v in vec_b.values()))

        if norm_a <= 1e-9 or norm_b <= 1e-9:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def rank(
        self,
        items: List[FeedItem],
        profile: UserProfile,
        top_k: int = 5,
        exploration_share: Optional[float] = None,
        seed: Optional[int] = None,
    ) -> List[RankedItem]:
        """Rank feed items against user profile with exploration share (epsilon-greedy)."""
        if not items:
            return []

        eps = exploration_share if exploration_share is not None else self.exploration_share
        rng_seed = seed if seed is not None else self.default_seed
        rng = random.Random(rng_seed)

        vectors = self.compute_tfidf(items)
        profile_vec = dict(profile.terms)

        scored: List[RankedItem] = []
        for idx, item in enumerate(items):
            vec = vectors[idx]
            sim = self.cosine_similarity(profile_vec, vec)

            # Topic matching boost
            topic = item.metadata.get("topic")
            if topic and topic in profile.topics:
                sim += 0.2 * profile.topics[topic]

            sim = min(1.0, max(0.0, sim))
            tokens = self._extract_item_tokens(item)
            scored.append(RankedItem(item=item, score=sim, is_exploration=False, tokens=tokens))

        # Sort descending by similarity score
        scored.sort(key=lambda r: r.score, reverse=True)

        k = min(top_k, len(scored))
        if k <= 1 or eps <= 0.0:
            return scored[:k]

        # Allocate exploit vs explore slots
        num_explore = int(round(k * eps))
        if num_explore == 0 and eps > 0.0:
            num_explore = 1
        num_exploit = k - num_explore

        exploit_items = scored[:num_exploit]
        remaining = scored[num_exploit:]

        if not remaining or num_explore <= 0:
            return scored[:k]

        # Deterministically sample explore items from remaining
        explore_sample_indices = sorted(rng.sample(range(len(remaining)), min(num_explore, len(remaining))))
        explore_items = []
        for i in explore_sample_indices:
            cand = remaining[i]
            cand.is_exploration = True
            explore_items.append(cand)

        result = exploit_items + explore_items
        return result

    def apply_feedback(
        self,
        profile: UserProfile,
        item: FeedItem,
        action: str,
        learning_rate: float = 0.15,
    ) -> None:
        """Apply online learning feedback (accept/dismiss) to update profile term weights."""
        tokens = self._extract_item_tokens(item)
        profile.record_feedback(
            item_id=item.id,
            action=action,
            item_tokens=tokens,
            learning_rate=learning_rate,
        )
