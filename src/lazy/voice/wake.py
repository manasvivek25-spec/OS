"""Restricted-grammar wake phrase detector for Lazy OS (default: wake up, daddy's home)."""
from __future__ import annotations

import re
import time
from pathlib import Path
from typing import List, Optional, Tuple

import yaml


class WakeDetector:
    """Detects wake phrases with exact and normalized grammar recognition."""

    DEFAULT_PHRASE = "wake up, daddy's home"

    def __init__(self, config_path: Optional[Path | str] = None, phrase: Optional[str] = None):
        self.wake_phrases: List[str] = []

        if phrase:
            self.wake_phrases.append(self._normalize(phrase))
        else:
            repo_root = Path(__file__).resolve().parent.parent.parent.parent
            cfg = Path(config_path) if config_path else repo_root / "config" / "voice.yaml"
            if cfg.is_file():
                try:
                    data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
                    main_phrase = data.get("wake_phrase", self.DEFAULT_PHRASE)
                    self.wake_phrases.append(self._normalize(main_phrase))
                    for alt in data.get("alternative_wake_phrases", []):
                        self.wake_phrases.append(self._normalize(alt))
                except Exception:
                    self.wake_phrases.append(self._normalize(self.DEFAULT_PHRASE))
            else:
                self.wake_phrases.append(self._normalize(self.DEFAULT_PHRASE))

    def _normalize(self, text: str) -> str:
        """Strip punctuation and normalize whitespace."""
        cleaned = re.sub(r"[^\w\s]", "", text.lower())
        return " ".join(cleaned.split())

    def is_wake_phrase(self, text: str) -> bool:
        """Check if text exactly or predominantly matches a wake phrase."""
        norm = self._normalize(text)
        return any(phrase == norm or phrase in norm for phrase in self.wake_phrases)

    def extract_directive(self, text: str) -> Tuple[bool, Optional[str], float]:
        """Check for wake phrase and extract subsequent directive. Returns (wake_detected, remainder_text, latency_ms)."""
        t0 = time.perf_counter()
        norm = self._normalize(text)

        for phrase in self.wake_phrases:
            if phrase in norm:
                # Find index where phrase ends
                idx = norm.find(phrase) + len(phrase)
                remainder = norm[idx:].strip()
                latency_ms = (time.perf_counter() - t0) * 1000.0
                return True, remainder if remainder else None, latency_ms

        latency_ms = (time.perf_counter() - t0) * 1000.0
        return False, None, latency_ms
