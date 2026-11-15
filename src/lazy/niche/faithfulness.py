"""Faithfulness checker for Lazy OS niche summaries (validating every claim maps to source items)."""
from __future__ import annotations

from dataclasses import dataclass, field
import logging
import re
from typing import Any, Dict, List, Set

from lazy.niche.fetcher import FeedItem
from lazy.niche.profile import tokenize
from lazy.niche.reader import StructuredSummary

logger = logging.getLogger("lazy.niche.faithfulness")


@dataclass
class FaithfulnessReport:
    """Report detailing faithfulness verification results."""
    is_faithful: bool
    total_claims: int
    valid_citations: List[str] = field(default_factory=list)
    hallucinated_citations: List[str] = field(default_factory=list)
    unsupported_claims: List[Dict[str, Any]] = field(default_factory=list)
    inline_citations: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_faithful": self.is_faithful,
            "total_claims": self.total_claims,
            "valid_citations": self.valid_citations,
            "hallucinated_citations": self.hallucinated_citations,
            "unsupported_claims": self.unsupported_claims,
            "inline_citations": self.inline_citations,
            "details": self.details,
        }


class FaithfulnessChecker:
    """Validates that structured summaries are strictly grounded in source items without hallucination."""

    def __init__(self, min_token_overlap: int = 1):
        self.min_token_overlap = min_token_overlap

    def verify(
        self,
        summary: StructuredSummary,
        source_items: List[FeedItem],
    ) -> FaithfulnessReport:
        """Verify that every citation and claim strictly maps to a valid source item."""
        source_map: Dict[str, FeedItem] = {it.id: it for it in source_items}
        source_tokens_map: Dict[str, Set[str]] = {}
        for it in source_items:
            full_text = f"{it.title} {it.summary} {it.content}"
            source_tokens_map[it.id] = set(tokenize(full_text))

        # 1. Check inline citations in text
        inline_matches = re.findall(r"\[([a-zA-Z0-9_\-]+)\]", summary.summary_text)
        hallucinated: List[str] = []
        valid: List[str] = []

        all_citations = set(summary.citations) | set(inline_matches)
        for cite in all_citations:
            if cite in source_map:
                if cite not in valid:
                    valid.append(cite)
            else:
                if cite not in hallucinated:
                    hallucinated.append(cite)

        # 2. Check each claim
        unsupported: List[Dict[str, Any]] = []
        for claim_entry in summary.claims:
            claim_text = claim_entry.get("claim", "")
            source_id = claim_entry.get("source_id", "")

            # Check if source_id exists
            if source_id not in source_map:
                unsupported.append({
                    "claim": claim_text,
                    "source_id": source_id,
                    "reason": f"Source ID '{source_id}' does not exist in input feeds",
                })
                continue

            # Check grounding overlap
            claim_tokens = set(tokenize(claim_text))
            source_tokens = source_tokens_map[source_id]
            overlap = claim_tokens & source_tokens

            if len(overlap) < self.min_token_overlap and len(claim_tokens) > 0:
                unsupported.append({
                    "claim": claim_text,
                    "source_id": source_id,
                    "reason": f"Claim has insufficient token overlap with source item (overlap: {list(overlap)})",
                })

        is_faithful = (len(hallucinated) == 0) and (len(unsupported) == 0) and (len(summary.claims) > 0 or len(source_items) == 0)

        return FaithfulnessReport(
            is_faithful=is_faithful,
            total_claims=len(summary.claims),
            valid_citations=valid,
            hallucinated_citations=hallucinated,
            unsupported_claims=unsupported,
            inline_citations=inline_matches,
            details={
                "source_items_count": len(source_items),
                "summary_length_chars": len(summary.summary_text),
            },
        )
