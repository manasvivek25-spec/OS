"""Capability manifest loader and validator for lazy-policy."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from lazy.common.contracts import validate_contract


class CapabilityManifest:
    """Represents a validated capability manifest."""

    def __init__(self, data: Dict[str, Any]):
        self.name: str = data["name"]
        self.description: str = data.get("description", "")
        self.params_schema: Dict[str, Any] = data["params_schema"]
        self.tier: str = data["tier"]
        self.effect_class: str = data["effect_class"]
        self.approval_mode: str = data["approval_mode"]
        self.sandbox_profile: str = data["sandbox_profile"]
        self.undo_method: str = data["undo_method"]
        self.taint_rules: Dict[str, Any] = data.get("taint_rules", {})
        self.raw: Dict[str, Any] = data

    def to_dict(self) -> Dict[str, Any]:
        return self.raw


class ManifestLoader:
    """Discovers, validates and loads capability manifests."""

    def __init__(self, manifest_dirs: Optional[List[Path | str]] = None):
        if manifest_dirs is None:
            # Default search roots: local repo config and system etc
            repo_root = Path(__file__).resolve().parent.parent.parent.parent
            self.manifest_dirs = [
                repo_root / "config" / "capabilities",
                Path("/etc/lazy/capabilities"),
            ]
        else:
            self.manifest_dirs = [Path(d) for d in manifest_dirs]

        self._capabilities: Dict[str, CapabilityManifest] = {}
        self.reload()

    def reload(self) -> None:
        """Scan directories and load all valid manifests."""
        self._capabilities.clear()
        for directory in self.manifest_dirs:
            if not directory.is_dir():
                continue
            for fpath in directory.glob("*.yaml"):
                try:
                    data = yaml.safe_load(fpath.read_text(encoding="utf-8"))
                    is_valid, err = validate_contract("capability_manifest", data)
                    if is_valid and isinstance(data, dict) and "name" in data:
                        self._capabilities[data["name"]] = CapabilityManifest(data)
                except Exception:
                    # Ignore invalid or non-manifest yaml during scan
                    continue

    def get(self, name: str) -> Optional[CapabilityManifest]:
        """Lookup capability manifest by name."""
        return self._capabilities.get(name)

    def list_capabilities(self) -> List[str]:
        """Return list of all registered capability names."""
        return sorted(list(self._capabilities.keys()))

    def __contains__(self, name: str) -> bool:
        return name in self._capabilities
