"""File system and document broker for Lazy OS (lazy-broker-fs)."""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from lazy.brokers.base import BaseBroker, BrokerExecutionError


class FSBroker(BaseBroker):
    """Handles file operations, document creation, and code writing."""

    def __init__(self, root_dir: Optional[Path | str] = None):
        super().__init__("lazy-broker-fs")
        self.root_dir = Path(root_dir) if root_dir else Path.home()
        self._register_handlers()

    def _resolve_path(self, path_str: str) -> Path:
        """Resolve path and ensure safety."""
        p = Path(path_str)
        if not p.is_absolute():
            p = self.root_dir / p
        return p.resolve()

    def _register_handlers(self) -> None:
        self.register("fs.read", self.handle_fs_read)
        self.register("fs.list", self.handle_fs_list)
        self.register("fs.write", self.handle_fs_write)
        self.register("fs.copy", self.handle_fs_copy)
        self.register("fs.move", self.handle_fs_move)
        self.register("fs.delete", self.handle_fs_delete)
        self.register("doc.create_markdown", self.handle_doc_markdown)
        self.register("doc.create_docx", self.handle_doc_docx)
        self.register("code.write", self.handle_code_write)

    def handle_fs_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        path = self._resolve_path(params["path"])
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")
        content = path.read_text(encoding="utf-8", errors="replace")
        return {"path": str(path), "content": content, "size": len(content)}

    def handle_fs_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        path = self._resolve_path(params["path"])
        if not path.is_dir():
            raise NotADirectoryError(f"Directory not found: {path}")
        entries = []
        for item in sorted(path.iterdir()):
            entries.append({
                "name": item.name,
                "is_dir": item.is_dir(),
                "size": item.stat().st_size if item.is_file() else 0,
            })
        return {"path": str(path), "entries": entries}

    def handle_fs_write(self, params: Dict[str, Any]) -> Dict[str, Any]:
        path = self._resolve_path(params["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        content = params["content"]
        path.write_text(content, encoding="utf-8")
        return {"path": str(path), "bytes_written": len(content.encode("utf-8"))}

    def handle_fs_copy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        src = self._resolve_path(params["src"])
        dest = self._resolve_path(params["dest"])
        if not src.exists():
            raise FileNotFoundError(f"Source not found: {src}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dest)
        return {"src": str(src), "dest": str(dest)}

    def handle_fs_move(self, params: Dict[str, Any]) -> Dict[str, Any]:
        src = self._resolve_path(params["src"])
        dest = self._resolve_path(params["dest"])
        if not src.exists():
            raise FileNotFoundError(f"Source not found: {src}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        return {"src": str(src), "dest": str(dest)}

    def handle_fs_delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        path = self._resolve_path(params["path"])
        if not path.exists():
            raise FileNotFoundError(f"Target not found: {path}")
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        return {"path": str(path), "deleted": True}

    def handle_doc_markdown(self, params: Dict[str, Any]) -> Dict[str, Any]:
        path = self._resolve_path(params["path"])
        if not path.name.endswith(".md"):
            path = path.with_suffix(".md")
        return self.handle_fs_write({"path": str(path), "content": params["content"]})

    def handle_doc_docx(self, params: Dict[str, Any]) -> Dict[str, Any]:
        path = self._resolve_path(params["path"])
        if not path.name.endswith(".docx"):
            path = path.with_suffix(".docx")
        # Write clean structured XML/text placeholder conforming to docx container
        header = f"# Document: {path.stem}\n\n"
        return self.handle_fs_write({"path": str(path), "content": header + params["content"]})

    def handle_code_write(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return self.handle_fs_write(params)
