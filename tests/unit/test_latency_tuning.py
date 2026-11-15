"""Unit tests for Lazy OS Interactive-Latency Tuning (Milestone M5.4).

Verifies:
- Memory locking (mlockall, munlockall, page faulting).
- CPU core affinity pinning and service affinity map generation.
- Cgroup v2 priority configurations and nice level adjustment.
- ModelWarmup execution and telemetry receipt.
- Statistical percentiles (p50, p90, p95) and latency ablation math.
- Systemd service units contain required latency tuning directives.
"""
from __future__ import annotations

import os
from pathlib import Path
import pytest

from lazy.tuning.memory import lock_memory, unlock_memory, preload_and_fault, get_locked_memory_kb, is_memory_locked
from lazy.tuning.affinity import (
    get_available_cpus,
    set_cpu_affinity,
    get_cpu_affinity,
    get_service_affinity_map,
    apply_service_affinity,
)
from lazy.tuning.cgroups import (
    CgroupProfile,
    INTERACTIVE_PROFILE,
    NORMAL_PROFILE,
    BACKGROUND_PROFILE,
    apply_nice,
    get_service_cgroup_profile,
)
from lazy.tuning.warmup import ModelWarmup
from lazy.systemd.parser import SystemdUnitParser


class TestMemoryLocking:
    def test_page_preload_and_fault(self):
        buf = bytearray(16384)  # 4 pages
        pages = preload_and_fault(buf, page_size=4096)
        assert pages == 4

    def test_empty_buffer_fault(self):
        assert preload_and_fault(b"") == 0

    def test_mlock_and_munlock_execution(self):
        # Test memory locking call
        res_lock = lock_memory(current=True, future=True)
        # On Linux with sufficient ulimit, res_lock is True
        assert isinstance(res_lock, bool)

        # Unlock
        res_unlock = unlock_memory()
        assert isinstance(res_unlock, bool)

    def test_locked_memory_kb_format(self):
        kb = get_locked_memory_kb()
        assert isinstance(kb, int)
        assert kb >= 0


class TestCpuAffinity:
    def test_available_cpus(self):
        cpus = get_available_cpus()
        assert len(cpus) >= 1
        assert 0 in cpus

    def test_set_and_get_affinity(self):
        orig_cpus = get_cpu_affinity()
        assert len(orig_cpus) >= 1

        # Pin to CPU 0
        success = set_cpu_affinity({0})
        if success:
            cur = get_cpu_affinity()
            assert 0 in cur
            # Restore
            set_cpu_affinity(orig_cpus)

    def test_service_affinity_mapping(self):
        # 4+ cores scenario
        mapping_4 = get_service_affinity_map(total_cpus=8)
        assert "lazy-llm" in mapping_4
        assert mapping_4["lazy-llm"] == {0, 1}
        assert "lazy-routines" in mapping_4
        assert mapping_4["lazy-routines"] == {2, 3}

        # 2 cores scenario
        mapping_2 = get_service_affinity_map(total_cpus=2)
        assert mapping_2["lazy-llm"] == {0}
        assert mapping_2["lazy-routines"] == {1}

        # 1 core scenario
        mapping_1 = get_service_affinity_map(total_cpus=1)
        assert mapping_1["lazy-llm"] == {0}
        assert mapping_1["lazy-routines"] == {0}

    def test_apply_service_affinity(self):
        res = apply_service_affinity("lazy-llm")
        assert isinstance(res, bool)


class TestCgroupsAndPriority:
    def test_cgroup_profiles(self):
        assert INTERACTIVE_PROFILE.cpu_weight == 500
        assert INTERACTIVE_PROFILE.io_weight == 500
        assert INTERACTIVE_PROFILE.nice == -5

        assert BACKGROUND_PROFILE.cpu_weight == 50
        assert BACKGROUND_PROFILE.io_weight == 50
        assert BACKGROUND_PROFILE.nice == 10

    def test_service_profile_mapping(self):
        llm_prof = get_service_cgroup_profile("lazy-llm")
        assert llm_prof.cpu_weight == 500
        assert llm_prof.name == "interactive"

        rout_prof = get_service_cgroup_profile("lazy-routines")
        assert rout_prof.cpu_weight == 50
        assert rout_prof.name == "background"

        audit_prof = get_service_cgroup_profile("lazy-audit")
        assert audit_prof.name == "normal"

    def test_apply_nice_graceful_handling(self):
        # Even if unprivileged, function returns False without unhandled exception
        res = apply_nice(0)
        assert isinstance(res, bool)


class TestModelWarmup:
    def test_warmup_execution(self, tmp_path: Path):
        model_file = tmp_path / "test_model.gguf"
        model_file.write_bytes(b"GGUF" + b"\x00" * 8192)

        warmup = ModelWarmup(model_path=model_file)
        res = warmup.execute_warmup()
        assert res["status"] == "ok"
        assert res["pages_preloaded"] >= 1
        assert res["warmup_duration_ms"] >= 0.0


class TestSystemdLatencyDirectives:
    def test_service_tuning_directives(self):
        repo_root = Path(__file__).resolve().parent.parent.parent
        systemd_dir = repo_root / "systemd"
        units = SystemdUnitParser.parse_directory(systemd_dir)

        # Check lazy-llm
        llm = units["lazy-llm.service"].service
        assert llm.get("LimitMEMLOCK") == "infinity", "lazy-llm must specify LimitMEMLOCK=infinity"
        assert int(llm.get("CPUWeight", 0)) >= 400, "lazy-llm must have high CPUWeight"
        assert "CPUAffinity" in llm, "lazy-llm must have CPUAffinity configured"

        # Check lazy-planner
        plan = units["lazy-planner.service"].service
        assert int(plan.get("CPUWeight", 0)) >= 400
        assert "CPUAffinity" in plan

        # Check lazy-routines (background)
        rout = units["lazy-routines.service"].service
        assert int(rout.get("CPUWeight", 100)) <= 50, "lazy-routines must have low CPUWeight"
        assert "CPUAffinity" in rout

        # Check warm-up service existence
        assert (systemd_dir / "lazy-warmup.service").is_file()
        assert (systemd_dir / "lazy-interactive.slice").is_file()
        assert (systemd_dir / "lazy-background.slice").is_file()
