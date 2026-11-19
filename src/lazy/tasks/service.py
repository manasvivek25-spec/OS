"""Task manager and snapshot undo service for lazy-tasks."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict
from lazy.common.socket_server import UnixSocketServer, parse_socket_arg
from lazy.tasks.manager import TaskManager


def main():
    sock = parse_socket_arg("tasks")
    target_dir = os.environ.get("LAZY_TASKS_TARGET", "/data/home/lazy")
    snapshots_dir = os.environ.get("LAZY_SNAPSHOTS_DIR", "/data/snapshots")
    backend_type = "btrfs" if os.path.exists("/data") else "copy"
    try:
        manager = TaskManager(target_dir=target_dir, backend_type=backend_type, snapshots_root=snapshots_dir)
    except Exception:
        manager = TaskManager(target_dir=target_dir, backend_type="copy", snapshots_root=snapshots_dir)

    srv = UnixSocketServer(sock, service_name="lazy-tasks")

    def handle_create(params: Dict[str, Any]) -> Dict[str, Any]:
        task = manager.create_task(task_id=params.get("task_id"))
        return {"status": "ok", "task": task.to_dict()}

    def handle_get(params: Dict[str, Any]) -> Dict[str, Any]:
        task = manager.get_task(params["task_id"])
        if not task:
            return {"status": "error", "error": "Task not found"}
        return {"status": "ok", "task": task.to_dict()}

    def handle_checkpoint(params: Dict[str, Any]) -> Dict[str, Any]:
        cp = manager.checkpoint_before_step(params["task_id"], params["intent_id"], params["step_index"])
        return {"status": "ok", "checkpoint_id": cp}

    def handle_commit(params: Dict[str, Any]) -> Dict[str, Any]:
        manager.commit_task(params["task_id"])
        return {"status": "ok"}

    def handle_undo(params: Dict[str, Any]) -> Dict[str, Any]:
        res = manager.undo_task(params["task_id"])
        return {"status": "ok", "result": res}

    def handle_rollback(params: Dict[str, Any]) -> Dict[str, Any]:
        res = manager.rollback_to_checkpoint(params["task_id"], params["checkpoint_id"])
        return {"status": "ok", "result": res}

    srv.register_simple("tasks.create", handle_create)
    srv.register_simple("tasks.get", handle_get)
    srv.register_simple("tasks.checkpoint", handle_checkpoint)
    srv.register_simple("tasks.commit", handle_commit)
    srv.register_simple("tasks.undo", handle_undo)
    srv.register_simple("tasks.rollback", handle_rollback)
    srv.serve_forever()


if __name__ == "__main__":
    main()
