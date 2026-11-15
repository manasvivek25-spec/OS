"""Unit tests for lazy-tasks, snapshot backends and undo (Rules F5, F7).

Exit criteria M1.3:
- discard returns the tree to its pre-task hash
- commit persists
- cancel mid-task works
Line coverage >= 90%.
"""

from pathlib import Path
import pytest

from lazy.common.contracts import validate_contract
from lazy.tasks import (
    BtrfsBackend,
    CopyBackend,
    OverlayBackend,
    TaskManager,
    TreeHasher,
)


@pytest.fixture
def test_env(tmp_path: Path):
    target_dir = tmp_path / "workdir"
    target_dir.mkdir(parents=True, exist_ok=True)
    # Create baseline file
    (target_dir / "base.txt").write_text("initial base content\n", encoding="utf-8")
    return target_dir, tmp_path / "snapshots"


# ==============================================================================
# 1. TREE HASHER INTEGRITY
# ==============================================================================

def test_tree_hasher_deterministic(test_env):
    target_dir, _ = test_env
    h1 = TreeHasher.hash_directory(target_dir)
    h2 = TreeHasher.hash_directory(target_dir)
    assert h1 == h2

    # Modification alters hash
    (target_dir / "new_file.txt").write_text("added", encoding="utf-8")
    h3 = TreeHasher.hash_directory(target_dir)
    assert h1 != h3

    # Deletion alters hash
    (target_dir / "new_file.txt").unlink()
    h4 = TreeHasher.hash_directory(target_dir)
    assert h1 == h4


# ==============================================================================
# 2. SNAPSHOT BACKENDS (COPY, OVERLAY, BTRFS)
# ==============================================================================

def test_copy_backend_snapshot_and_restore(test_env):
    target_dir, snap_root = test_env
    backend = CopyBackend(target_dir, snap_root)
    pre_hash = TreeHasher.hash_directory(target_dir)

    # 1. Create snapshot
    snap_ref = backend.create_snapshot("chk-01")
    assert Path(snap_ref).exists()

    # 2. Modify target dir
    (target_dir / "pollute.txt").write_text("bad data", encoding="utf-8")
    (target_dir / "base.txt").write_text("overwritten", encoding="utf-8")
    assert TreeHasher.hash_directory(target_dir) != pre_hash

    # 3. Restore snapshot (discard uncommitted)
    backend.restore_snapshot("chk-01")
    post_hash = TreeHasher.hash_directory(target_dir)
    assert post_hash == pre_hash
    assert not (target_dir / "pollute.txt").exists()
    assert (target_dir / "base.txt").read_text(encoding="utf-8") == "initial base content\n"

    # 4. Commit snapshot cleanup
    backend.commit_snapshot("chk-01")
    assert not Path(snap_ref).exists()


def test_overlay_backend_lifecycle(test_env):
    target_dir, snap_root = test_env
    backend = OverlayBackend(target_dir, snap_root)
    snap_ref = backend.create_snapshot("ovl-01")
    assert Path(snap_ref).exists()
    backend.restore_snapshot("ovl-01")
    backend.commit_snapshot("ovl-01")
    assert not Path(snap_ref).exists()


def test_btrfs_backend_lifecycle(test_env):
    target_dir, snap_root = test_env
    backend = BtrfsBackend(target_dir, snap_root)
    snap_ref = backend.create_snapshot("btr-01")
    assert snap_ref is not None
    backend.restore_snapshot("btr-01")
    backend.commit_snapshot("btr-01")


# ==============================================================================
# 3. TASK MANAGER WORKFLOW & EXIT CRITERIA
# ==============================================================================

def test_task_commit_persists(test_env):
    """[M1.3 Exit Criterion] commit persists modifications."""
    target_dir, snap_root = test_env
    manager = TaskManager(target_dir, backend_type="copy", snapshots_root=snap_root)

    task = manager.create_task("task-commit-test")
    assert task.status == "pending"

    # Step 0
    cp_id = manager.checkpoint_before_step(task.id, "intent-01", 0)
    assert task.status == "running"

    # Execute modification
    (target_dir / "result.md").write_text("# Project Completed\n", encoding="utf-8")
    manager.finish_step(task.id, 0, {"status": "ok"})

    # Commit task
    manager.commit_task(task.id)
    assert task.status == "completed"
    assert (target_dir / "result.md").exists()
    assert (target_dir / "result.md").read_text(encoding="utf-8") == "# Project Completed\n"


def test_cancel_mid_task_returns_tree_to_pre_task_hash(test_env):
    """[M1.3 Exit Criterion] cancel mid-task rolls back to pre-task hash."""
    target_dir, snap_root = test_env
    manager = TaskManager(target_dir, backend_type="copy", snapshots_root=snap_root)

    task = manager.create_task("task-cancel-test")
    initial_hash = task.initial_pre_hash

    # Step 0: checkpoint and execute destructive changes
    manager.checkpoint_before_step(task.id, "intent-01", 0)
    (target_dir / "corrupted.bin").write_bytes(b"\x00\xFF" * 100)
    (target_dir / "base.txt").unlink()  # deleted base file

    mid_hash = TreeHasher.hash_directory(target_dir)
    assert mid_hash != initial_hash

    # Cancel task mid-execution!
    post_cancel_hash = manager.cancel_task(task.id)

    # Verification: Tree hash matches initial pre-task hash exactly!
    assert post_cancel_hash == initial_hash
    assert task.status == "cancelled"
    assert not (target_dir / "corrupted.bin").exists()
    assert (target_dir / "base.txt").exists()
    assert (target_dir / "base.txt").read_text(encoding="utf-8") == "initial base content\n"


