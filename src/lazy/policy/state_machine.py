"""Approval state machine for lazy-policy (pending, approved, denied, expired)."""
from __future__ import annotations

import enum
import time
from typing import Any, Dict, Optional, Tuple


class ApprovalState(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"


class ApprovalRequest:
    """Represents an interactive approval request for L2/L3 capabilities."""

    def __init__(
        self,
        request_id: str,
        intent_id: str,
        capability: str,
        tier: str,
        params: Dict[str, Any],
        preview: str,
        timeout_seconds: float = 300.0,
        requested_at: Optional[float] = None,
    ):
        self.request_id = request_id
        self.intent_id = intent_id
        self.capability = capability
        self.tier = tier
        self.params = params
        self.preview = preview
        self.timeout_seconds = timeout_seconds
        self.requested_at = requested_at if requested_at is not None else time.time()
        self.decided_at: Optional[float] = None
        self.state: ApprovalState = ApprovalState.PENDING
        self.approver: Optional[str] = None
        self.approval_mode: Optional[str] = None
        self.decision_reason: Optional[str] = None

    def is_expired(self, current_time: Optional[float] = None) -> bool:
        """Check if request has timed out while still pending."""
        if self.state != ApprovalState.PENDING:
            return False
        now = current_time if current_time is not None else time.time()
        return (now - self.requested_at) > self.timeout_seconds

    def check_and_update_expiry(self, current_time: Optional[float] = None) -> bool:
        """Update state to EXPIRED if timeout exceeded."""
        if self.is_expired(current_time):
            self.state = ApprovalState.EXPIRED
            self.decided_at = current_time if current_time is not None else time.time()
            self.decision_reason = f"Approval timed out after {self.timeout_seconds}s"
            return True
        return False

    def approve(self, approver: str, mode: str, current_time: Optional[float] = None) -> Tuple[bool, Optional[str]]:
        """Transition request to APPROVED.

        Enforces constraint: L3 cannot be approved by voice alone.
        Enforces constraint: L4 can never be approved.
        """
        now = current_time if current_time is not None else time.time()

        if self.check_and_update_expiry(now):
            return False, "Cannot approve expired request."

        if self.state != ApprovalState.PENDING:
            return False, f"Cannot approve request in '{self.state.value}' state."

        # Hard constraint: L4 never allowed
        if self.tier == "L4":
            self.state = ApprovalState.DENIED
            self.decided_at = now
            self.decision_reason = "Hardcoded Rule F6: L4 capability is strictly prohibited."
            return False, "Rule F6 violation: L4 operations can never be approved."

        # Hard constraint: L3 hazardous explicit approval cannot be approved by voice alone
        if self.tier == "L3" and mode.lower() in {"voice", "user_voice"}:
            return False, "Hazardous L3 capability requires explicit interactive approval with preview; voice alone is prohibited."

        self.state = ApprovalState.APPROVED
        self.approver = approver
        self.approval_mode = mode
        self.decided_at = now
        self.decision_reason = f"Approved by {approver} via {mode}"
        return True, None

    def deny(self, denier: str, reason: str, current_time: Optional[float] = None) -> Tuple[bool, Optional[str]]:
        """Transition request to DENIED."""
        now = current_time if current_time is not None else time.time()

        if self.state != ApprovalState.PENDING:
            return False, f"Cannot deny request in '{self.state.value}' state."

        self.state = ApprovalState.DENIED
        self.approver = denier
        self.decided_at = now
        self.decision_reason = reason
        return True, None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "intent_id": self.intent_id,
            "capability": self.capability,
            "tier": self.tier,
            "params": self.params,
            "preview": self.preview,
            "state": self.state.value,
            "requested_at": self.requested_at,
            "decided_at": self.decided_at,
            "approver": self.approver,
            "approval_mode": self.approval_mode,
            "decision_reason": self.decision_reason,
        }
