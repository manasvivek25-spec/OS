"""Taint tracking and provenance verification for lazy-policy (Rules F3, F4, F8)."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple


UNTRUSTED_SOURCES: Set[str] = {
    "web",
    "web_scrape",
    "email_body",
    "email_incoming",
    "chat_incoming",
    "rss",
    "feed",
    "document_external",
    "untrusted_data",
}

SENSITIVE_PARAM_KEYS: Set[str] = {
    "to",
    "recipient",
    "dest_email",
    "forward_to",
    "url",
    "target_url",
    "new_domain",
    "password",
    "token",
    "secret",
    "api_key",
    "credential",
}


class TaintTracker:
    """Evaluates intent parameters against provenance records to prevent prompt injection taint."""

    @staticmethod
    def is_tainted_provenance(provenance: List[Dict[str, Any]]) -> bool:
        """Check if any provenance entry is marked untrusted or originates from untrusted sources."""
        if not provenance:
            return False

        for entry in provenance:
            if not entry.get("trusted", True):
                return True
            src = entry.get("source", "").lower()
            if src in UNTRUSTED_SOURCES:
                return True
        return False

    @staticmethod
    def check_taint(
        capability_name: str,
        params: Dict[str, Any],
        provenance: List[Dict[str, Any]],
        disallowed_keys: Optional[List[str]] = None,
        require_user_confirmation: bool = False,
    ) -> Tuple[bool, Optional[str]]:
        """Verify that untrusted input has not flowed into sensitive execution parameters (Rule F8).

        Returns: (is_safe, error_message)
        """
        is_tainted = TaintTracker.is_tainted_provenance(provenance)

        # 1. Hard check: Credentials in parameters are strictly prohibited (Rule F4)
        for key in params:
            if key.lower() in {"password", "token", "secret", "api_key", "private_key"}:
                return False, f"Rule F4 violation: Credential parameter '{key}' is not allowed in intent."

        # If not tainted, check passes
        if not is_tainted:
            return True, None

        # 2. If tainted, check for sensitive destination parameters
        keys_to_check = set(disallowed_keys or [])
        keys_to_check.update(SENSITIVE_PARAM_KEYS)

        for param_key in params:
            if param_key in keys_to_check:
                val = params[param_key]
                if val:  # Non-empty sensitive parameter from untrusted source
                    return (
                        False,
                        f"Rule F8 violation: Parameter '{param_key}' derives from untrusted provenance without user confirmation.",
                    )

        return True, None
