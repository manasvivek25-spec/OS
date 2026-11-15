"""CPU affinity management and core pinning for Lazy OS services."""
from __future__ import annotations

import logging
import os
from typing import Dict, List, Optional, Set

logger = logging.getLogger("lazy.tuning.affinity")

INTERACTIVE_SERVICES = {
    "lazy-llm",
    "lazy-planner",
    "lazy-gateway",
    "lazy-voice",
    "lazy-policy",
}

BACKGROUND_SERVICES = {
    "lazy-routines",
    "lazy-fetcher",
    "lazy-chores",
    "lazy-code-sandbox",
}


def get_available_cpus() -> List[int]:
    """Return list of online logical CPU IDs."""
    count = os.cpu_count() or 1
    return list(range(count))


def set_cpu_affinity(cpus: Set[int] | List[int], pid: int = 0) -> bool:
    """Set CPU affinity mask for specified pid (0 = current process)."""
    if not hasattr(os, "sched_setaffinity"):
        logger.warning("os.sched_setaffinity not supported on this OS")
        return False

    avail = set(get_available_cpus())
    target = set(cpus) & avail
    if not target:
        target = avail  # Fallback to all online CPUs

    try:
        os.sched_setaffinity(pid, target)
        logger.debug("Set CPU affinity for PID %d to %s", pid, target)
        return True
    except Exception as e:
        logger.warning("Failed to set CPU affinity for PID %d: %s", pid, e)
        return False


def get_cpu_affinity(pid: int = 0) -> Set[int]:
    """Get current CPU affinity mask for specified pid (0 = current process)."""
    if not hasattr(os, "sched_getaffinity"):
        return set(get_available_cpus())
    try:
        return set(os.sched_getaffinity(pid))
    except Exception:
        return set(get_available_cpus())


def get_service_affinity_map(total_cpus: Optional[int] = None) -> Dict[str, Set[int]]:
    """Generate default service-to-CPU affinity mapping based on available cores."""
    n = total_cpus if total_cpus is not None else (os.cpu_count() or 1)
    
    if n >= 4:
        # 4+ cores: Performance cores {0, 1} for interactive, efficiency/background {2, 3} for routines
        interactive_cores = {0, 1}
        background_cores = {2, 3}
    elif n >= 2:
        # 2 cores: Dedicated interactive core {0}, background core {1}
        interactive_cores = {0}
        background_cores = {1}
    else:
        # Single core
        interactive_cores = {0}
        background_cores = {0}

    mapping: Dict[str, Set[int]] = {}
    for svc in INTERACTIVE_SERVICES:
        mapping[svc] = set(interactive_cores)
    for svc in BACKGROUND_SERVICES:
        mapping[svc] = set(background_cores)

    return mapping


def apply_service_affinity(service_name: str, pid: int = 0) -> bool:
    """Apply standard CPU affinity for a named Lazy OS service."""
    mapping = get_service_affinity_map()
    clean_name = service_name.replace(".service", "")
    target_cores = mapping.get(clean_name)
    if target_cores is not None:
        return set_cpu_affinity(target_cores, pid=pid)
    return True