def test_task_undo_reverts_completed_work(test_env):
    """[F7] Undo returns the tree to pre-task hash after task completion."""
    target_dir, snap_root = test_env
    manager = TaskManager(target_dir, backend_type="copy", snapshots_root=snap_root)

    task = manager.create_task("task-undo-test")
    initial_hash = task.initial_pre_hash

    # Step 0
    manager.checkpoint_before_step(task.id, "intent-01", 0)
    (target_dir / "extra.log").write_text("extra log\n", encoding="utf-8")
    manager.finish_step(task.id, 0, {"ok": True})

    # Step 1
    manager.checkpoint_before_step(task.id, "intent-02", 1)
    (target_dir / "another.txt").write_text("another\n", encoding="utf-8")
    manager.finish_step(task.id, 1, {"ok": True})

    # Undo task
    undo_hash = manager.undo_task(task.id)
    assert undo_hash == initial_hash
    assert not (target_dir / "extra.log").exists()
    assert not (target_dir / "another.txt").exists()


def test_task_contract_schema_validation(test_env):
    """Verify that generated Task records conform to docs/contracts/task.schema.json."""
    target_dir, snap_root = test_env
    manager = TaskManager(target_dir, backend_type="copy", snapshots_root=snap_root)

    task = manager.create_task("task-contract-check")
    manager.checkpoint_before_step(task.id, "intent-01", 0)
    manager.finish_step(task.id, 0, {"result": "success"})
    manager.commit_task(task.id)

    is_valid, err = validate_contract("task", task.to_dict())
    assert is_valid, f"Task schema validation failed: {err}"


def test_rollback_to_specific_checkpoint(test_env):
    """Verify rollback_to_checkpoint restores state to target checkpoint."""
    target_dir, snap_root = test_env
    manager = TaskManager(target_dir, backend_type="copy", snapshots_root=snap_root)

    task = manager.create_task("task-chk-test")
    assert manager.get_task("task-chk-test") is not None

    # Checkpoint 1
    cp1 = manager.checkpoint_before_step(task.id, "intent-01", 0)
    (target_dir / "step1.txt").write_text("v1", encoding="utf-8")
    manager.finish_step(task.id, 0, {"ok": True})
    hash1 = TreeHasher.hash_directory(target_dir)

    # Checkpoint 2
    cp2 = manager.checkpoint_before_step(task.id, "intent-02", 1)
    (target_dir / "step2.txt").write_text("v2", encoding="utf-8")
    manager.finish_step(task.id, 1, {"ok": True})

    # Rollback to checkpoint 2 (which preserved state after step 1)
    restored_hash = manager.rollback_to_checkpoint(task.id, cp2)
    assert restored_hash == hash1
    assert not (target_dir / "step2.txt").exists()
    assert (target_dir / "step1.txt").exists()


def test_task_manager_error_handling(test_env):
    """Verify TaskManager raises KeyError on non-existent task IDs."""
    target_dir, snap_root = test_env
    manager = TaskManager(target_dir, backend_type="copy", snapshots_root=snap_root)

    with pytest.raises(KeyError):
        manager.checkpoint_before_step("non-existent", "i-1", 0)

    with pytest.raises(KeyError):
        manager.finish_step("non-existent", 0, {})

    with pytest.raises(KeyError):
        manager.commit_task("non-existent")

    with pytest.raises(KeyError):
        manager.rollback_to_checkpoint("non-existent", "cp-1")

    with pytest.raises(KeyError):
        manager.cancel_task("non-existent")


def test_cancel_task_with_no_checkpoints(test_env):
    """Verify canceling task before any steps wipes newly created files."""
    target_dir, snap_root = test_env
    manager = TaskManager(target_dir, backend_type="copy", snapshots_root=snap_root)
    task = manager.create_task("task-no-checkpoints")

    (target_dir / "dirty.tmp").write_text("junk", encoding="utf-8")
    manager.cancel_task(task.id)
    assert task.status == "cancelled"
    assert not (target_dir / "dirty.tmp").exists()


def test_tree_hasher_non_existent_directory(tmp_path: Path):
    """Verify TreeHasher handles missing directories gracefully."""
    non_existent = tmp_path / "does_not_exist"
    h = TreeHasher.hash_directory(non_existent)
    assert len(h) == 64


def test_backend_default_roots(test_env):
    """Verify backends construct default snapshot paths when unspecified."""
    target_dir, _ = test_env
    cp_backend = CopyBackend(target_dir)
    assert cp_backend.snapshots_root == target_dir.parent / ".snapshots"

    ov_backend = OverlayBackend(target_dir)
    assert ov_backend.overlay_root == target_dir.parent / ".overlay"


def test_tree_hasher_empty_directory(tmp_path: Path):
    """Verify TreeHasher handles completely empty directories."""
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()
    h = TreeHasher.hash_directory(empty_dir)
    assert len(h) == 64


def test_copy_backend_target_dir_not_exists(tmp_path: Path):
    """Verify CopyBackend handles creating snapshot when target_dir does not exist."""
    missing_dir = tmp_path / "missing_workdir"
    backend = CopyBackend(missing_dir, tmp_path / "snaps")
    snap = backend.create_snapshot("chk_missing")
    assert Path(snap).exists()


def test_btrfs_restore_missing_snapshot(test_env):
    """Verify BtrfsBackend triggers fallback on missing snapshot reference."""
    target_dir, snap_root = test_env
    backend = BtrfsBackend(target_dir, snap_root)
    with pytest.raises(FileNotFoundError):
        backend.restore_snapshot("missing_chk")
