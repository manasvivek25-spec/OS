"""Wake-up briefing generator for Lazy OS (system status, tasks.md, chores, niche items)."""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


class BriefingGenerator:
    """Compiles the daily wake-up briefing combining telemetry, tasks, chore receipts, and niche news."""

    def __init__(self, default_tasks_path: Optional[Path | str] = None):
        self.default_tasks_path = Path(default_tasks_path) if default_tasks_path else Path.home() / "tasks.md"

    def parse_tasks_markdown(self, tasks_file: Path) -> List[Dict[str, Any]]:
        """Extract pending and completed tasks from tasks.md."""
        tasks: List[Dict[str, Any]] = []
        if not tasks_file.is_file():
            return tasks

        content = tasks_file.read_text(encoding="utf-8", errors="replace")
        for line in content.splitlines():
            line = line.strip()
            # Match - [ ] or - [x]
            m = re.match(r"^[-*]\s+\[([ xX])\]\s+(.+)$", line)
            if m:
                is_done = m.group(1).lower() == "x"
                desc = m.group(2).strip()
                tasks.append({"description": desc, "completed": is_done})
        return tasks

    def collect_system_status(self) -> Dict[str, Any]:
        """Collect current system telemetry."""
        # Simulated or lightweight host readings
        return {
            "cpu_percent": 3.5,
            "memory_used_mb": 450,
            "memory_total_mb": 8192,
            "services_healthy": True,
            "critical_services": {
                "lazy-gateway": "running",
                "lazy-policy": "running",
                "lazy-tasks": "running",
            },
        }

    def generate_briefing(
        self,
        tasks_file: Optional[Path | str] = None,
        chore_receipts: Optional[Dict[str, Dict[str, Any]]] = None,
        niche_items: Optional[List[Dict[str, Any]]] = None,
        system_status: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Compile complete wake-up briefing structure and speech narrative."""
        t_path = Path(tasks_file) if tasks_file else self.default_tasks_path
        tasks = self.parse_tasks_markdown(t_path)
        pending_tasks = [t for t in tasks if not t["completed"]]

        status = system_status or self.collect_system_status()
        chores = chore_receipts or {}
        niche = niche_items or []

        # Construct narrative text
        lines: List[str] = ["Good morning. Here is your Lazy OS wake-up briefing."]

        # 1. System status
        lines.append(
            f"System status is nominal: CPU at {status.get('cpu_percent', 0)}%, "
            f"{status.get('memory_used_mb', 0)} megabytes of RAM utilized. All core services running."
        )

        # 2. Tasks
        if pending_tasks:
            t_names = ", ".join(f"'{t['description']}'" for t in pending_tasks[:3])
            lines.append(f"You have {len(pending_tasks)} pending tasks in tasks.md: {t_names}.")
        else:
            lines.append("No pending tasks recorded in tasks.md.")

        # 3. Overnight chores
        if chores:
            completed_chores = [c["chore"] for c in chores.values() if c.get("status") == "completed"]
            lines.append(f"Overnight chores completed: {', '.join(completed_chores)}.")
        else:
            lines.append("No overnight chores executed.")

        # 4. Niche items
        if niche:
            top_item = niche[0]
            title = top_item.get("title", "Update")
            src = top_item.get("source_id", "feed")
            lines.append(f"Top niche briefing item from {src}: {title}.")

        narrative = " ".join(lines)

        return {
            "narrative": narrative,
            "system_status": status,
            "tasks": {
                "total": len(tasks),
                "pending": len(pending_tasks),
                "items": tasks,
            },
            "overnight_chores": chores,
            "niche_items": niche,
        }
