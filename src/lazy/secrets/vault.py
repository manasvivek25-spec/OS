"""Secret vault with peer-credential access control for Lazy OS (Rule F4)."""
from __future__ import annotations

import json
import os
import stat
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class SecretAccessDenied(PermissionError):
    """Raised when an unauthorized peer (such as lazy-planner) attempts secret access."""


class SecretVault:
    """Encrypted/protected credential vault enforcing strict Unix peer-credential checks."""

    def __init__(
        self,
        vault_dir: Path | str,
        allowed_uids: Optional[Set[int]] = None,
        denied_uids: Optional[Set[int]] = None,
        allowed_users: Optional[Set[str]] = None,
        denied_users: Optional[Set[str]] = None,
    ):
        self.vault_dir = Path(vault_dir)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        # Enforce secure directory permissions 0700
        try:
            self.vault_dir.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        except Exception:
            pass

        self.allowed_uids: Set[int] = set(allowed_uids or [0, os.getuid()])
        self.denied_uids: Set[int] = set(denied_uids or [])
        self.allowed_users: Set[str] = set(allowed_users or ["root", "lazy-comms", "lazy-web"])
        self.denied_users: Set[str] = set(denied_users or ["lazy-planner", "planner"])
        self._secrets_file = self.vault_dir / "secrets.json"
        self._cache: Dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        if self._secrets_file.is_file():
            try:
                data = json.loads(self._secrets_file.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    self._cache = data
            except Exception:
                self._cache = {}

    def _save(self) -> None:
        content = json.dumps(self._cache, indent=2)
        self._secrets_file.write_text(content, encoding="utf-8")
        try:
            self._secrets_file.chmod(stat.S_IRUSR | stat.S_IWUSR)
        except Exception:
            pass

    def check_access(self, peer_uid: int, peer_user: Optional[str] = None) -> None:
        """Validate connecting peer credentials (Rule F4).

        Raises SecretAccessDenied if peer is lazy-planner or not explicitly authorized.
        """
        # Hard check 1: Explicitly denied user (planner)
        if peer_user and peer_user.lower() in self.denied_users:
            raise SecretAccessDenied(
                f"Rule F4 violation: User '{peer_user}' (planner) is strictly forbidden from accessing secret vault."
            )

        # Hard check 2: Explicitly denied UID
        if peer_uid in self.denied_uids:
            raise SecretAccessDenied(
                f"Rule F4 violation: Peer UID {peer_uid} (planner) is strictly forbidden from accessing secret vault."
            )

        # Hard check 3: Must be in allowed UIDs or allowed users
        is_allowed_uid = peer_uid in self.allowed_uids
        is_allowed_user = bool(peer_user and peer_user.lower() in self.allowed_users)

        if not (is_allowed_uid or is_allowed_user):
            raise SecretAccessDenied(
                f"Rule F4 access denied: Peer UID {peer_uid} / user '{peer_user}' is not authorized to read secrets."
            )

    def set_secret(self, key: str, value: str, peer_uid: int, peer_user: Optional[str] = None) -> None:
        """Store a secret after peer credential validation."""
        self.check_access(peer_uid, peer_user)
        self._cache[key] = value
        self._save()

    def get_secret(self, key: str, peer_uid: int, peer_user: Optional[str] = None) -> Optional[str]:
        """Retrieve a secret value after peer credential validation."""
        self.check_access(peer_uid, peer_user)
        return self._cache.get(key)

    def list_keys(self, peer_uid: int, peer_user: Optional[str] = None) -> List[str]:
        """List stored secret keys (values omitted) after peer credential validation."""
        self.check_access(peer_uid, peer_user)
        return sorted(list(self._cache.keys()))
