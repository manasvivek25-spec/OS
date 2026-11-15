"""Correction rules engine for Lazy OS dialogue manager."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml


class CorrectionEngine:
    """Matches conversational user corrections and updates intent parameters."""

    def __init__(self, config_path: Optional[Path | str] = None):
        if config_path:
            self.config_path = Path(config_path)
        else:
            repo_root = Path(__file__).resolve().parent.parent.parent.parent
            self.config_path = repo_root / "config" / "corrections.yaml"

        self.rules: List[Dict[str, Any]] = []
        self._load_rules()

    def _load_rules(self) -> None:
        if not self.config_path.is_file():
            return
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            self.rules = data.get("rules", []) if isinstance(data, dict) else []

    def match_and_apply(
        self, user_text: str, current_params: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """Attempt to match user text against correction rules and patch params."""
        normalized = user_text.strip().lower()
        new_params = dict(current_params)

        for rule in self.rules:
            rule_id = rule.get("id", "unknown")
            target_param = rule.get("target_param")
            cast_type = rule.get("cast_type")
            patterns = rule.get("trigger_patterns", [])

            for pat in patterns:
                match = re.search(pat, normalized, re.IGNORECASE)
                if match:
                    group_dict = match.groupdict()
                    val = group_dict.get(target_param) or match.group(1) if match.groups() else None
                    if val is not None:
                        if cast_type == "int":
                            try:
                                val = int(val)
                            except ValueError:
                                continue
                        new_params[target_param] = val
                        return True, rule_id, new_params

        return False, None, new_params
