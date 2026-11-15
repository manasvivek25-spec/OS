"""Dialogue Manager for Lazy OS: conversational control, clarifications, plan views, and narration."""
from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from lazy.dialogue.corrections import CorrectionEngine
from lazy.planner.base import PlannerInterface
from lazy.planner.mock import MockPlanner


class DialogueManager:
    """Manages dialogue state, clarifications, plan view events, and narration."""

    def __init__(
        self,
        planner: Optional[PlannerInterface] = None,
        correction_engine: Optional[CorrectionEngine] = None,
        quiet_mode: bool = False,
    ):
        self.planner = planner or MockPlanner()
        self.correction_engine = correction_engine or CorrectionEngine()
        self.quiet_mode = quiet_mode

        self.active_plan: Optional[Dict[str, Any]] = None
        self.active_step_index: int = 0
        self.is_paused: bool = False
        self.pending_clarification: Optional[Dict[str, Any]] = None
        self.history: List[Dict[str, Any]] = []

    def set_quiet_mode(self, enabled: bool) -> None:
        """Toggle quiet mode on or off."""
        self.quiet_mode = enabled

    def narrate_step(self, step_idx: int, total_steps: int, intent: Dict[str, Any]) -> Optional[str]:
        """Produce conversational step narration string (suppressed in quiet mode)."""
        if self.quiet_mode:
            return None

        cap = intent.get("capability", "task")
        params = intent.get("params", {})
        param_desc = ""
        if "path" in params:
            param_desc = f" on {params['path']}"
        elif "service" in params:
            param_desc = f" for {params['service']}"
        elif "volume" in params:
            param_desc = f" to {params['volume']}%"
        elif "brightness" in params:
            param_desc = f" to {params['brightness']}%"
        elif "url" in params:
            param_desc = f" {params['url']}"

        return f"Step {step_idx + 1} of {total_steps}: Executing {cap}{param_desc}."

    def process_input(self, text: str, requester: str = "text") -> Dict[str, Any]:
        """Process conversational user input through dialogue manager state machine."""
        clean_text = text.strip()
        lower_text = clean_text.lower()
        self.history.append({"speaker": "user", "text": clean_text})

        # 1. Quiet mode toggles
        if lower_text in ["quiet mode on", "enable quiet mode", "quiet on", "mute narration"]:
            self.set_quiet_mode(True)
            turn = {"type": "system", "message": "Quiet mode enabled. Narration suppressed."}
            self.history.append({"speaker": "lazy", "turn": turn})
            return turn

        if lower_text in ["quiet mode off", "disable quiet mode", "quiet off", "unmute narration"]:
            self.set_quiet_mode(False)
            turn = {"type": "system", "message": "Quiet mode disabled. Narration active."}
            self.history.append({"speaker": "lazy", "turn": turn})
            return turn

        # 2. Mid-flight control commands (pause, resume, stop, undo)
        if lower_text in ["pause", "hold on", "wait"]:
            self.is_paused = True
            turn = {
                "type": "control",
                "command": "pause",
                "narration": "Task execution paused." if not self.quiet_mode else "",
            }
            self.history.append({"speaker": "lazy", "turn": turn})
            return turn

        if lower_text in ["resume", "continue"]:
            self.is_paused = False
            turn = {
                "type": "control",
                "command": "resume",
                "narration": "Resuming task execution." if not self.quiet_mode else "",
            }
            self.history.append({"speaker": "lazy", "turn": turn})
            return turn

        if lower_text in ["stop", "cancel", "abort"]:
            self.active_plan = None
            self.is_paused = False
            turn = {
                "type": "control",
                "command": "stop",
                "narration": "Task cancelled and rolled back." if not self.quiet_mode else "",
            }
            self.history.append({"speaker": "lazy", "turn": turn})
            return turn

        if lower_text in ["undo", "revert", "undo that", "rollback"]:
            turn = {
                "type": "control",
                "command": "undo",
                "capability": "task.undo",
                "narration": "Rolling back previous task snapshot." if not self.quiet_mode else "",
            }
            self.history.append({"speaker": "lazy", "turn": turn})
            return turn

        # 3. Handle pending clarification response
        if self.pending_clarification:
            options = self.pending_clarification["options"]
            selected_idx = None

            # Option selection by digit: 1, 2, ...
            if lower_text.isdigit():
                val = int(lower_text) - 1
                if 0 <= val < len(options):
                    selected_idx = val
            else:
                for idx, opt in enumerate(options):
                    if lower_text in opt.lower() or opt.lower() in lower_text:
                        selected_idx = idx
                        break

            if selected_idx is not None:
                chosen_option = options[selected_idx]
                context_cap = self.pending_clarification.get("context_capability", "fs.read")
                param_key = self.pending_clarification.get("param_key", "path")
                self.pending_clarification = None

                # Clean option text
                clean_val = re.sub(r"^\d+\.\s*", "", chosen_option)
                intent = self.planner.propose_intent(context_cap, {param_key: clean_val}, requester=requester)
                plan = self.planner.create_plan([intent], f"Execute {context_cap} for {clean_val}")
                self.active_plan = plan
                turn = {
                    "type": "plan_view",
                    "plan": plan,
                    "narration": f"Selected option {selected_idx + 1}. Executing {clean_val}." if not self.quiet_mode else "",
                }
                self.history.append({"speaker": "lazy", "turn": turn})
                return turn
            else:
                # Option not understood, repeat question
                turn = {
                    "type": "clarification",
                    "question": self.pending_clarification["question"],
                    "options": options,
                    "narration": "Please select a valid option from the list." if not self.quiet_mode else "",
                }
                self.history.append({"speaker": "lazy", "turn": turn})
                return turn

        # 4. Check for correction on active plan
        if self.active_plan and self.active_plan.get("steps"):
            curr_step = self.active_plan["steps"][self.active_step_index]
            matched, rule_id, new_params = self.correction_engine.match_and_apply(clean_text, curr_step.get("params", {}))
            if matched:
                curr_step["params"] = new_params
                turn = {
                    "type": "correction_applied",
                    "rule_id": rule_id,
                    "plan": self.active_plan,
                    "narration": f"Updated parameters: {new_params}." if not self.quiet_mode else "",
                }
                self.history.append({"speaker": "lazy", "turn": turn})
                return turn

        # 5. Check for ambiguous requests requiring clarification
        if lower_text in ["delete file", "delete notes", "read notes", "restart service"]:
            if "notes" in lower_text:
                options = ["1. ~/Documents/notes.txt", "2. ~/Desktop/notes.txt", "3. /tmp/notes.txt"]
                cap = "fs.delete" if "delete" in lower_text else "fs.read"
                self.pending_clarification = {
                    "question": f"Multiple notes files found. Which file would you like to {cap.split('.')[1]}?",
                    "options": options,
                    "context_capability": cap,
                    "param_key": "path",
                }
                turn = {
                    "type": "clarification",
                    "question": self.pending_clarification["question"],
                    "options": options,
                    "narration": "Multiple matching files found. Please choose an option." if not self.quiet_mode else "",
                }
                self.history.append({"speaker": "lazy", "turn": turn})
                return turn
            elif "service" in lower_text:
                options = ["1. lazy-gateway", "2. lazy-policy", "3. lazy-tasks"]
                self.pending_clarification = {
                    "question": "Which service do you want to restart?",
                    "options": options,
                    "context_capability": "sys.service_restart",
                    "param_key": "service",
                }
                turn = {
                    "type": "clarification",
                    "question": self.pending_clarification["question"],
                    "options": options,
                    "narration": "Which service should I restart?" if not self.quiet_mode else "",
                }
                self.history.append({"speaker": "lazy", "turn": turn})
                return turn

        # 6. Normal input planning
        try:
            plan = self.planner.plan(clean_text, requester=requester)
            self.active_plan = plan
            self.active_step_index = 0
            steps_count = len(plan.get("steps", []))
            rationale = plan.get("rationale", "")
            turn = {
                "type": "plan_view",
                "plan": plan,
                "narration": f"Plan with {steps_count} steps created: {rationale}." if not self.quiet_mode else "",
            }
            self.history.append({"speaker": "lazy", "turn": turn})
            return turn
        except ValueError as err:
            turn = {
                "type": "error",
                "message": str(err),
                "narration": "I did not understand the request." if not self.quiet_mode else "",
            }
            self.history.append({"speaker": "lazy", "turn": turn})
            return turn
