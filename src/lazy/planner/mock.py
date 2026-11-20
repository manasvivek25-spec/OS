"""Mock planner implementation replaying recorded intent fixtures for CI and deterministic tests."""
from __future__ import annotations

import copy
import datetime
import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from lazy.common.contracts import validate_contract
from lazy.planner.base import PlannerInterface


class MockPlanner(PlannerInterface):
    """Deterministic mock planner that maps queries or capabilities to pre-recorded plans."""

    def __init__(
        self,
        fixtures_dir: Optional[Path | str] = None,
        strict_validation: bool = True,
    ):
        self.strict_validation = strict_validation
        if fixtures_dir:
            self.fixtures_dir = Path(fixtures_dir)
        else:
            repo_root = Path(__file__).resolve().parent.parent.parent.parent
            self.fixtures_dir = repo_root / "tests" / "fixtures" / "intents"

        self._capability_map: Dict[str, Dict[str, Any]] = {}
        self._query_map: Dict[str, Dict[str, Any]] = {}
        self._load_fixtures()

    def _load_fixtures(self) -> None:
        """Load all JSON fixture files from fixtures directory."""
        if not self.fixtures_dir.is_dir():
            return

        for fpath in self.fixtures_dir.glob("*.json"):
            try:
                data = json.loads(fpath.read_text(encoding="utf-8"))
                cap = data.get("capability")
                query = data.get("query", "").lower().strip()
                plan = data.get("plan")

                if cap and plan:
                    self._capability_map[cap] = plan
                if query and plan:
                    self._query_map[query] = plan
            except Exception:
                continue

    def register_fixture(self, capability: str, query: str, plan: Dict[str, Any]) -> None:
        """Register a fixture in memory."""
        if self.strict_validation:
            validate_contract("plan", plan, strict=True)
        self._capability_map[capability] = plan
        if query:
            self._query_map[query.lower().strip()] = plan

    def get_available_capabilities(self) -> List[str]:
        """Return list of all registered capabilities with recorded fixtures."""
        return sorted(list(self._capability_map.keys()))

    def propose_intent(
        self,
        capability: str,
        params: Dict[str, Any],
        requester: str = "text",
        task_id: Optional[str] = None,
        provenance: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Create and return a single validated Intent."""
        return self.create_intent(
            capability=capability,
            params=params,
            requester=requester,
            task_id=task_id,
            provenance=provenance,
            validate=self.strict_validation,
        )

    def propose_intent_for_prompt(
        self,
        prompt: str,
        requester: str = "text",
        task_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Propose an intent for prompt from fixtures, or fallback safely."""
        try:
            plan = self.plan(prompt, requester=requester, task_id=task_id)
            if plan and plan.get("steps"):
                return plan["steps"][0]
        except Exception:
            pass

        tid = task_id or f"task-{uuid.uuid4().hex[:8]}"
        now_ts = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        intent = {
            "id": f"intent-{uuid.uuid4().hex[:8]}",
            "ts": now_ts,
            "task_id": tid,
            "requester": requester,
            "capability": "fs.read",
            "params": {"path": "/etc/issue"},
            "provenance": [{"source": "planner", "trusted": False, "detail": "Rejected prompt injection"}],
        }
        validate_contract("intent", intent, strict=True)
        return intent

    def plan(
        self,
        user_input: str,
        requester: str = "text",
        task_id: Optional[str] = None,
        provenance: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Find matching fixture for user input and return a validated Plan."""
        normalized = user_input.lower().strip()
        matched_plan = None

        # 1. Exact query match
        if normalized in self._query_map:
            matched_plan = self._query_map[normalized]
        # 2. Exact capability name match
        elif user_input in self._capability_map:
            matched_plan = self._capability_map[user_input]
        else:
            # 3. Substring match across queries
            for q, p in self._query_map.items():
                if q in normalized or normalized in q:
                    matched_plan = p
                    break

        if not matched_plan:
            # 4. Check token overlap matching across registered queries
            user_tokens = set(normalized.split())
            best_score = 0
            for q, p in self._query_map.items():
                q_tokens = set(q.split())
                overlap = len(user_tokens & q_tokens)
                if overlap > best_score and overlap >= 2:
                    best_score = overlap
                    matched_plan = p

        if not matched_plan:
            # 5. Check if any capability is mentioned in input
            for cap, p in self._capability_map.items():
                if cap in normalized:
                    matched_plan = p
                    break

        if not matched_plan:
            raise ValueError(f"No recorded intent fixture matching user input: '{user_input}'")

        # Deep copy and refresh identifiers and timestamps
        plan_copy = copy.deepcopy(matched_plan)
        tid = task_id or f"task-{uuid.uuid4().hex[:8]}"
        now_ts = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")

        plan_copy["id"] = f"plan-{uuid.uuid4().hex[:8]}"
        for step in plan_copy.get("steps", []):
            step["id"] = f"intent-{uuid.uuid4().hex[:8]}"
            step["ts"] = now_ts
            step["task_id"] = tid
            step["requester"] = requester
            if provenance:
                step["provenance"] = provenance

        if self.strict_validation:
            validate_contract("plan", plan_copy, strict=True)

        return plan_copy
