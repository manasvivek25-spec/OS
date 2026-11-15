"""Security auditing and scoring for systemd service sandboxes."""
from __future__ import annotations

from dataclasses import dataclass, field
import logging
from typing import Any, Dict, List, Set

from lazy.systemd.parser import ServiceUnit

logger = logging.getLogger("lazy.systemd.security")

NETWORK_ALLOWED_SERVICES: Set[str] = {
    "lazy-gateway.service",
    "lazy-broker-web.service",
    "lazy-broker-comms.service",
    "lazy-fetcher.service",
}


@dataclass
class SecurityAuditResult:
    """Security audit assessment for a systemd service unit."""
    service_name: str
    user: str
    score: float  # 0.0 to 10.0
    passed: bool
    checks: Dict[str, bool] = field(default_factory=dict)
    violations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "service_name": self.service_name,
            "user": self.user,
            "score": round(self.score, 2),
            "passed": self.passed,
            "checks": self.checks,
            "violations": self.violations,
        }


class SecurityAuditor:
    """Audits systemd service sandboxing compliance against Lazy OS security requirements."""

    def audit_unit(self, unit: ServiceUnit) -> SecurityAuditResult:
        service_sec = unit.service
        violations: List[str] = []
        checks: Dict[str, bool] = {}

        # 1. Dedicated unprivileged user
        user = service_sec.get("User", "")
        if not user or user == "root":
            violations.append(f"Invalid user '{user}': services must run under dedicated unprivileged users")
            checks["user_isolation"] = False
        else:
            checks["user_isolation"] = True

        # 2. NoNewPrivileges
        nnp = service_sec.get("NoNewPrivileges", "").lower()
        if nnp in ("yes", "true", "1"):
            checks["no_new_privileges"] = True
        else:
            violations.append("NoNewPrivileges is not enabled")
            checks["no_new_privileges"] = False

        # 3. ProtectSystem=strict
        ps = service_sec.get("ProtectSystem", "").lower()
        if ps == "strict":
            checks["protect_system_strict"] = True
        else:
            violations.append(f"ProtectSystem must be 'strict' (found: '{ps}')")
            checks["protect_system_strict"] = False

        # 4. PrivateTmp
        ptmp = service_sec.get("PrivateTmp", "").lower()
        if ptmp in ("yes", "true", "1"):
            checks["private_tmp"] = True
        else:
            violations.append("PrivateTmp is not enabled")
            checks["private_tmp"] = False

        # 5. ProtectKernelTunables & ProtectControlGroups
        pkt = service_sec.get("ProtectKernelTunables", "").lower() in ("yes", "true", "1")
        pcg = service_sec.get("ProtectControlGroups", "").lower() in ("yes", "true", "1")
        if pkt and pcg:
            checks["protect_kernel_and_cgroups"] = True
        else:
            violations.append("ProtectKernelTunables and ProtectControlGroups must both be enabled")
            checks["protect_kernel_and_cgroups"] = False

        # 6. Network Restriction
        raf = service_sec.get("RestrictAddressFamilies", "")
        is_net_allowed = unit.name in NETWORK_ALLOWED_SERVICES
        if is_net_allowed:
            # Must still restrict to UNIX and INET
            if "AF_UNIX" in raf and "AF_INET" in raf:
                checks["network_restriction"] = True
            else:
                violations.append(f"Network service '{unit.name}' missing standard AF_UNIX/AF_INET restrictions")
                checks["network_restriction"] = False
        else:
            # Internal service must be strictly AF_UNIX
            if raf == "AF_UNIX":
                checks["network_restriction"] = True
            else:
                violations.append(f"Internal service '{unit.name}' must restrict address families strictly to AF_UNIX (found: '{raf}')")
                checks["network_restriction"] = False

        # 7. SystemCallFilter
        scf = service_sec.get("SystemCallFilter", "")
        if "@system-service" in scf:
            checks["syscall_filter"] = True
        else:
            violations.append("SystemCallFilter missing @system-service baseline")
            checks["syscall_filter"] = False

        # 8. Resource Isolation (MemoryMax and CPUWeight)
        mem = service_sec.get("MemoryMax", "")
        cpu = service_sec.get("CPUWeight", "")
        if mem and cpu:
            checks["resource_limits"] = True
        else:
            violations.append("MemoryMax and CPUWeight must both be specified")
            checks["resource_limits"] = False

        # Calculate score (scale 0.0 - 10.0)
        passed_count = sum(1 for v in checks.values() if v)
        total_checks = len(checks)
        score = (passed_count / total_checks) * 10.0 if total_checks > 0 else 0.0
        passed = (len(violations) == 0)

        return SecurityAuditResult(
            service_name=unit.name,
            user=user,
            score=score,
            passed=passed,
            checks=checks,
            violations=violations,
        )

    def audit_all(self, units: Dict[str, ServiceUnit]) -> Dict[str, SecurityAuditResult]:
        """Audit all provided units."""
        return {name: self.audit_unit(unit) for name, unit in units.items()}
