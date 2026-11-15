"""LLM client for Lazy OS interacting with llama.cpp server and grammar constraints."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from lazy.common.contracts import ContractValidationError, validate_contract
from lazy.llm.grammar import get_intent_gbnf
from lazy.planner.mock import MockPlanner


class LLMClient:
    """Client for grammar-constrained LLM inference via llama.cpp or local fallback."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8080",
        timeout: float = 10.0,
        mock_fallback: bool = True,
        fixtures_dir: Optional[Path | str] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.mock_fallback = mock_fallback
        self._fallback_planner = MockPlanner(fixtures_dir=fixtures_dir) if mock_fallback else None

    def is_healthy(self) -> bool:
        """Check if llama.cpp server is reachable and reports healthy."""
        try:
            req = urllib.request.Request(f"{self.base_url}/health", method="GET")
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("status") == "ok" or resp.status == 200
        except Exception:
            return False

    def generate_intent(
        self,
        prompt: str,
        grammar: Optional[str] = None,
        requester: str = "text",
        task_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a validated Intent from user prompt using grammar-constrained decoding."""
        grammar_str = grammar or get_intent_gbnf()
        tid = task_id or f"task-{uuid.uuid4().hex[:8]}"

        # Attempt llama.cpp HTTP completion if server is running
        if self.is_healthy():
            payload = {
                "prompt": f"<|im_start|>system\nYou are Lazy OS dialogue planner. Emit only valid Intent JSON.<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n",
                "grammar": grammar_str,
                "n_predict": 256,
                "temperature": 0.1,
                "stop": ["<|im_end|>", "\n\n"],
            }
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{self.base_url}/completion",
                data=req_data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    resp_json = json.loads(resp.read().decode("utf-8"))
                    content = resp_json.get("content", "").strip()
                    intent = json.loads(content)
                    validate_contract("intent", intent, strict=True)
                    return intent
            except Exception as err:
                if not self.mock_fallback:
                    raise RuntimeError(f"llama-server generation failed: {err}") from err

        # Fallback to deterministic mock generator constrained to contract
        if self.mock_fallback and self._fallback_planner:
            try:
                plan = self._fallback_planner.plan(prompt, requester=requester, task_id=tid)
                intent = plan["steps"][0]
                validate_contract("intent", intent, strict=True)
                return intent
            except ValueError as val_err:
                # If prompt is an injection or unrecognized instruction, return safe refusal intent
                refusal_intent = {
                    "id": f"intent-{uuid.uuid4().hex[:8]}",
                    "ts": "2026-11-15T12:00:00Z",
                    "task_id": tid,
                    "requester": requester,
                    "capability": "fs.read",
                    "params": {"path": "/etc/issue"},
                    "provenance": [
                        {
                            "source": "planner",
                            "trusted": False,
                            "detail": f"Unrecognized or injection input rejected: {str(val_err)}",
                        }
                    ],
                }
                validate_contract("intent", refusal_intent, strict=True)
                return refusal_intent

        raise RuntimeError("No LLM server available and mock fallback is disabled.")
