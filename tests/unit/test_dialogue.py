"""Unit and golden-transcript tests for Lazy OS Dialogue Manager."""
from __future__ import annotations

import pytest

from lazy.dialogue.corrections import CorrectionEngine
from lazy.dialogue.manager import DialogueManager
from lazy.planner.mock import MockPlanner


class TestCorrectionEngine:
    @pytest.fixture
    def engine(self):
        return CorrectionEngine()

    def test_path_substitution(self, engine: CorrectionEngine):
        current_params = {"path": "/home/user/old.txt"}
        matched, rule_id, new_params = engine.match_and_apply("no, use /tmp/new.txt instead", current_params)
        assert matched is True
        assert rule_id == "corr-path-substitute"
        assert new_params["path"] == "/tmp/new.txt"

    def test_brightness_override(self, engine: CorrectionEngine):
        current_params = {"brightness": 50}
        matched, rule_id, new_params = engine.match_and_apply("no, make it 80 percent", current_params)
        assert matched is True
        assert rule_id == "corr-brightness-override"
        assert new_params["brightness"] == 80
        assert isinstance(new_params["brightness"], int)

    def test_volume_override(self, engine: CorrectionEngine):
        current_params = {"volume": 20}
        matched, rule_id, new_params = engine.match_and_apply("make volume 65", current_params)
        assert matched is True
        assert rule_id == "corr-volume-override"
        assert new_params["volume"] == 65
        assert isinstance(new_params["volume"], int)

    def test_service_override(self, engine: CorrectionEngine):
        current_params = {"service": "lazy-gateway"}
        matched, rule_id, new_params = engine.match_and_apply("no, restart lazy-policy instead", current_params)
        assert matched is True
        assert rule_id == "corr-service-override"
        assert new_params["service"] == "lazy-policy"

    def test_unmatched_text(self, engine: CorrectionEngine):
        current_params = {"path": "/test.txt"}
        matched, rule_id, new_params = engine.match_and_apply("completely unrelated statement", current_params)
        assert matched is False
        assert rule_id is None
        assert new_params == current_params


class TestDialogueManager:
    @pytest.fixture
    def dm(self):
        return DialogueManager()

    def test_plan_view_generation(self, dm: DialogueManager):
        turn = dm.process_input("read file notes.txt")
        assert turn["type"] == "plan_view"
        assert "plan" in turn
        assert len(turn["plan"]["steps"]) == 1
        assert "Plan with 1 steps created" in turn["narration"]

    def test_clarifying_question_and_option_selection(self, dm: DialogueManager):
        # 1. Ambiguous query triggers clarification
        turn1 = dm.process_input("read notes")
        assert turn1["type"] == "clarification"
        assert "Multiple notes files found" in turn1["question"]
        assert len(turn1["options"]) == 3

        # 2. User chooses option 1
        turn2 = dm.process_input("1")
        assert turn2["type"] == "plan_view"
        assert turn2["plan"]["steps"][0]["params"]["path"] == "~/Documents/notes.txt"
        assert dm.pending_clarification is None

    def test_control_commands_pause_resume_stop(self, dm: DialogueManager):
        dm.process_input("set screen brightness to 75 percent")
        assert dm.active_plan is not None

        # Pause
        p_turn = dm.process_input("pause")
        assert p_turn["type"] == "control"
        assert p_turn["command"] == "pause"
        assert dm.is_paused is True

        # Resume
        r_turn = dm.process_input("resume")
        assert r_turn["type"] == "control"
        assert r_turn["command"] == "resume"
        assert dm.is_paused is False

        # Stop
        s_turn = dm.process_input("stop")
        assert s_turn["type"] == "control"
        assert s_turn["command"] == "stop"
        assert dm.active_plan is None

    def test_control_command_undo(self, dm: DialogueManager):
        u_turn = dm.process_input("undo that")
        assert u_turn["type"] == "control"
        assert u_turn["command"] == "undo"
        assert u_turn["capability"] == "task.undo"

    def test_quiet_mode_toggle_and_narration_suppression(self, dm: DialogueManager):
        # Default: quiet mode is False
        assert dm.quiet_mode is False
        narr = dm.narrate_step(0, 1, {"capability": "fs.read", "params": {"path": "/etc/issue"}})
        assert narr is not None
        assert "Step 1 of 1: Executing fs.read" in narr

        # Enable quiet mode
        q_turn = dm.process_input("quiet mode on")
        assert q_turn["type"] == "system"
        assert dm.quiet_mode is True

        # Narration is suppressed in quiet mode
        narr_quiet = dm.narrate_step(0, 1, {"capability": "fs.read", "params": {"path": "/etc/issue"}})
        assert narr_quiet is None

        # Plan view narration is also blanked
        plan_turn = dm.process_input("read file notes.txt")
        assert plan_turn["type"] == "plan_view"
        assert plan_turn["narration"] == ""

        # Disable quiet mode
        dm.process_input("quiet mode off")
        assert dm.quiet_mode is False

    def test_correction_rule_application(self, dm: DialogueManager):
        # First turn: plan creation
        dm.process_input("set screen brightness to 75 percent")
        assert dm.active_plan["steps"][0]["params"]["brightness"] == 80

        # Second turn: user corrects
        corr_turn = dm.process_input("no, make it 40 percent")
        assert corr_turn["type"] == "correction_applied"
        assert corr_turn["rule_id"] == "corr-brightness-override"
        assert dm.active_plan["steps"][0]["params"]["brightness"] == 40


class TestGoldenTranscripts:
    """End-to-end multi-turn golden transcripts verifying interactive OS agent behavior."""

    def test_golden_clarification_flow(self):
        dm = DialogueManager()
        # Step 1: User says ambiguous query
        t1 = dm.process_input("delete notes")
        assert t1["type"] == "clarification"
        assert len(t1["options"]) == 3

        # Step 2: User selects option 2
        t2 = dm.process_input("2")
        assert t2["type"] == "plan_view"
        assert t2["plan"]["steps"][0]["capability"] == "fs.delete"
        assert t2["plan"]["steps"][0]["params"]["path"] == "~/Desktop/notes.txt"

    def test_golden_midflight_correction_flow(self):
        dm = DialogueManager()
        # Step 1: User requests service restart
        t1 = dm.process_input("restart lazy-policy service")
        assert t1["type"] == "plan_view"
        assert t1["plan"]["steps"][0]["params"]["service"] == "lazy-policy"

        # Step 2: User corrects
        t2 = dm.process_input("no, restart lazy-gateway instead")
        assert t2["type"] == "correction_applied"
        assert t2["plan"]["steps"][0]["params"]["service"] == "lazy-gateway"

    def test_golden_pause_and_cancel_flow(self):
        dm = DialogueManager()
        # Step 1: User initiates code write
        t1 = dm.process_input("write data to file")
        assert t1["type"] == "plan_view"

        # Step 2: User pauses
        t2 = dm.process_input("wait")
        assert t2["type"] == "control"
        assert t2["command"] == "pause"

        # Step 3: User cancels
        t3 = dm.process_input("cancel")
        assert t3["type"] == "control"
        assert t3["command"] == "stop"
        assert dm.active_plan is None
