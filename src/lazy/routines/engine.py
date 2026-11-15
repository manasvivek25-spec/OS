"""Integrated Routines Engine for Lazy OS (overnight chores, wake-up briefing, and timers)."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from lazy.routines.briefing import BriefingGenerator
from lazy.routines.chores import ChoreManager


class RoutinesEngine:
    """Manages scheduled background chores and the morning wake-up briefing."""

    def __init__(
        self,
        workspace_dir: Path | str,
        snapshots_root: Optional[Path | str] = None,
        tasks_file: Optional[Path | str] = None,
    ):
        self.workspace_dir = Path(workspace_dir)
        self.tasks_file = Path(tasks_file) if tasks_file else self.workspace_dir / "tasks.md"
        self.chores = ChoreManager(workspace_dir=self.workspace_dir, snapshots_root=snapshots_root)
        self.briefing = BriefingGenerator(default_tasks_path=self.tasks_file)

    def run_overnight_chores(self) -> Dict[str, Dict[str, Any]]:
        """Run all designated overnight chores with automatic snapshot isolation."""
        downloads_dir = self.workspace_dir / "Downloads"
        docs_dir = self.workspace_dir / "Documents"
        backups_dir = self.workspace_dir / "Backups"
        log_file = self.workspace_dir / "system.log"
        digest_file = self.workspace_dir / "log_digest.txt"
        manifest_file = self.workspace_dir / "manifest.txt"

        self.chores.run_chore("tidy_downloads", downloads_dir=downloads_dir)
        self.chores.run_chore("backup_documents", source_dir=docs_dir, backup_dir=backups_dir)
        self.chores.run_chore("digest_logs", log_file=log_file, out_file=digest_file)
        self.chores.run_chore("check_updates", manifest_path=manifest_file)

        return self.chores.chore_receipts

    def generate_morning_briefing(self, niche_items: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Generate morning briefing combining telemetry, tasks, chores receipts, and niche news."""
        return self.briefing.generate_briefing(
            tasks_file=self.tasks_file,
            chore_receipts=self.chores.chore_receipts,
            niche_items=niche_items,
        )

    def undo_chore(self, chore_name: str) -> bool:
        """Roll back a specific chore's changes using its pre-chore snapshot."""
        return self.chores.undo_chore(chore_name)

    @staticmethod
    def get_systemd_timer_units() -> Dict[str, str]:
        """Return systemd unit definitions for routine timers."""
        return {
            "lazy-chores.timer": """[Unit]
Description=Lazy OS Overnight Chores Timer
ConditionUser=!root

[Timer]
OnCalendar=*-*-* 03:00:00
Persistent=true

[Install]
WantedBy=timers.target
""",
            "lazy-chores.service": """[Unit]
Description=Lazy OS Overnight Chores Runner
After=local-fs.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 -m lazy.routines --run-chores
StandardOutput=journal
StandardError=journal
""",
            "lazy-briefing.timer": """[Unit]
Description=Lazy OS Morning Briefing Timer
ConditionUser=!root

[Timer]
OnCalendar=*-*-* 07:30:00
Persistent=true

[Install]
WantedBy=timers.target
""",
            "lazy-briefing.service": """[Unit]
Description=Lazy OS Morning Briefing Announcer
After=lazy-gateway.service

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 -m lazy.routines --run-briefing
StandardOutput=journal
StandardError=journal
""",
        }
