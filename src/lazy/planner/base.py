"""Base planner interface and contract factories for Lazy OS."""
from __future__ import annotations

import datetime
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from lazy.common.contracts import validate_contract


class PlannerInterface(ABC):
    """Abstract interface defining Lazy OS dialogue planner clients."""

    @abstractmethod
    def plan(
        self,
        user_input: str,
        requester: str = "text",
        task_id: Optional[str] = None,
        provenance: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Generate a validated Plan object from user input."""
        pass

    @abstractmethod
    def propose_intent(
        self,
        capability: str,
        params: Dict[str, Any],
        requester: str = "text",
        task_id: Optional[str] = None,
        provenance: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Propose a single typed and validated Intent object."""
        pass

    @staticmethod
    def create_intent(
        capability: str,
        params: Dict[str, Any],
        requester: str = "text",
        task_id: Optional[str] = None,
        intent_id: Optional[str] = None,
        provenance: Optional[List[Dict[str, Any]]] = None,
        validate: bool = True,
    ) -> Dict[str, Any]:
        """Factory for creating an Intent contract dictionary."""
        intent = {
            "id": intent_id or f"intent-{uuid.uuid4().hex[:8]}",
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
            "task_id": task_id or f"task-{uuid.uuid4().hex[:8]}",
            "requester": requester,
            "capability": capability,
            "params": params,
            "provenance": provenance
            or [
                {
                    "source": "user",
                    "trusted": True,
                    "detail": "Direct user request",
                }
            ],
        }
        if validate:
            validate_contract("intent", intent, strict=True)
        return intent

    @staticmethod
    def create_plan(
        steps: List[Dict[str, Any]],
        rationale: str,
        plan_id: Optional[str] = None,
        validate: bool = True,
    ) -> Dict[str, Any]:
        """Factory for creating a Plan contract dictionary."""
        plan = {
            "id": plan_id or f"plan-{uuid.uuid4().hex[:8]}",
            "steps": steps,
            "rationale": rationale,
        }
        if validate:
            validate_contract("plan", plan, strict=True)
        return plan
