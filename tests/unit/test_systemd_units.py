"""Unit tests for Lazy OS systemd service sandboxing units (Milestone M3.5).

Verifies:
- All 15 Lazy OS services and sandbox units are defined.
- Strict user separation (no root execution, dedicated unprivileged users).
- Filesystem isolation (ProtectSystem=strict, PrivateTmp=yes).
- Privilege escalation prevention (NoNewPrivileges=yes).
- Kernel and cgroup protection (ProtectKernelTunables, ProtectControlGroups).
- Network boundary isolation (AF_UNIX only for internal services).
- Resource constraints (MemoryMax, CPUWeight).
- Security audit scoring (SecurityAuditor).
- Transient sandbox command generation (systemd-run).
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import pytest

from lazy.systemd.parser import SystemdUnitParser, ServiceUnit
from lazy.systemd.security import SecurityAuditor, NETWORK_ALLOWED_SERVICES
from lazy.systemd.runner import build_systemd_run_cmd, SandboxedRunner

REQUIRED_SERVICES = [
    "lazy-gateway.service",
    "lazy-planner.service",
    "lazy-llm.service",
    "lazy-policy.service",
    "lazy-tasks.service",
    "lazy-broker-fs.service",
    "lazy-broker-sys.service",
    "lazy-broker-hw.service",
    "lazy-broker-web.service",
    "lazy-broker-comms.service",
    "lazy-secrets.service",
    "lazy-outbox.service",
    "lazy-fetcher.service",
    "lazy-routines.service",
    "lazy-audit.service",
]


@pytest.fixture
def systemd_dir() -> Path:
    repo_root = Path(__file__).resolve().parent.parent.parent
    return repo_root / "systemd"


@pytest.fixture
def all_units(systemd_dir: Path) -> dict[str, ServiceUnit]:
    units = SystemdUnitParser.parse_directory(systemd_dir)
    return units


class TestSystemdSandboxingUnits:
    def test_all_15_services_and_sandbox_units_exist(self, systemd_dir: Path, all_units: dict[str, ServiceUnit]):
        assert systemd_dir.is_dir()
        for svc in REQUIRED_SERVICES:
            assert svc in all_units, f"Missing systemd service unit: {svc}"

        # Check transient sandbox files
        assert (systemd_dir / "lazy-code-sandbox@.service").is_file()
        assert (systemd_dir / "lazy-code-sandbox.slice").is_file()

    def test_dedicated_unprivileged_users(self, all_units: dict[str, ServiceUnit]):
        users_seen = set()
        for svc in REQUIRED_SERVICES:
            unit = all_units[svc]
            user = unit.service.get("User")
            assert user is not None and len(user) > 0, f"{svc} must specify a User"
            assert user != "root", f"{svc} must not run as root"
            assert user.startswith("lazy-"), f"{svc} user '{user}' must start with 'lazy-'"
            users_seen.add(user)

        # Confirm distinct users across services
        assert len(users_seen) >= 12, "Services must use dedicated unprivileged users"

    def test_filesystem_and_privilege_sandboxing(self, all_units: dict[str, ServiceUnit]):
        for svc in REQUIRED_SERVICES:
            unit = all_units[svc]
            sec = unit.service

            # NoNewPrivileges
            assert sec.get("NoNewPrivileges", "").lower() in ("yes", "true", "1"), f"{svc} missing NoNewPrivileges=yes"

            # ProtectSystem=strict
            assert sec.get("ProtectSystem", "").lower() == "strict", f"{svc} missing ProtectSystem=strict"

            # PrivateTmp=yes
            assert sec.get("PrivateTmp", "").lower() in ("yes", "true", "1"), f"{svc} missing PrivateTmp=yes"

            # ProtectKernelTunables & ProtectControlGroups
            assert sec.get("ProtectKernelTunables", "").lower() in ("yes", "true", "1"), f"{svc} missing ProtectKernelTunables"
            assert sec.get("ProtectControlGroups", "").lower() in ("yes", "true", "1"), f"{svc} missing ProtectControlGroups"

    def test_network_isolation_rules(self, all_units: dict[str, ServiceUnit]):
        for svc in REQUIRED_SERVICES:
            unit = all_units[svc]
            raf = unit.service.get("RestrictAddressFamilies", "")

            if svc in NETWORK_ALLOWED_SERVICES:
                assert "AF_INET" in raf, f"{svc} is a network service and should support AF_INET"
            else:
                assert raf == "AF_UNIX", (
                    f"Security violation: unprivileged service {svc} must have RestrictAddressFamilies=AF_UNIX "
                    f"to prevent any network access! Found: {raf}"
                )

    def test_resource_limits_configured(self, all_units: dict[str, ServiceUnit]):
        for svc in REQUIRED_SERVICES:
            unit = all_units[svc]
            mem = unit.service.get("MemoryMax")
            cpu = unit.service.get("CPUWeight")
            assert mem is not None and len(mem) > 0, f"{svc} missing MemoryMax"
            assert cpu is not None and len(cpu) > 0, f"{svc} missing CPUWeight"

    def test_security_audit_full_score(self, all_units: dict[str, ServiceUnit]):
        auditor = SecurityAuditor()
        results = auditor.audit_all(all_units)

        for svc in REQUIRED_SERVICES:
            res = results[svc]
            assert res.passed is True, f"{svc} failed security audit: {res.violations}"
            assert res.score == 10.0, f"{svc} did not achieve 10.0/10.0 hardening score"

    def test_systemd_run_command_generation(self):
        cmd = build_systemd_run_cmd(
            command="python3 -c 'print(42)'",
            user="lazy-sandbox",
            slice_name="lazy-code-sandbox.slice",
            memory_max="128M",
            cpu_weight=40,
            timeout_sec=15,
        )

        cmd_str = " ".join(cmd)
        assert "systemd-run" in cmd[0]
        assert "--slice=lazy-code-sandbox.slice" in cmd
        assert "--property=User=lazy-sandbox" in cmd
        assert "--property=ProtectSystem=strict" in cmd
        assert "--property=PrivateTmp=yes" in cmd
        assert "--property=MemoryMax=128M" in cmd
        assert "--property=CPUWeight=40" in cmd
        assert "--property=RestrictAddressFamilies=AF_UNIX" in cmd
        assert "python3 -c 'print(42)'" in cmd[-1]

    def test_sandboxed_runner_execution_fallback(self):
        runner = SandboxedRunner()
        res = runner.run("echo 'sandbox test'")
        assert res["returncode"] == 0
        assert "sandbox test" in res["stdout"]

    def test_systemd_analyze_verify_host_syntax(self, systemd_dir: Path):
        analyze_path = shutil.which("systemd-analyze")
        if not analyze_path:
            pytest.skip("systemd-analyze not installed on host")

        # Verify unit files syntax using systemd-analyze
        service_files = [str(f) for f in systemd_dir.glob("*.service")]
        cmd = [analyze_path, "verify"] + service_files
        res = subprocess.run(cmd, capture_output=True, text=True)
        # Note: systemd-analyze verify may emit warnings for missing executables (/usr/bin/python3 -m ...),
        # but syntax parse errors cause fatal exits or specific parse error messages.
        assert "Failed to parse" not in res.stderr
        assert "Syntax error" not in res.stderr
