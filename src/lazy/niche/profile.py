"""User interest profile for niche feed personalization and online learning."""
from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("lazy.niche.profile")

STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but",
    "by", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him",
    "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me",
    "more", "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once", "only",
    "or", "other", "our", "ours", "ourselves", "out", "over", "own", "s", "same", "she", "should",
    "so", "some", "such", "t", "than", "that", "the", "their", "theirs", "them", "themselves",
    "then", "there", "these", "they", "this", "those", "through", "to", "too", "under", "until",
    "up", "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom",
    "why", "will", "with", "would", "you", "your", "yours", "yourself", "yourselves",
}


def tokenize(text: str) -> List[str]:
    """Extract lowercased alphanumeric tokens excluding standard stopwords."""
    words = re.findall(r"[a-zA-Z0-9_\-]+", text.lower())
    return [w for w in words if len(w) > 2 and w not in STOPWORDS]


class UserProfile:
    """Maintains user niche interests, online learned weights, and interaction history."""

    def __init__(self, profile_path: Optional[Path | str] = None):
        self.profile_path = Path(profile_path) if profile_path else None
        self.terms: Dict[str, float] = {}
        self.topics: Dict[str, float] = {}
        self.history: List[Dict[str, Any]] = []
        self.accepted_count: int = 0
        self.dismissed_count: int = 0

        if self.profile_path and self.profile_path.is_file():
            self.load(self.profile_path)

    def extract_signals_from_text(self, text: str, boost: float = 0.5) -> None:
        """Derive initial interest weights from local text signals (tasks, notes, code commits)."""
        tokens = tokenize(text)
        for token in tokens:
            self.terms[token] = self.terms.get(token, 0.0) + boost

    def set_term_weight(self, term: str, weight: float) -> None:
        """Explicitly set or edit an interest term weight."""
        term_clean = term.lower().strip()
        if weight <= 0.0:
            self.terms.pop(term_clean, None)
        else:
            self.terms[term_clean] = float(weight)

    def add_topic(self, topic: str, weight: float = 1.0) -> None:
        """Add or update an interest category/topic."""
        self.topics[topic.lower().strip()] = float(weight)

    def remove_topic(self, topic: str) -> None:
        """Remove an interest topic."""
        self.topics.pop(topic.lower().strip(), None)

    def record_feedback(
        self,
        item_id: str,
        action: str,
        item_tokens: Optional[List[str]] = None,
        learning_rate: float = 0.15,
    ) -> None:
        """Record user feedback ('accept' or 'dismiss') and shift term weights."""
        action = action.lower()
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.history.append({
            "item_id": item_id,
            "action": action,
            "timestamp": now,
        })

        if action in ("accept", "click", "like"):
            self.accepted_count += 1
            if item_tokens:
                for token in item_tokens:
                    self.terms[token] = self.terms.get(token, 0.0) + learning_rate
        elif action in ("dismiss", "ignore", "dislike"):
            self.dismissed_count += 1
            if item_tokens:
                penalty = learning_rate * 0.5
                for token in item_tokens:
                    if token in self.terms:
                        self.terms[token] = max(0.0, self.terms[token] - penalty)
                        if self.terms[token] <= 1e-4:
                            del self.terms[token]

        if self.profile_path:
            self.save(self.profile_path)

    def get_profile(self) -> Dict[str, Any]:
        """Viewer API: inspect current interest terms, topics, and metrics."""
        # Top 20 terms sorted by weight
        sorted_terms = sorted(self.terms.items(), key=lambda x: x[1], reverse=True)[:20]
        return {
            "top_terms": dict(sorted_terms),
            "total_terms": len(self.terms),
            "topics": dict(self.topics),
            "accepted_count": self.accepted_count,
            "dismissed_count": self.dismissed_count,
            "history_length": len(self.history),
        }

    def reset(self) -> None:
        """Reset all interest weights and interaction history."""
        self.terms.clear()
        self.topics.clear()
        self.history.clear()
        self.accepted_count = 0
        self.dismissed_count = 0
        if self.profile_path and self.profile_path.exists():
            self.save(self.profile_path)

    def save(self, path: Optional[Path | str] = None) -> None:
        """Persist profile state to JSON."""
        target = Path(path) if path else self.profile_path
        if not target:
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "terms": self.terms,
            "topics": self.topics,
            "accepted_count": self.accepted_count,
            "dismissed_count": self.dismissed_count,
            "history": self.history[-100:],  # keep last 100 entries
        }
        target.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def load(self, path: Path | str) -> None:
        """Load profile state from JSON."""
        target = Path(path)
        if not target.is_file():
            return
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
            self.terms = {str(k): float(v) for k, v in data.get("terms", {}).items()}
            self.topics = {str(k): float(v) for k, v in data.get("topics", {}).items()}
            self.accepted_count = int(data.get("accepted_count", 0))
            self.dismissed_count = int(data.get("dismissed_count", 0))
            self.history = list(data.get("history", []))
        except Exception as e:
            logger.error("Failed to load user profile from %s: %s", target, e)
