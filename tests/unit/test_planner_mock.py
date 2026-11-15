"""Unit tests for lazy-planner: interface, mock mode, and all 37 recorded intent fixtures."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import jsonschema

from lazy.common.contracts import ContractValidationError, validate_contract
from lazy.planner.base import PlannerInterface
from lazy.planner.mock import MockPlanner


class DummyPlanner(PlannerInterface):
    """Test implementation of PlannerInterface."""
    def plan(self, user_input, requester="text", task_id=None, provenance=None):
        step = self.create_intent("fs.read", {"path": "/tmp/test.txt"}, requester=requester, task_id=task_id, provenance=provenance)
        return self.create_plan([step], "Test plan")

    def propose_intent(self, capability, params, requester="text", task_id=None, provenance=None):
        return self.create_intent(capability, params, requester=requester, task_id=task_id, provenance=provenance)


class TestPlannerInterface:
    def test_factory_methods(self):
        planner = DummyPlanner()
        intent = planner.propose_intent("fs.read", {"path": "/etc/issue"})
        assert intent["capability"] == "fs.read"
        assert intent["requester"] == "text"
        assert intent["params"]["path"] == "/etc/issue"
        assert len(intent["provenance"]) >= 1

        is_valid, _ = validate_contract("intent", intent)
        assert is_valid is True

        plan = planner.plan("dummy input")
        assert len(plan["steps"]) == 1
        assert plan["rationale"] == "Test plan"

        is_valid, _ = validate_contract("plan", plan)
        assert is_valid is True

    def test_invalid_intent_rejected(self):
        with pytest.raises(ContractValidationError):
            PlannerInterface.create_intent("invalid_cap_without_dot", {})

    def test_invalid_plan_rejected(self):
        with pytest.raises(ContractValidationError):
            PlannerInterface.create_plan([{"bad": "intent"}], "bad plan")


class TestMockPlanner:
    @pytest.fixture
    def planner(self):
        return MockPlanner()

    def test_all_37_capabilities_loaded(self, planner: MockPlanner):
        caps = planner.get_available_capabilities()
        assert len(caps) == 37
        expected_sample = ["fs.read", "fs.write", "hw.backlight_set", "mail.send", "web.navigate", "task.undo"]
        for exp in expected_sample:
            assert exp in caps

    def test_query_matching(self, planner: MockPlanner):
        plan = planner.plan("read file notes.txt")
        assert len(plan["steps"]) == 1
        assert plan["steps"][0]["capability"] == "fs.read"
        assert plan["steps"][0]["params"]["path"] == "/home/user/notes.txt"
        is_valid, _ = validate_contract("plan", plan)
        assert is_valid is True

    def test_capability_name_matching(self, planner: MockPlanner):
        plan = planner.plan("hw.backlight_set")
        assert len(plan["steps"]) == 1
        assert plan["steps"][0]["capability"] == "hw.backlight_set"
        assert plan["steps"][0]["params"]["brightness"] == 80
        is_valid, _ = validate_contract("plan", plan)
        assert is_valid is True

    def test_requester_and_task_id_propagation(self, planner: MockPlanner):
        plan = planner.plan("set volume to 50", requester="voice", task_id="task-custom-99")
        assert len(plan["steps"]) == 1
        step = plan["steps"][0]
        assert step["requester"] == "voice"
        assert step["task_id"] == "task-custom-99"

    def test_custom_provenance_propagation(self, planner: MockPlanner):
        custom_prov = [{"source": "voice_stt", "trusted": True, "detail": "confidence 0.98"}]
        plan = planner.plan("list files in home directory", provenance=custom_prov)
        step = plan["steps"][0]
        assert step["provenance"] == custom_prov

    def test_unknown_query_raises(self, planner: MockPlanner):
        with pytest.raises(ValueError, match="No recorded intent fixture matching"):
            planner.plan("unrecognized non-existent request 999xyz")

    def test_dynamic_register_fixture(self, planner: MockPlanner):
        step = PlannerInterface.create_intent("sys.process_list", {})
        custom_plan = PlannerInterface.create_plan([step], "Custom process list plan")

        planner.register_fixture("sys.custom_list", "show all active processes now", custom_plan)
        res = planner.plan("show all active processes now")
        assert res["rationale"] == "Custom process list plan"

    @pytest.mark.parametrize("cap_name", [
        "chat.read", "chat.send", "code.run", "code.write", "doc.create_docx", "doc.create_markdown",
        "fs.copy", "fs.delete", "fs.list", "fs.move", "fs.read", "fs.write",
        "hw.backlight_set", "hw.governor_set", "hw.power_profile_set", "hw.rfkill_set",
        "hw.usb_authorize", "hw.usb_list", "hw.volume_set",
        "mail.draft", "mail.list", "mail.read", "mail.send", "outbox.cancel",
        "sys.logs_read", "sys.process_list", "sys.process_signal", "sys.service_restart",
        "sys.service_status", "sys.setting_set", "task.undo",
        "web.click", "web.download", "web.fill", "web.navigate", "web.read", "web.submit"
    ])
    def test_every_capability_can_plan(self, planner: MockPlanner, cap_name: str):
        """Negative and positive check: every single capability in Lazy OS has an active, valid fixture."""
        plan = planner.plan(cap_name)
        assert len(plan["steps"]) >= 1
        assert plan["steps"][0]["capability"] == cap_name
        is_valid, err = validate_contract("plan", plan)
        assert is_valid is True, f"Plan validation failed for {cap_name}: {err}"
