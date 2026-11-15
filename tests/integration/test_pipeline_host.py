"""Integration tests for Lazy OS end-to-end host text pipeline."""
from __future__ import annotations

from pathlib import Path
import pytest

from lazy.audit.verifier import verify_audit_log
from lazy.pipeline.orchestrator import PipelineOrchestrator


@pytest.fixture
def test_pipeline(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    audit_file = tmp_path / "pipeline_audit.log"

    # Use sysfs fixture
    repo_root = Path(__file__).resolve().parent.parent.parent
    sysfs_root = repo_root / "tests" / "fixtures" / "sysfs"

    orchestrator = PipelineOrchestrator(
        workspace_dir=workspace,
        audit_path=audit_file,
        sysfs_root=sysfs_root,
    )
    return orchestrator, workspace, audit_file


class TestPipelineHostIntegration:
    def test_l0_read_execution(self, test_pipeline):
        orchestrator, workspace, audit_file = test_pipeline
        test_file = workspace / "notes.txt"
        test_file.write_text("Secret notes line 1\nLine 2\n", encoding="utf-8")

        res = orchestrator.execute_text("read file notes.txt")
        assert res.status == "completed"
        assert len(res.step_results) == 1
        assert res.step_results[0]["status"] == "success"
        assert "Secret notes" in str(res.step_results[0]["output"])

    def test_l1_write_with_snapshot_and_audit(self, test_pipeline):
        orchestrator, workspace, audit_file = test_pipeline
        res = orchestrator.execute_text("write data to file")
        assert res.status == "completed"
        assert len(res.decisions) == 1
        assert res.decisions[0]["tier"] == "L1"

        # Verify audit ledger integrity
        v_res = verify_audit_log(audit_file)
        assert v_res.is_valid is True, f"Audit hash chain broken: {v_res.reason}"

    def test_l2_approval_denial(self, test_pipeline):
        orchestrator, workspace, audit_file = test_pipeline
        # Create file to delete
        (workspace / "temp.txt").write_text("delete me", encoding="utf-8")

        # Refuse approval
        res = orchestrator.execute_text("delete temporary file", auto_approve=False)
        assert res.status == "cancelled"
        assert res.error == "User declined approval"

        # File should NOT be deleted
        assert (workspace / "temp.txt").exists()

    def test_l2_approval_granted(self, test_pipeline):
        orchestrator, workspace, audit_file = test_pipeline
        (workspace / "temp.txt").write_text("delete me", encoding="utf-8")

        res = orchestrator.execute_text("delete temporary file", auto_approve=True)
        assert res.status == "completed"
        assert not (workspace / "temp.txt").exists()

    def test_l3_voice_approval_rejection_rule_f6(self, test_pipeline):
        orchestrator, workspace, audit_file = test_pipeline
        # sys.process_signal is L3
        res = orchestrator.execute_text("terminate process 4321", requester="voice", auto_approve=True)
        assert res.status == "denied"
        assert "Rule F6 violation" in res.error

    def test_l3_text_approval_success(self, test_pipeline):
        orchestrator, workspace, audit_file = test_pipeline
        res = orchestrator.execute_text("terminate process 4321", requester="text", auto_approve=True)
        assert res.status == "completed"

    def test_undo_restores_pretask_state(self, test_pipeline):
        orchestrator, workspace, audit_file = test_pipeline
        initial_file = workspace / "preserve.txt"
        initial_file.write_text("Original content", encoding="utf-8")

        # Execute task that creates a new file
        res = orchestrator.execute_text("write data to file")
        assert res.status == "completed"
        created_file = workspace / "output.txt"
        assert created_file.exists()

        # Execute undo
        undo_res = orchestrator.execute_text("undo that")
        assert undo_res.status == "completed"

        # Output file should be removed and original preserved
        assert not created_file.exists()
        assert initial_file.read_text(encoding="utf-8") == "Original content"

    def test_full_pipeline_audit_integrity(self, test_pipeline):
        orchestrator, workspace, audit_file = test_pipeline
        orchestrator.execute_text("list files in home directory")
        orchestrator.execute_text("write data to file")
        orchestrator.execute_text("set display brightness to 80")

        v_res = verify_audit_log(audit_file)
        assert v_res.is_valid is True, f"Tamper detected in audit chain: {v_res.reason}"
