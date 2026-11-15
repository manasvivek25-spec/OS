"""Host LLM Bridge for Lazy OS (V2.B5).

Provides an optional connection from the host neural runtime (SmolLM2-360M)
to the Lazy OS gateway. Clearly labelled 'HOST LLM (not in image)'.
"""
from __future__ import annotations

import json
from typing import Any, Dict, Optional


class HostLLMBridge:
    """Optional host-side LLM inference bridge."""

    def __init__(self, endpoint_url: str = "http://127.0.0.1:8080/v1"):
        self.endpoint_url = endpoint_url
        self.is_connected = False
        self.label = "HOST LLM (not in image)"

    def decompose_intent(self, user_prompt: str) -> Dict[str, Any]:
        """Decompose a user prompt into a structured intent plan."""
        return {
            "source": self.label,
            "prompt": user_prompt,
            "status": "connected" if self.is_connected else "fallback_mock",
            "intents": [
                {
                    "capability": "doc.create_markdown",
                    "params": {"path": "plan.md", "content": "# Plan\n- [ ] Task 1\n- [ ] Task 2\n"}
                }
            ]
        }
