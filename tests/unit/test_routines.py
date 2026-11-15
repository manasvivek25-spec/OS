"""Unit tests for Lazy OS Routines: overnight chores, wake-up briefing, snapshot undo, and timers."""
from __future__ import annotations

from pathlib import Path
import pytest

from lazy.routines.briefing import BriefingGenerator
from lazy.routines.chores import ChoreManager
from lazy.routines.engine import RoutinesEngine


@pytest.fixture
def test_workspace(tmp_path: Path):
    ws = tmp_path / "workspace"
    ws.mkdir()
    snaps = tmp_path / "snapshots"
    snaps.mkdir()
    return ws, snaps


class TestChoreManager:
    def test_tidy_downloads_with_undo(self, test_workspace):
        ws, snaps = test_workspace
        downloads = ws / "Downloads"
        downloads.mkdir()

        # Seed files
        f1 = downloads / "file1.txt"
        f2 = downloads / "file2.pdf"
        f1.write_text("file 1 content", encoding="utf-8")
        f2.write_text("file 2 content", encoding="utf-8")

        mgr = ChoreManager(workspace_dir=ws, snapshots_root=snaps)
        receipt = mgr.run_chore("tidy_downloads", downloads_dir=downloads)

        assert receipt["status"] == "completed"
        assert receipt["changes"]["count"] == 2
        assert not f1.exists()
        assert not f2.exists()
        assert (downloads / "Archive" / "file1.txt").exists()
        assert (downloads / "Archive" / "file2.pdf").exists()

        # Test Undo chore (Rule F7)
        undo_ok = mgr.undo_chore("tidy_downloads")
        assert undo_ok is True
        assert f1.exists()
        assert f2.exists()
        assert f1.read_text(encoding="utf-8") == "file 1 content"

    def test_backup_documents(self, test_workspace):
        ws, snaps = test_workspace
        docs = ws / "Documents"
        docs.mkdir()
        backups = ws / "Backups"

        (docs / "doc1.txt").write_text("important document", encoding="utf-8")
        mgr = ChoreManager(workspace_dir=ws, snapshots_root=snaps)
        receipt = mgr.run_chore("backup_documents", source_dir=docs, backup_dir=backups)

        assert receipt["status"] == "completed"
        tar_path = Path(receipt["changes"]["backup_archive"])
        assert tar_path.is_file()
        assert tar_path.stat().st_size > 0

    def test_digest_logs(self, test_workspace):
        ws, snaps = test_workspace
        log_file = ws / "system.log"
        out_file = ws / "log_digest.txt"

        log_content = (
            "INFO Starting daemon\n"
            "WARN High latency detected\n"
            "ERROR Failed to bind socket\n"
            "INFO Retrying connection\n"
        )
        log_file.write_text(log_content, encoding="utf-8")

        mgr = ChoreManager(workspace_dir=ws, snapshots_root=snaps)
        receipt = mgr.run_chore("digest_logs", log_file=log_file, out_file=out_file)

        assert receipt["status"] == "completed"
        assert receipt["changes"]["total_lines"] == 4
        assert receipt["changes"]["errors"] == 1
        assert receipt["changes"]["warnings"] == 1
        assert out_file.is_file()

    def test_check_updates(self, test_workspace):
        ws, snaps = test_workspace
        manifest = ws / "manifest.txt"
        manifest.write_text("version=1.0.0\n", encoding="utf-8")

        mgr = ChoreManager(workspace_dir=ws, snapshots_root=snaps)
        receipt = mgr.run_chore("check_updates", manifest_path=manifest)

        assert receipt["status"] == "completed"
        assert receipt["changes"]["status"] == "up_to_date"


class TestBriefingGenerator:
    def test_tasks_markdown_parser(self, tmp_path: Path):
        tasks_file = tmp_path / "tasks.md"
        tasks_content = """# My Tasks
- [ ] Review operating systems rubric
- [x] Set up Yocto environment
- [ ] Complete Phase 3 interface and routines
* [x] Run M2.4 evaluation benchmark
"""
        tasks_file.write_text(tasks_content, encoding="utf-8")

        gen = BriefingGenerator(default_tasks_path=tasks_file)
        tasks = gen.parse_tasks_markdown(tasks_file)

        assert len(tasks) == 4
        pending = [t for t in tasks if not t["completed"]]
        assert len(pending) == 2
        assert pending[0]["description"] == "Review operating systems rubric"
        assert pending[1]["description"] == "Complete Phase 3 interface and routines"

    def test_briefing_narrative_generation(self, tmp_path: Path):
        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text("- [ ] Submit assignment\n", encoding="utf-8")

        gen = BriefingGenerator(default_tasks_path=tasks_file)
        chores_data = {
            "tidy_downloads": {"chore": "tidy_downloads", "status": "completed"},
            "backup_documents": {"chore": "backup_documents", "status": "completed"},
        }
        niche_items = [
            {"source_id": "kernel_feed", "title": "Linux 6.6 LTS release announcement"}
        ]

        briefing = gen.generate_briefing(
            tasks_file=tasks_file,
            chore_receipts=chores_data,
            niche_items=niche_items,
        )

        assert "narrative" in briefing
        narr = briefing["narrative"]
        assert "Good morning" in narr
        assert "System status is nominal" in narr
        assert "pending tasks in tasks.md: 'Submit assignment'" in narr
        assert "tidy_downloads, backup_documents" in narr
        assert "Linux 6.6 LTS release announcement" in narr


class TestRoutinesEngineIntegration:
    def test_overnight_sequence_and_morning_briefing(self, test_workspace):
        ws, snaps = test_workspace
        tasks_file = ws / "tasks.md"
        tasks_file.write_text("- [ ] Deploy Lazy OS full image\n", encoding="utf-8")

        engine = RoutinesEngine(workspace_dir=ws, snapshots_root=snaps, tasks_file=tasks_file)

        # 1. Run overnight chores
        receipts = engine.run_overnight_chores()
        assert len(receipts) == 4
        for chore_name, rec in receipts.items():
            assert rec["status"] == "completed"

        # 2. Generate morning briefing
        niche_data = [{"source_id": "osdev_news", "title": "Btrfs snapshotting latency improvements"}]
        briefing = engine.generate_morning_briefing(niche_items=niche_data)

        assert briefing["tasks"]["pending"] == 1
        assert len(briefing["overnight_chores"]) == 4
        assert len(briefing["niche_items"]) == 1

        # 3. Systemd timers syntax check
        units = engine.get_systemd_timer_units()
        assert "lazy-chores.timer" in units
        assert "lazy-briefing.timer" in units
        assert "OnCalendar=*-*-* 03:00:00" in units["lazy-chores.timer"]
        assert "OnCalendar=*-*-* 07:30:00" in units["lazy-briefing.timer"]
