"""Cgroup v2 priority configurations and process scheduling profiles for Lazy OS."""
from __future__ import annotations

from dataclasses import dataclass
import logging
import os
from typing import Dict, Optional

logger = logging.getLogger("lazy.tuning.cgroups")


@dataclass(frozen=True)
class CgroupProfile:
    """Resource scheduling parameters for cgroup v2 and process priority."""
    name: str
    cpu_weight: int       # cgroup v2 cpu.weight (1 - 10000, default 100)
    io_weight: int        # cgroup v2 io.weight (1 - 10000, default 100)
    nice: int             # Linux process nice priority (-20 to 19, default 0)
    memory_max: Optional[str] = None
    memory_high: Optional[str] = None


# High priority interactive services (Voice, LLM, Dialogue Planner, Gateway)
INTERACTIVE_PROFILE = CgroupProfile(
    name="interactive",
    cpu_weight=500,
    io_weight=500,
    nice=-5,
    memory_max="1024M",
)

# Standard priority services (Policy, Brokers, Secrets, Outbox, Audit)
NORMAL_PROFILE = CgroupProfile(
    name="normal",
    cpu_weight=100,
    io_weight=100,
    nice=0,
    memory_max="256M",
)

# Lower priority background routines and batch workloads (Chores, Feeds, Code sandbox)
BACKGROUND_PROFILE = CgroupProfile(
    name="background",
    cpu_weight=50,
    io_weight=50,
    nice=10,
    memory_max="256M",
)


SERVICE_PROFILE_MAP: Dict[str, CgroupProfile] = {
    # Interactive
    "lazy-llm": INTERACTIVE_PROFILE,
    "lazy-planner": INTERACTIVE_PROFILE,
    "lazy-gateway": INTERACTIVE_PROFILE,
    "lazy-voice": INTERACTIVE_PROFILE,
    # Background
    "lazy-routines": BACKGROUND_PROFILE,
    "lazy-fetcher": BACKGROUND_PROFILE,
    "lazy-chores": BACKGROUND_PROFILE,
    "lazy-code-sandbox": BACKGROUND_PROFILE,
}


def get_service_cgroup_profile(service_name: str) -> CgroupProfile:
    """Return the designated CgroupProfile for a service."""
    clean = service_name.replace(".service", "")
    return SERVICE_PROFILE_MAP.get(clean, NORMAL_PROFILE)


def apply_nice(nice_level: int, pid: int = 0) -> bool:
    """Set process nice level (-20 to 19).
    
    Negative values (higher priority) require CAP_SYS_NICE or unprivileged user limits.
    Gracefully catches PermissionError when running unprivileged.
    """
    if not hasattr(os, "setpriority") or not hasattr(os, "PRIO_PROCESS"):
        return False
    try:
        os.setpriority(os.PRIO_PROCESS, pid, nice_level)
        return True
    except PermissionError:
        logger.debug("Permission denied setting nice=%d (requires CAP_SYS_NICE)", nice_level)
        return False
    except Exception as e:
        logger.warning("Error setting nice level: %s", e)
        return False
