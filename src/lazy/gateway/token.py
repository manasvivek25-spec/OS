"""HUD authentication token management for lazy-gateway."""
from __future__ import annotations

import hmac
import os
import secrets
from pathlib import Path
from typing import Optional


class HUDTokenManager:
    """Generates, persists, and validates ephemeral HUD session tokens."""

    def __init__(self, token_path: Optional[Path | str] = None, explicit_token: Optional[str] = None):
        self.token_path = Path(token_path) if token_path else None
        if explicit_token:
            self._token = explicit_token
        else:
            self._token = secrets.token_hex(32)

        if self.token_path:
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            self.token_path.write_text(self._token, encoding="utf-8")
            try:
                self.token_path.chmod(0o600)
            except Exception:
                pass

    @property
    def token(self) -> str:
        return self._token

    def validate(self, candidate_token: str) -> bool:
        """Constant-time token validation against timing attacks."""
        if not candidate_token:
            return False
        return hmac.compare_digest(self._token, candidate_token.strip())
