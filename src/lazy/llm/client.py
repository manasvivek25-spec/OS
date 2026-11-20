"""LLM client for Lazy OS interacting with llama.cpp server and grammar constraints.

Role B W3: MockPlanner fallback DELETED. Silent fallback to canned fixtures in
tests/fixtures/intents/ removed. If llama-server is unreachable, returns an explicit
structured error object (or raises RuntimeError if mock_fallback=False).
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
import uuid
from typing import Any, Dict, Optional

from lazy.common.contracts import ContractValidationError, validate_contract
from lazy.llm.grammar import get_intent_gbnf


class LLMClient:
    """Client for grammar-constrained LLM inference via llama.cpp.

    Communicates with llama-server running Qwen2.5-1.5B-Instruct-Q4_K_M.gguf.
    No silent mock fallback to canned fixtures.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8080",
        timeout: float = 30.0,
        mock_fallback: bool = False,
        fixtures_dir: Optional[Any] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.mock_fallback = mock_fallback
        if mock_fallback:
            from lazy.planner.mock import MockPlanner
            self._fallback_planner = MockPlanner(fixtures_dir=fixtures_dir)
        else:
            self._fallback_planner = None

    def is_healthy(self) -> bool:
        """Check if llama.cpp server is reachable and reports healthy."""
        try:
            req = urllib.request.Request(f"{self.base_url}/health", method="GET")
            with urllib.request.urlopen(req, timeout=2.0) as resp:
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
        """Generate a validated Intent from user prompt using grammar-constrained decoding.

        If llama-server is reachable, prompts the model with GBNF grammar constraints.
        If llama-server is unreachable:
          - If mock_fallback is False: raises RuntimeError("No LLM server available...")
          - Otherwise: returns an explicit structured error object.
        """
        grammar_str = grammar or get_intent_gbnf()
        tid = task_id or f"task-{uuid.uuid4().hex[:8]}"

        if not self.is_healthy():
            if self.mock_fallback and self._fallback_planner:
                return self._fallback_planner.propose_intent_for_prompt(prompt, requester=requester, task_id=tid)
            raise RuntimeError("No LLM server available and mock fallback is disabled.")

        payload = {
            "prompt": (
                "<|im_start|>system\n"
                "You are Lazy OS dialogue planner. Emit ONLY valid Intent JSON conforming to the schema.<|im_end|>\n"
                f"<|im_start|>user\n{prompt}<|im_end|>\n"
                "<|im_start|>assistant\n"
            ),
            "grammar": grammar_str,
            "n_predict": 512,
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
                if not intent.get("task_id"):
                    intent["task_id"] = tid
                if not intent.get("requester"):
                    intent["requester"] = requester
                validate_contract("intent", intent, strict=True)
                return intent
        except Exception as err:
            if not self.mock_fallback:
                raise RuntimeError(f"llama-server generation failed: {err}") from err
            return {
                "error": True,
                "status": "error",
                "reason": f"llama-server generation failed: {err}",
                "task_id": tid,
                "requester": requester,
                "capability": None,
            }

    def generate_intent_streaming(
        self,
        prompt: str,
        grammar: Optional[str] = None,
        requester: str = "text",
        task_id: Optional[str] = None,
    ):
        """Generator that yields token chunks from llama-server streaming endpoint."""
        grammar_str = grammar or get_intent_gbnf()
        tid = task_id or f"task-{uuid.uuid4().hex[:8]}"

        if not self.is_healthy():
            yield {
                "error": True,
                "status": "error",
                "reason": f"llama-server is unreachable at {self.base_url}",
                "task_id": tid,
            }
            return

        payload = {
            "prompt": (
                "<|im_start|>system\n"
                "You are Lazy OS dialogue planner. Emit ONLY valid Intent JSON conforming to the schema.<|im_end|>\n"
                f"<|im_start|>user\n{prompt}<|im_end|>\n"
                "<|im_start|>assistant\n"
            ),
            "grammar": grammar_str,
            "n_predict": 512,
            "temperature": 0.1,
            "stream": True,
            "stop": ["<|im_end|>", "\n\n"],
        }
        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/completion",
            data=req_data,
            headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
            method="POST",
        )

        accumulated = ""
        idx = 0
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                for line in resp:
                    line_str = line.decode("utf-8").strip()
                    if not line_str or not line_str.startswith("data: "):
                        continue
                    data_str = line_str[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk_data = json.loads(data_str)
                        token = chunk_data.get("content", "")
                        accumulated += token
                        idx += 1
                        yield {
                            "chunk": token,
                            "index": idx,
                            "done": chunk_data.get("stop", False),
                            "task_id": tid,
                        }
                    except json.JSONDecodeError:
                        continue

            try:
                intent = json.loads(accumulated.strip())
                if not intent.get("task_id"):
                    intent["task_id"] = tid
                if not intent.get("requester"):
                    intent["requester"] = requester
                validate_contract("intent", intent, strict=True)
                yield {"done": True, "intent": intent, "task_id": tid}
            except Exception as parse_err:
                yield {"error": True, "reason": f"Failed to parse final intent: {parse_err}", "task_id": tid}
        except Exception as err:
            yield {"error": True, "reason": f"Streaming failed: {err}", "task_id": tid}
