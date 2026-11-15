"""Base broker handler definition for Lazy OS capabilities."""
from __future__ import annotations

import abc
from typing import Any, Callable, Dict, Optional, Tuple


class BrokerExecutionError(Exception):
    """Raised when a broker operation fails."""


class BaseBroker(abc.ABC):
    """Abstract base broker for capability execution."""

    def __init__(self, broker_name: str):
        self.broker_name = broker_name
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {}

    def register(self, capability: str, handler: Callable[[Dict[str, Any]], Any]) -> None:
        """Register a handler callback for a capability."""
        self._handlers[capability] = handler

    def can_handle(self, capability: str) -> bool:
        return capability in self._handlers

    def execute(self, capability: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch capability execution to its registered handler."""
        if capability not in self._handlers:
            raise BrokerExecutionError(f"Broker '{self.broker_name}' has no handler for '{capability}'")

        handler = self._handlers[capability]
        try:
            result = handler(params)
            return {"status": "ok", "capability": capability, "result": result}
        except Exception as err:
            return {"status": "error", "capability": capability, "error": str(err)}
