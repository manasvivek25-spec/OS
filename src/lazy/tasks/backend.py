"""Snapshot backends for lazy-tasks (Rule F5, F7).

Supports copy (reflink/fallback for host tests), overlay, and btrfs.
"""
from __future__ import annotations

import abc
import hashlib
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


class TreeHasher:
    """Computes deterministic hash of a directory tree for checkpoint verification."""

    @staticmethod
    def hash_directory(dir_path: Path | str) -> str:
        """Compute recursive SHA-256 hash of all files and relative paths in directory."""
        path = Path(dir_path)
        if not path.is_dir():
            return hashlib.sha256(b"NON_EXISTENT_DIR").hexdigest()

        h = hashlib.sha256()
        # Collect all files sorted by relative path
        all_entries: List[Path] = []
        for root, dirs, files in os.walk(path):
            dirs.sort()
            for f in sorted(files):
                all_entries.append(Path(root) / f)

        for file_path in all_entries:
            rel_path = file_path.relative_to(path).as_posix()
            h.update(rel_path.encode("utf-8"))
            try:
                content = file_path.read_bytes()
                h.update(hashlib.sha256(content).digest())
            except Exception:
                pass

        return h.hexdigest()


class SnapshotBackend(abc.ABC):
    """Abstract interface for transactional filesystem snapshot backends."""

    def __init__(self, target_dir: Path | str):
        self.target_dir = Path(target_dir)

    @abc.abstractmethod
    def create_snapshot(self, checkpoint_id: str) -> str:
        """Create a point-in-time snapshot of target_dir. Returns snapshot reference."""
        raise NotImplementedError

    @abc.abstractmethod
    def restore_snapshot(self, checkpoint_id: str) -> None:
        """Rollback target_dir to the designated checkpoint state."""
        raise NotImplementedError

    @abc.abstractmethod
    def commit_snapshot(self, checkpoint_id: str) -> None:
        """Persist current state and finalize checkpoint."""
        raise NotImplementedError

    @abc.abstractmethod
    def discard_snapshot(self, checkpoint_id: str) -> None:
        """Remove temporary snapshot without altering target_dir."""
        raise NotImplementedError


class CopyBackend(SnapshotBackend):
    """Host/CI snapshot backend using copy trees with reflink support."""

    def __init__(self, target_dir: Path | str, snapshots_root: Optional[Path | str] = None):
        super().__init__(target_dir)
        if snapshots_root is None:
            self.snapshots_root = self.target_dir.parent / ".snapshots"
        else:
            self.snapshots_root = Path(snapshots_root)
        self.snapshots_root.mkdir(parents=True, exist_ok=True)
        self._snapshots: Dict[str, Path] = {}

    def create_snapshot(self, checkpoint_id: str) -> str:
        snap_path = self.snapshots_root / checkpoint_id
        if snap_path.exists():
            shutil.rmtree(snap_path)

        if self.target_dir.exists():
            # Attempt reflink copy via cp -a --reflink=auto if available, else copytree
            try:
                ret = subprocess.run(
                    ["cp", "-a", "--reflink=auto", str(self.target_dir), str(snap_path)],
                    capture_output=True,
                    check=False,
                )
                if ret.returncode != 0:
                    shutil.copytree(self.target_dir, snap_path, symlinks=True)
            except Exception:
                shutil.copytree(self.target_dir, snap_path, symlinks=True)
        else:
            snap_path.mkdir(parents=True, exist_ok=True)

        self._snapshots[checkpoint_id] = snap_path
        return str(snap_path)

    def restore_snapshot(self, checkpoint_id: str) -> None:
        snap_path = self._snapshots.get(checkpoint_id) or (self.snapshots_root / checkpoint_id)
        if not snap_path.exists():
            raise FileNotFoundError(f"Snapshot '{checkpoint_id}' not found at {snap_path}")

        # Wipe target dir contents (preserving mountpoint and snapshot root) and restore from snapshot
        if self.target_dir.exists():
            for item in self.target_dir.iterdir():
                if item.name in ("@snapshots", ".snapshots"):
                    continue
                try:
                    if item.is_dir() and not item.is_symlink():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                except Exception:
                    pass

        if snap_path.exists():
            for item in snap_path.iterdir():
                if item.name in ("@snapshots", ".snapshots"):
                    continue
                dst = self.target_dir / item.name
                if item.is_dir() and not item.is_symlink():
                    shutil.copytree(item, dst, symlinks=True)
                else:
                    shutil.copy2(item, dst, follow_symlinks=False)

    def commit_snapshot(self, checkpoint_id: str) -> None:
        # Changes are already in target_dir; cleanup checkpoint copy
        self.discard_snapshot(checkpoint_id)

    def discard_snapshot(self, checkpoint_id: str) -> None:
        snap_path = self._snapshots.pop(checkpoint_id, None) or (self.snapshots_root / checkpoint_id)
        if snap_path.exists():
            shutil.rmtree(snap_path)


