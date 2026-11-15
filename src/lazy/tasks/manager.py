"""Task execution, checkpointing and rollback manager for Lazy OS (Rule F5, F7)."""
from __future__ import annotations

import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from lazy.tasks.backend import CopyBackend, SnapshotBackend, TreeHasher


class Task:
    """Represents a tracked, checkpointed, and undoable job."""

    def __init__(self, task_id: str, backend: SnapshotBackend, target_dir: Path | str):
        self.id = task_id
        self.backend = backend
        self.target_dir = Path(target_dir)
        self.status = "pending"
        self.steps: List[Dict[str, Any]] = []
        self.checkpoints: List[Dict[str, Any]] = []
        now = datetime.now(timezone.utc).isoformat()
        self.created_at = now
        self.updated_at = now
        self.initial_pre_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "status": self.status,
            "steps": self.steps,
            "checkpoints": self.checkpoints,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class TaskManager:
    """Coordinates job executions, checkpoints, snapshots, and transactional rollbacks."""

    def __init__(self, target_dir: Path | str, backend_type: str = "copy", snapshots_root: Optional[Path | str] = None):
        self.target_dir = Path(target_dir)
        self.target_dir.mkdir(parents=True, exist_ok=True)
        self.backend_type = backend_type

        if backend_type == "copy":
            self.backend: SnapshotBackend = CopyBackend(self.target_dir, snapshots_root)
        else:
            self.backend = CopyBackend(self.target_dir, snapshots_root)

        self._tasks: Dict[str, Task] = {}

    def create_task(self, task_id: Optional[str] = None) -> Task:
        """Initialize a new task tracking instance."""
        tid = task_id or f"task-{uuid.uuid4().hex[:8]}"
        task = Task(task_id=tid, backend=self.backend, target_dir=self.target_dir)
        # Capture baseline initial tree hash
        task.initial_pre_hash = TreeHasher.hash_directory(self.target_dir)
        # Create baseline pre-task snapshot for rollback and undo (Rule F5, F7)
        base_ckpt_id = f"snap-{tid}-base"
        self.backend.create_snapshot(base_ckpt_id)
        task.checkpoints.append({
            "id": base_ckpt_id,
            "ts": datetime.now(timezone.utc).isoformat(),
            "backend": self.backend_type,
            "reference": str(self.backend.snapshots_root / base_ckpt_id),
            "pre_hash": task.initial_pre_hash,
        })
        self._tasks[tid] = task
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def checkpoint_before_step(self, task_id: str, intent_id: str, step_index: int) -> str:
        """Create a point-in-time filesystem checkpoint before executing an intent step (Rule F5)."""
        task = self._tasks.get(task_id)
        if task is None:
            raise KeyError(f"Task '{task_id}' not found.")

        task.status = "running"
        task.updated_at = datetime.now(timezone.utc).isoformat()

        checkpoint_id = f"snap-{task_id}-step-{step_index}"
        pre_hash = TreeHasher.hash_directory(self.target_dir)
        snap_ref = self.backend.create_snapshot(checkpoint_id)

        checkpoint_record = {
            "id": checkpoint_id,
            "ts": datetime.now(timezone.utc).isoformat(),
            "backend": self.backend_type,
            "reference": snap_ref,
            "pre_hash": pre_hash,
        }
        task.checkpoints.append(checkpoint_record)

        step_record = {
            "step_index": step_index,
            "intent_id": intent_id,
            "status": "running",
            "checkpoint_id": checkpoint_id,
        }
        task.steps.append(step_record)
        return checkpoint_id

    def finish_step(self, task_id: str, step_index: int, result: Dict[str, Any]) -> None:
        """Mark step complete and commit local state."""
        task = self._tasks.get(task_id)
        if task is None:
            raise KeyError(f"Task '{task_id}' not found.")

        for step in task.steps:
            if step["step_index"] == step_index:
                step["status"] = "done"
                step["result"] = result
                break
        task.updated_at = datetime.now(timezone.utc).isoformat()

    def commit_task(self, task_id: str) -> None:
        """Commit all changes made during the task and mark completed."""
        task = self._tasks.get(task_id)
        if task is None:
            raise KeyError(f"Task '{task_id}' not found.")

        # Discard intermediate step checkpoints to save space; retain base snapshot for undo (Rule F7)
        for cp in task.checkpoints[1:]:
            self.backend.commit_snapshot(cp["id"])

        task.status = "completed"
        task.updated_at = datetime.now(timezone.utc).isoformat()

    def rollback_to_checkpoint(self, task_id: str, checkpoint_id: str) -> str:
        """Revert working directory to a specific checkpoint. Returns resulting tree hash."""
        task = self._tasks.get(task_id)
        if task is None:
            raise KeyError(f"Task '{task_id}' not found.")

        self.backend.restore_snapshot(checkpoint_id)
        post_hash = TreeHasher.hash_directory(self.target_dir)
        return post_hash

    def cancel_task(self, task_id: str) -> str:
        """Cancel running task mid-execution and rollback to initial pre-task checkpoint (Rule F5, F7)."""
        task = self._tasks.get(task_id)
        if task is None:
            raise KeyError(f"Task '{task_id}' not found.")

        if task.checkpoints:
            base_checkpoint = task.checkpoints[0]["id"]
            self.backend.restore_snapshot(base_checkpoint)

        for step in task.steps:
            if step["status"] == "running":
                step["status"] = "undone"

        task.status = "cancelled"
        task.updated_at = datetime.now(timezone.utc).isoformat()
        return TreeHasher.hash_directory(self.target_dir)

    def undo_task(self, task_id: str) -> str:
        """Undo a completed task by restoring the earliest checkpoint (Rule F7)."""
        return self.cancel_task(task_id)
