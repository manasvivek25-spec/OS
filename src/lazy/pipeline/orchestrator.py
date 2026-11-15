"""Pipeline orchestrator executing end-to-end Lazy OS pipeline across dialogue, policy, staging, brokers, and audit."""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from lazy.audit.ledger import AuditLedger
from lazy.brokers.fs_broker import FSBroker
from lazy.brokers.hw_broker import HWBroker
from lazy.brokers.sys_broker import FakeSystemdClient, SysBroker
from lazy.dialogue.manager import DialogueManager
from lazy.planner.base import PlannerInterface
from lazy.planner.mock import MockPlanner
from lazy.policy.engine import PolicyEngine
from lazy.policy.manifest import ManifestLoader
from lazy.tasks.manager import TaskManager


@dataclass
class PipelineResult:
    task_id: str
    status: str  # "completed", "denied", "cancelled", "failed"
    query: str
    plan: Optional[Dict[str, Any]] = None
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    step_results: List[Dict[str, Any]] = field(default_factory=list)
    narration: List[str] = field(default_factory=list)
    latency_ms: float = 0.0
    error: Optional[str] = None


class PipelineOrchestrator:
    """End-to-end pipeline connecting input, planner, policy, staging, brokers, and audit."""

    def __init__(
        self,
        workspace_dir: Optional[Path | str] = None,
        audit_path: Optional[Path | str] = None,
        policy_dir: Optional[Path | str] = None,
        planner: Optional[PlannerInterface] = None,
        dialogue_manager: Optional[DialogueManager] = None,
        sysfs_root: Optional[Path | str] = None,
    ):
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
        self.workspace_dir = Path(workspace_dir) if workspace_dir else repo_root / "tests" / "fixtures" / "workspace"
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        self.audit_path = Path(audit_path) if audit_path else repo_root / "tests" / "results" / "pipeline_audit.log"
        self.audit = AuditLedger(self.audit_path)

        if policy_dir:
            loader = ManifestLoader(manifests_dir=policy_dir)
            self.policy = PolicyEngine(manifest_loader=loader)
        else:
            self.policy = PolicyEngine()

        self.task_manager = TaskManager(target_dir=self.workspace_dir)

        self.planner = planner or MockPlanner()
        self.dialogue = dialogue_manager or DialogueManager(planner=self.planner)

        # Initialize brokers
        self.fs_broker = FSBroker(root_dir=self.workspace_dir)
        self.sys_broker = SysBroker(client=FakeSystemdClient())
        self.hw_broker = HWBroker(sysfs_root=sysfs_root)

        self.last_completed_task_id: Optional[str] = None

    def execute_text(
        self,
        query: str,
        requester: str = "text",
        auto_approve: bool = True,
        approval_callback: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> PipelineResult:
        """Run full end-to-end pipeline execution from text query."""
        start_time = time.perf_counter()
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        narration_log: List[str] = []

        # 1. Dialogue / Planning phase
        turn = self.dialogue.process_input(query, requester=requester)
        if turn.get("type") == "control":
            cmd = turn.get("command")
            if cmd == "undo":
                if self.last_completed_task_id:
                    self.task_manager.undo_task(self.last_completed_task_id)
                    undo_ok = True
                else:
                    undo_ok = False
                elapsed = (time.perf_counter() - start_time) * 1000.0
                return PipelineResult(
                    task_id=task_id,
                    status="completed" if undo_ok else "failed",
                    query=query,
                    narration=[turn.get("narration", "")],
                    latency_ms=elapsed,
                )
            elapsed = (time.perf_counter() - start_time) * 1000.0
            return PipelineResult(
                task_id=task_id,
                status="cancelled",
                query=query,
                narration=[turn.get("narration", "")],
                latency_ms=elapsed,
            )

        if turn.get("type") != "plan_view" or not turn.get("plan"):
            elapsed = (time.perf_counter() - start_time) * 1000.0
            return PipelineResult(
                task_id=task_id,
                status="failed",
                query=query,
                error=turn.get("message", "Could not generate plan"),
                latency_ms=elapsed,
            )

        plan = turn["plan"]
        steps = plan.get("steps", [])
        if turn.get("narration"):
            narration_log.append(turn["narration"])

        # Audit plan creation
        self.audit.append("plan_created", "lazy-planner", {"task_id": task_id, "plan_id": plan.get("id"), "steps_count": len(steps)})

        # 2. Task lifecycle initialization
        self.task_manager.create_task(task_id=task_id)

        decisions_log: List[Dict[str, Any]] = []
        results_log: List[Dict[str, Any]] = []

        # 3. Step execution loop
        for idx, intent in enumerate(steps):
            # Narrate step progress
            narr = self.dialogue.narrate_step(idx, len(steps), intent)
            if narr:
                narration_log.append(narr)

            # Step A: Policy evaluation
            decision = self.policy.evaluate_intent(intent)
            decisions_log.append(decision)
            self.audit.append("policy_decision", "lazy-policy", decision)

            verdict = decision.get("verdict")
            tier = decision.get("tier")

            if verdict == "deny":
                self.task_manager.cancel_task(task_id)
                self.audit.append("task_denied", "lazy-policy", {"task_id": task_id, "reason": decision.get("reason")})
                elapsed = (time.perf_counter() - start_time) * 1000.0
                return PipelineResult(
                    task_id=task_id,
                    status="denied",
                    query=query,
                    plan=plan,
                    decisions=decisions_log,
                    narration=narration_log,
                    latency_ms=elapsed,
                    error=decision.get("reason"),
                )

            # Step B: Approval check for L2 and L3
            if verdict == "ask":
                # Strict Rule: Voice requester cannot approve L3 actions!
                if tier == "L3" and requester == "voice":
                    self.task_manager.cancel_task(task_id)
                    reason = "Rule F6 violation: Tier L3 hazardous actions cannot be approved by voice alone."
                    elapsed = (time.perf_counter() - start_time) * 1000.0
                    return PipelineResult(
                        task_id=task_id,
                        status="denied",
                        query=query,
                        plan=plan,
                        decisions=decisions_log,
                        narration=narration_log,
                        latency_ms=elapsed,
                        error=reason,
                    )

                approved = False
                if approval_callback:
                    approved = approval_callback(decision)
                elif auto_approve:
                    approved = True

                if not approved:
                    self.task_manager.cancel_task(task_id)
                    elapsed = (time.perf_counter() - start_time) * 1000.0
                    return PipelineResult(
                        task_id=task_id,
                        status="cancelled",
                        query=query,
                        plan=plan,
                        decisions=decisions_log,
                        narration=narration_log,
                        latency_ms=elapsed,
                        error="User declined approval",
                    )

            # Step C: Staging & Checkpoint
            intent_id = intent.get("id", f"intent-{idx}")
            ckpt_id = self.task_manager.checkpoint_before_step(task_id=task_id, intent_id=intent_id, step_index=idx)
            self.audit.append("checkpoint_created", "lazy-tasks", {"task_id": task_id, "step_index": idx, "checkpoint_id": ckpt_id})

            # Step D: Broker execution
            cap = intent.get("capability", "")
            params = intent.get("params", {})
            try:
                res = self._dispatch_to_broker(cap, params)
                results_log.append({"capability": cap, "status": "success", "output": res})
                self.task_manager.finish_step(task_id=task_id, step_index=idx, result={"output": res})
                self.audit.append("step_executed", "lazy-broker", {"task_id": task_id, "step_index": idx, "capability": cap, "success": True})
            except Exception as broker_err:
                results_log.append({"capability": cap, "status": "error", "error": str(broker_err)})
                self.task_manager.cancel_task(task_id)
                self.audit.append("step_failed", "lazy-broker", {"task_id": task_id, "step_index": idx, "error": str(broker_err)})
                elapsed = (time.perf_counter() - start_time) * 1000.0
                return PipelineResult(
                    task_id=task_id,
                    status="failed",
                    query=query,
                    plan=plan,
                    decisions=decisions_log,
                    step_results=results_log,
                    narration=narration_log,
                    latency_ms=elapsed,
                    error=str(broker_err),
                )

        # 4. Commit task
        self.task_manager.commit_task(task_id)
        self.last_completed_task_id = task_id
        self.audit.append("task_completed", "lazy-pipeline", {"task_id": task_id, "steps_executed": len(steps)})
        elapsed = (time.perf_counter() - start_time) * 1000.0

        return PipelineResult(
            task_id=task_id,
            status="completed",
            query=query,
            plan=plan,
            decisions=decisions_log,
            step_results=results_log,
            narration=narration_log,
            latency_ms=elapsed,
        )

    def _dispatch_to_broker(self, capability: str, params: Dict[str, Any]) -> Any:
        """Route capability invocation to designated registered broker."""
        domain = capability.split(".")[0]
        if domain in ["fs", "doc", "code"]:
            return self.fs_broker.execute(capability, params)
        elif domain == "sys":
            return self.sys_broker.execute(capability, params)
        elif domain == "hw":
            return self.hw_broker.execute(capability, params)
        elif domain in ["mail", "chat", "outbox", "web", "task"]:
            # Stubs / simulated responses for host pipeline
            return {"status": "ok", "capability": capability, "params": params}
        else:
            raise ValueError(f"No broker registered for domain '{domain}' in capability '{capability}'")
