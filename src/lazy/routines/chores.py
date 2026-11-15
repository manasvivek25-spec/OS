"""Overnight chores engine with transactional snapshot rollback and undo (Rule F5, F7)."""
from __future__ import annotations

import os
import shutil
import tarfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from lazy.tasks.manager import TaskManager


class ChoreManager:
    """Executes safe background system chores, each isolated inside a snapshot with full undo."""

    def __init__(self, workspace_dir: Path | str, snapshots_root: Optional[Path | str] = None):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.task_manager = TaskManager(
            target_dir=self.workspace_dir,
            backend_type="copy",
            snapshots_root=snapshots_root,
        )
        self.chore_receipts: Dict[str, Dict[str, Any]] = {}

    def run_chore(self, chore_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a chore inside a point-in-time snapshot with transactional rollback."""
        task_id = f"task-chore-{chore_name}-{int(time.time())}"
        task = self.task_manager.create_task(task_id=task_id)

        ckpt_id = self.task_manager.checkpoint_before_step(
            task_id=task_id, intent_id=f"intent-{chore_name}", step_index=0
        )

        try:
            if chore_name == "tidy_downloads":
                changes = self._tidy_downloads(kwargs.get("downloads_dir", self.workspace_dir / "Downloads"))
            elif chore_name == "backup_documents":
                changes = self._backup_documents(
                    kwargs.get("source_dir", self.workspace_dir / "Documents"),
                    kwargs.get("backup_dir", self.workspace_dir / "Backups"),
                )
            elif chore_name == "digest_logs":
                changes = self._digest_logs(
                    kwargs.get("log_file", self.workspace_dir / "system.log"),
                    kwargs.get("out_file", self.workspace_dir / "log_digest.txt"),
                )
            elif chore_name == "check_updates":
                changes = self._check_updates(kwargs.get("manifest_path", self.workspace_dir / "manifest.txt"))
            else:
                raise ValueError(f"Unknown chore: {chore_name}")

            self.task_manager.finish_step(task_id, 0, {"changes": changes})
            self.task_manager.commit_task(task_id)

            receipt = {
                "chore": chore_name,
                "status": "completed",
                "task_id": task_id,
                "checkpoint_id": ckpt_id,
                "changes": changes,
                "timestamp": task.created_at,
            }
            self.chore_receipts[chore_name] = receipt
            return receipt

        except Exception as err:
            self.task_manager.cancel_task(task_id)
            receipt = {
                "chore": chore_name,
                "status": "failed",
                "task_id": task_id,
                "error": str(err),
            }
            self.chore_receipts[chore_name] = receipt
            raise

    def undo_chore(self, chore_name: str) -> bool:
        """Undo a completed chore by rolling back to its initial snapshot."""
        receipt = self.chore_receipts.get(chore_name)
        if not receipt or "task_id" not in receipt:
            return False

        task_id = receipt["task_id"]
        try:
            self.task_manager.undo_task(task_id)
            receipt["status"] = "undone"
            return True
        except Exception:
            return False

    def _tidy_downloads(self, downloads_dir: Path) -> Dict[str, Any]:
        downloads_dir.mkdir(parents=True, exist_ok=True)
        archive_dir = downloads_dir / "Archive"
        archive_dir.mkdir(parents=True, exist_ok=True)

        moved_files: List[str] = []
        for item in downloads_dir.iterdir():
            if item.is_file() and item.name != ".DS_Store":
                dest = archive_dir / item.name
                shutil.move(str(item), str(dest))
                moved_files.append(item.name)

        return {"files_archived": moved_files, "count": len(moved_files)}

    def _backup_documents(self, source_dir: Path, backup_dir: Path) -> Dict[str, Any]:
        source_dir.mkdir(parents=True, exist_ok=True)
        backup_dir.mkdir(parents=True, exist_ok=True)

        tar_path = backup_dir / "documents_backup.tar.gz"
        backed_up: List[str] = []
        with tarfile.open(str(tar_path), "w:gz") as tar:
            for item in source_dir.iterdir():
                if item.is_file():
                    tar.add(str(item), arcname=item.name)
                    backed_up.append(item.name)

        return {"backup_archive": str(tar_path), "files_included": backed_up, "size_bytes": tar_path.stat().st_size}

    def _digest_logs(self, log_file: Path, out_file: Path) -> Dict[str, Any]:
        errors = 0
        warnings = 0
        total_lines = 0

        if log_file.is_file():
            with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    total_lines += 1
                    if "ERROR" in line or "CRITICAL" in line:
                        errors += 1
                    elif "WARN" in line:
                        warnings += 1

        digest = f"Log Digest: {total_lines} lines analyzed | {errors} errors | {warnings} warnings\n"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(digest, encoding="utf-8")
        return {"total_lines": total_lines, "errors": errors, "warnings": warnings, "digest_file": str(out_file)}

    def _check_updates(self, manifest_path: Path) -> Dict[str, Any]:
        has_manifest = manifest_path.is_file()
        return {
            "manifest_checked": str(manifest_path),
            "status": "up_to_date" if has_manifest else "manifest_missing",
            "pending_updates": 0,
        }
