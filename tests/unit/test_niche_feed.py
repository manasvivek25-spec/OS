"""Unit tests for Lazy OS M3.4 Niche Feed subsystem.

Covers:
- Sandboxed feed fetcher and Rule F3 data labelling
- Profile initialization from local signals, viewer/editor API, and persistence
- Pure Python TF-IDF cosine ranking and 20% exploration share
- Online learning feedback loop (accept boost vs dismiss penalty)
- Structured reader with item ID citations
- Strict faithfulness checker (grounding and hallucination detection)
- End-to-end briefing integration
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from lazy.niche.faithfulness import FaithfulnessChecker, FaithfulnessReport
from lazy.niche.fetcher import FeedFetcher, FeedItem
from lazy.niche.profile import UserProfile
from lazy.niche.ranker import NicheRanker
from lazy.niche.reader import FeedReader, StructuredSummary
from lazy.niche.service import NicheFeedService
from lazy.routines.briefing import BriefingGenerator


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def sample_items() -> list[FeedItem]:
    return [
        FeedItem(
            id="item-001",
            title="Btrfs snapshot performance and subvolume cloning",
            summary="Optimizations in Btrfs reduce snapshot commit latency by 40 percent.",
            url="https://example.org/btrfs",
            published="2026-11-14T10:00:00Z",
            content="Detailed analysis of Btrfs copy-on-write trees and metadata journal commit times.",
            feed_id="feed-kernel",
            untrusted_data=True,
            metadata={"topic": "kernel"},
        ),
        FeedItem(
            id="item-002",
            title="Formal Grammars for Language Model Sandboxing",
            summary="Using context-free grammars like GBNF eliminates prompt injection vulnerabilities.",
            url="https://example.org/grammar",
            published="2026-11-13T12:00:00Z",
            content="Mathematical proof showing token masking against strict grammar specifications.",
            feed_id="feed-osdev",
            untrusted_data=True,
            metadata={"topic": "security"},
        ),
        FeedItem(
            id="item-003",
            title="Yocto Project 5.0 Scarthgap minimal image recipes",
            summary="Building stripped down Linux distributions using BitBake and WIC partition tools.",
            url="https://example.org/yocto",
            published="2026-11-12T08:00:00Z",
            content="Guide to configuring squashfs read-only root and Btrfs state partition for embedded OS.",
            feed_id="feed-yocto",
            untrusted_data=True,
            metadata={"topic": "embedded_linux"},
        ),
        FeedItem(
            id="item-004",
            title="Cooking recipes for Italian pasta carbonara",
            summary="Authentic Roman pasta recipe using guanciale, pecorino romano, and egg yolks.",
            url="https://example.org/carbonara",
            published="2026-11-11T19:00:00Z",
            content="Step-by-step culinary technique for smooth emulsion without adding heavy cream.",
            feed_id="feed-cooking",
            untrusted_data=True,
            metadata={"topic": "lifestyle"},
        ),
    ]


class TestFeedFetcher:
    def test_fetch_fixture_feeds(self, repo_root: Path):
        config_path = repo_root / "config" / "feeds.yaml"
        fetcher = FeedFetcher(config_path=config_path, base_dir=repo_root)

        items = fetcher.fetch_all_feeds()
        assert len(items) >= 4

        ids = [it.id for it in items]
        assert "kern-001" in ids
        assert "osdev-001" in ids
        assert "yocto-001" in ids

        for it in items:
            assert it.untrusted_data is True
            # Rule F3 check
            labelled = it.to_labelled_data()
            assert "=== BEGIN UNTRUSTED DATA" in labelled
            assert "=== END UNTRUSTED DATA ==="
            assert it.id in labelled

    def test_missing_config_graceful_fallback(self, tmp_path: Path):
        fetcher = FeedFetcher(config_path=tmp_path / "nonexistent.yaml")
        items = fetcher.fetch_all_feeds()
        assert items == []


class TestUserProfile:
    def test_profile_viewer_and_editor_api(self, tmp_path: Path):
        profile_file = tmp_path / "user_profile.json"
        profile = UserProfile(profile_path=profile_file)

        # Editor API
        profile.set_term_weight("btrfs", 2.5)
        profile.set_term_weight("snapshot", 1.8)
        profile.add_topic("kernel", 1.5)

        # Viewer API
        view = profile.get_profile()
        assert view["top_terms"]["btrfs"] == 2.5
        assert view["top_terms"]["snapshot"] == 1.8
        assert view["topics"]["kernel"] == 1.5
        assert view["accepted_count"] == 0

        # Topic removal and term deletion
        profile.remove_topic("kernel")
        profile.set_term_weight("btrfs", 0.0)
        view2 = profile.get_profile()
        assert "kernel" not in view2["topics"]
        assert "btrfs" not in view2["top_terms"]

    def test_signals_extraction_from_local_tasks(self):
        profile = UserProfile()
        tasks_text = """
        - [ ] Optimize Btrfs snapshot performance on Yocto Linux image
        - [ ] Verify GBNF grammar prompt injection defense
        """
        profile.extract_signals_from_text(tasks_text, boost=0.6)
        view = profile.get_profile()

        assert "btrfs" in view["top_terms"]
        assert "snapshot" in view["top_terms"]
        assert "yocto" in view["top_terms"]
        assert view["top_terms"]["btrfs"] >= 0.6

    def test_profile_persistence(self, tmp_path: Path):
        profile_file = tmp_path / "saved_profile.json"
        p1 = UserProfile(profile_path=profile_file)
        p1.set_term_weight("microkernel", 1.4)
        p1.add_topic("osdev", 2.0)
        p1.record_feedback("test-item", "accept", item_tokens=["microkernel", "ipc"])

        # Reload from disk
        p2 = UserProfile(profile_path=profile_file)
        assert p2.terms["microkernel"] >= 1.4
        assert p2.topics["osdev"] == 2.0
        assert p2.accepted_count == 1
        assert len(p2.history) == 1


class TestNicheRanker:
    def test_tfidf_cosine_ranking(self, sample_items: list[FeedItem]):
        ranker = NicheRanker(exploration_share=0.0)
        profile = UserProfile()
        profile.set_term_weight("btrfs", 3.0)
        profile.set_term_weight("snapshot", 2.0)
        profile.set_term_weight("subvolume", 1.5)

        ranked = ranker.rank(sample_items, profile, top_k=3, exploration_share=0.0)
        assert len(ranked) == 3
        # item-001 (Btrfs) must be rank 1
        assert ranked[0].item.id == "item-001"
        assert ranked[0].score > ranked[1].score
        # item-004 (pasta) has zero overlap with btrfs/snapshot
        assert ranked[-1].item.id != "item-001"

    def test_exploration_share_selection(self, sample_items: list[FeedItem]):
        ranker = NicheRanker(exploration_share=0.25, default_seed=123)
        profile = UserProfile()
        profile.set_term_weight("btrfs", 5.0)

        # Top 4 items with 25% exploration means 1 item explored
        ranked = ranker.rank(sample_items, profile, top_k=4, exploration_share=0.25, seed=42)
        assert len(ranked) == 4

        explore_items = [r for r in ranked if r.is_exploration]
        assert len(explore_items) == 1
        exploit_items = [r for r in ranked if not r.is_exploration]
        assert len(exploit_items) == 3
        # Exploit item #1 is btrfs
        assert exploit_items[0].item.id == "item-001"

    def test_online_learning_feedback_loop(self, sample_items: list[FeedItem]):
        ranker = NicheRanker(exploration_share=0.0)
        profile = UserProfile()

        # Initially, neutral profile
        ranked_initial = ranker.rank(sample_items, profile, top_k=4)
        initial_order = [r.item.id for r in ranked_initial]

        # User accepts cooking item (item-004)
        cooking_item = sample_items[3]
        ranker.apply_feedback(profile, cooking_item, action="accept", learning_rate=0.8)

        # After accept, cooking item should rank higher
        ranked_after_accept = ranker.rank(sample_items, profile, top_k=4)
        assert ranked_after_accept[0].item.id == "item-004"
        assert "carbonara" in profile.terms
        assert profile.terms["carbonara"] > 0.5

        # User dismisses cooking item
        ranker.apply_feedback(profile, cooking_item, action="dismiss", learning_rate=1.0)
        assert profile.dismissed_count == 1
        # Weight decreased
        assert profile.terms.get("carbonara", 0.0) < 0.5


class TestFeedReader:
    def test_deterministic_summary_with_citations(self, sample_items: list[FeedItem]):
        reader = FeedReader(mode="mock")
        items = sample_items[:2]

        summary = reader.summarize(items, max_items=2)
        assert summary.items_read == 2
        assert len(summary.citations) == 2
        assert "item-001" in summary.citations
        assert "item-002" in summary.citations

        # Check inline citation formatting [item-001]
        assert "[item-001]" in summary.summary_text
        assert "[item-002]" in summary.summary_text

        # Claims structure check
        assert len(summary.claims) == 2
        assert summary.claims[0]["source_id"] == "item-001"
        assert summary.claims[1]["source_id"] == "item-002"


class TestFaithfulnessChecker:
    def test_faithful_summary_passes(self, sample_items: list[FeedItem]):
        checker = FaithfulnessChecker()
        reader = FeedReader(mode="mock")
        items = sample_items[:3]

        summary = reader.summarize(items, max_items=3)
        report = checker.verify(summary, items)

        assert report.is_faithful is True
        assert len(report.hallucinated_citations) == 0
        assert len(report.unsupported_claims) == 0
        assert set(report.valid_citations) == {"item-001", "item-002", "item-003"}

    def test_hallucinated_citation_detected(self, sample_items: list[FeedItem]):
        checker = FaithfulnessChecker()
        fake_summary = StructuredSummary(
            summary_text="Quantum computer chips were manufactured with silicon photonics [quantum-999].",
            citations=["quantum-999"],
            claims=[{
                "claim": "Quantum computer chips manufactured with photonics",
                "source_id": "quantum-999",
            }],
            items_read=1,
        )

        report = checker.verify(fake_summary, sample_items)
        assert report.is_faithful is False
        assert "quantum-999" in report.hallucinated_citations

    def test_unsupported_claim_detected(self, sample_items: list[FeedItem]):
        checker = FaithfulnessChecker()
        # Uses real source ID (item-001: Btrfs) but claim is about chocolate baking (0 overlap)
        fake_summary = StructuredSummary(
            summary_text="Bake rich dark chocolate brownies at 350 degrees [item-001].",
            citations=["item-001"],
            claims=[{
                "claim": "Bake rich dark chocolate brownies at 350 degrees",
                "source_id": "item-001",
            }],
            items_read=1,
        )

        report = checker.verify(fake_summary, sample_items)
        assert report.is_faithful is False
        assert len(report.unsupported_claims) == 1
        assert report.unsupported_claims[0]["source_id"] == "item-001"


class TestNicheFeedServiceIntegration:
    def test_end_to_end_service_and_briefing(self, repo_root: Path, tmp_path: Path):
        config_path = repo_root / "config" / "feeds.yaml"
        profile_path = tmp_path / "niche_profile.json"

        service = NicheFeedService(
            config_path=config_path,
            profile_path=profile_path,
            base_dir=repo_root,
            exploration_share=0.20,
            reader_mode="mock",
        )

        # 1. Seed interest in kernel and btrfs
        service.edit_term_weight("btrfs", 2.0)
        service.edit_term_weight("kernel", 1.5)
        service.add_interest_topic("kernel", 1.0)

        # 2. Generate briefing section
        section = service.generate_briefing_section(limit=3)
        assert "summary" in section
        assert "faithfulness" in section
        assert "items" in section

        # Faithfulness check: every claim maps to a source item!
        assert section["faithfulness"]["is_faithful"] is True
        assert len(section["faithfulness"]["hallucinated_citations"]) == 0
        assert len(section["faithfulness"]["unsupported_claims"]) == 0

        # Top item should be kernel-related
        top_item = section["items"][0]
        assert "kern-" in top_item["id"] or top_item["source_id"] == "feed-kernel"

        # 3. Test feedback learning
        ok = service.record_feedback(top_item["id"], "accept")
        assert ok is True
        view = service.get_profile_view()
        assert view["accepted_count"] == 1

        # 4. Integrate with BriefingGenerator
        gen = BriefingGenerator()
        briefing = gen.generate_briefing(
            niche_items=section["items"],
            chore_receipts={},
            system_status={"cpu_percent": 2.1, "memory_used_mb": 420},
        )
        assert "narrative" in briefing
        assert "Top niche briefing item from feed-kernel" in briefing["narrative"]
        assert len(briefing["niche_items"]) == 3
