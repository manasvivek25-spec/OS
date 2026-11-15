"""Lazy OS Interactive Latency Tuning and Resource Scheduling Package."""
from __future__ import annotations

from lazy.tuning.memory import lock_memory, unlock_memory, preload_and_fault, is_memory_locked
from lazy.tuning.affinity import (
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

__all__ = [
    "lock_memory",
    "unlock_memory",
    "preload_and_fault",
    "is_memory_locked",
    "set_cpu_affinity",
    "get_cpu_affinity",
    "get_service_affinity_map",
    "apply_service_affinity",
    "CgroupProfile",
    "INTERACTIVE_PROFILE",
    "NORMAL_PROFILE",
    "BACKGROUND_PROFILE",
    "apply_nice",
    "get_service_cgroup_profile",
    "ModelWarmup",
]
