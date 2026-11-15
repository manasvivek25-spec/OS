"""Sliding window rate limiter for capability execution in lazy-policy."""
from __future__ import annotations

import time
from typing import Dict, List, Optional, Tuple


DEFAULT_RATE_LIMITS: Dict[str, Tuple[int, int]] = {
    # capability_name: (max_calls, window_seconds)
    "mail.send": (30, 3600),       # Max 30 emails per hour
    "chat.send": (60, 3600),       # Max 60 chats per hour
    "fs.delete": (20, 60),         # Max 20 deletions per minute
    "sys.service_restart": (10, 60), # Max 10 service restarts per minute
    "code.run": (20, 60),          # Max 20 code executions per minute
    "web.submit": (30, 3600),      # Max 30 form submits per hour
    "hw.usb_authorize": (5, 60),   # Max 5 USB authorizations per minute
}


class RateLimiter:
    """Sliding-window rate limiter ensuring safe operations bounds."""

    def __init__(self, limits: Optional[Dict[str, Tuple[int, int]]] = None):
        self.limits = limits if limits is not None else dict(DEFAULT_RATE_LIMITS)
        self._history: Dict[str, List[float]] = {}

    def is_rate_limited(self, capability: str, timestamp: Optional[float] = None) -> Tuple[bool, Optional[str]]:
        """Check if capability has exceeded its configured rate limit.

        Returns (is_limited, reason).
        """
        if capability not in self.limits:
            return False, None

        max_calls, window_sec = self.limits[capability]
        now = timestamp if timestamp is not None else time.time()
        window_start = now - window_sec

        calls = self._history.get(capability, [])
        # Filter calls inside window
        active_calls = [t for t in calls if t >= window_start]
        self._history[capability] = active_calls

        if len(active_calls) >= max_calls:
            return True, f"Rate limit exceeded for {capability}: {len(active_calls)}/{max_calls} calls in {window_sec}s"

        return False, None

    def record(self, capability: str, timestamp: Optional[float] = None) -> None:
        """Record an execution timestamp for the given capability."""
        now = timestamp if timestamp is not None else time.time()
        if capability not in self._history:
            self._history[capability] = []
        self._history[capability].append(now)

    def reset(self) -> None:
        """Clear all historical invocation records."""
        self._history.clear()