class OverlayBackend(SnapshotBackend):
    """Overlayfs snapshot backend for layered file modifications."""

    def __init__(self, target_dir: Path | str, overlay_root: Optional[Path | str] = None):
        super().__init__(target_dir)
        self.overlay_root = Path(overlay_root) if overlay_root else self.target_dir.parent / ".overlay"
        self.overlay_root.mkdir(parents=True, exist_ok=True)
        self._checkpoints: Dict[str, Path] = {}

    def create_snapshot(self, checkpoint_id: str) -> str:
        snap_dir = self.overlay_root / checkpoint_id
        snap_dir.mkdir(parents=True, exist_ok=True)
        self._checkpoints[checkpoint_id] = snap_dir
        return str(snap_dir)

    def restore_snapshot(self, checkpoint_id: str) -> None:
        # In overlay mode, clearing upperdir reverts all uncommitted modifications
        snap_dir = self._checkpoints.get(checkpoint_id)
        if snap_dir and snap_dir.exists():
            shutil.rmtree(snap_dir)
            snap_dir.mkdir(parents=True, exist_ok=True)

    def commit_snapshot(self, checkpoint_id: str) -> None:
        self.discard_snapshot(checkpoint_id)

    def discard_snapshot(self, checkpoint_id: str) -> None:
        snap_dir = self._checkpoints.pop(checkpoint_id, None)
        if snap_dir and snap_dir.exists():
            shutil.rmtree(snap_dir)


class BtrfsBackend(SnapshotBackend):
    """Native Btrfs subvolume snapshot backend for production image."""

    def __init__(self, target_dir: Path | str, snapshots_root: Optional[Path | str] = None):
        super().__init__(target_dir)
        self.snapshots_root = Path(snapshots_root) if snapshots_root else self.target_dir.parent / ".btrfs_snapshots"
        self._snapshots: Dict[str, Path] = {}

    def create_snapshot(self, checkpoint_id: str) -> str:
        self.snapshots_root.mkdir(parents=True, exist_ok=True)
        snap_path = self.snapshots_root / checkpoint_id

        # btrfs subvolume snapshot -r <source> <dest>
        try:
            res = subprocess.run(
                ["btrfs", "subvolume", "snapshot", "-r", str(self.target_dir), str(snap_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            if res.returncode != 0:
                fallback = CopyBackend(self.target_dir, self.snapshots_root)
                return fallback.create_snapshot(checkpoint_id)
        except Exception:
            fallback = CopyBackend(self.target_dir, self.snapshots_root)
            return fallback.create_snapshot(checkpoint_id)

        self._snapshots[checkpoint_id] = snap_path
        return str(snap_path)

    def restore_snapshot(self, checkpoint_id: str) -> None:
        snap_path = self._snapshots.get(checkpoint_id) or (self.snapshots_root / checkpoint_id)
        if not snap_path.exists():
            fallback = CopyBackend(self.target_dir, self.snapshots_root)
            fallback.restore_snapshot(checkpoint_id)
            return

        try:
            del_res = subprocess.run(["btrfs", "subvolume", "delete", str(self.target_dir)], capture_output=True, check=False)
            if del_res.returncode != 0:
                fallback = CopyBackend(self.target_dir, self.snapshots_root)
                fallback.restore_snapshot(checkpoint_id)
                return
            subprocess.run(["btrfs", "subvolume", "snapshot", str(snap_path), str(self.target_dir)], capture_output=True, check=False)
        except Exception:
            fallback = CopyBackend(self.target_dir, self.snapshots_root)
            fallback.restore_snapshot(checkpoint_id)

    def commit_snapshot(self, checkpoint_id: str) -> None:
        self.discard_snapshot(checkpoint_id)

    def discard_snapshot(self, checkpoint_id: str) -> None:
        snap_path = self._snapshots.pop(checkpoint_id, None) or (self.snapshots_root / checkpoint_id)
        if snap_path.exists():
            try:
                subprocess.run(["btrfs", "subvolume", "delete", str(snap_path)], capture_output=True, check=False)
            except Exception:
                shutil.rmtree(snap_path, ignore_errors=True)
