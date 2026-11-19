"""In-guest LLM daemon managing llama-server process and Unix socket control."""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any, Dict
from lazy.common.socket_server import UnixSocketServer, parse_socket_arg
from lazy.llm.client import LLMClient
from lazy.llm.server import LLMServerProcess

MODEL_CANDIDATES = [
    Path("/usr/share/lazy/models/SmolLM2-360M-Instruct-Q4_K_M.gguf"),
    Path("/var/lib/lazy/models/SmolLM2-360M-Instruct-Q4_K_M.gguf"),
    Path("/build/models/SmolLM2-360M-Instruct-Q4_K_M.gguf"),
    Path("/mnt/c/Users/len/OS/build/models/SmolLM2-360M-Instruct-Q4_K_M.gguf"),
]


def find_model() -> Path | None:
    env_m = os.environ.get("LAZY_MODEL_PATH")
    if env_m and Path(env_m).is_file():
        return Path(env_m)
    for c in MODEL_CANDIDATES:
        if c.is_file():
            return c
    return None


def main():
    sock = parse_socket_arg("llm")
    model_path = find_model()
    server_proc = None
    if model_path and (shutil.which("llama-server") or shutil.which("llama.cpp/llama-server")):
        try:
            server_proc = LLMServerProcess(model_path=model_path, port=8080)
            server_proc.start(timeout=10.0)
        except Exception:
            server_proc = None

    client = LLMClient(mock_fallback=True)
    srv = UnixSocketServer(sock, service_name="lazy-llm")

    def handle_status(params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "ok",
            "server_running": server_proc.is_running if server_proc else False,
            "healthy": client.is_healthy(),
            "model": str(model_path) if model_path else "mock_builtin",
        }

    def handle_generate(params: Dict[str, Any]) -> Dict[str, Any]:
        prompt = params.get("prompt", "")
        grammar = params.get("grammar")
        intent = client.generate_intent(prompt=prompt, grammar=grammar)
        return {"status": "ok", "intent": intent}

    srv.register_simple("llm.status", handle_status)
    srv.register_simple("llm.health", handle_status)
    srv.register_simple("llm.generate", handle_generate)
    srv.serve_forever()


if __name__ == "__main__":
    main()
