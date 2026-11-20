"""In-guest LLM daemon managing llama-server process and Unix socket control.

Role B W3: Updated to use Qwen2.5-1.5B-Instruct-Q4_K_M.gguf (Apache-2.0).
MockPlanner fallback removed — explicit errors on llama-server unavailability.
"""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict
from lazy.common.socket_server import UnixSocketServer, parse_socket_arg
from lazy.llm.client import LLMClient
from lazy.llm.server import LLMServerProcess

# Qwen2.5-1.5B-Instruct-Q4_K_M.gguf — Apache-2.0, ~1 GB, 0 proprietary components
MODEL_CANDIDATES = [
    Path("/usr/share/lazy/models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"),
    Path("/var/lib/lazy/models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"),
    Path("/build/models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"),
    Path("/data/models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"),
]


def find_model() -> Path | None:
    """Locate the Qwen2.5-1.5B-Instruct GGUF model on disk."""
    env_m = os.environ.get("LAZY_MODEL_PATH")
    if env_m and Path(env_m).is_file():
        return Path(env_m)
    for c in MODEL_CANDIDATES:
        if c.is_file():
            return c
    return None


def load_model_manifest() -> Dict[str, Any]:
    """Load MODEL_MANIFEST.json from the same directory as this module."""
    manifest_path = Path(__file__).parent / "MODEL_MANIFEST.json"
    if manifest_path.is_file():
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    return {}


def main():
    sock = parse_socket_arg("llm")
    model_path = find_model()
    manifest = load_model_manifest()
    server_proc = None

    if model_path and (shutil.which("llama-server") or shutil.which("llama.cpp/llama-server")):
        try:
            server_proc = LLMServerProcess(
                model_path=model_path,
                port=8080,
                threads=manifest.get("threads", 4),
                context_size=manifest.get("context_size", 2048),
            )
            server_proc.start(timeout=15.0)
        except Exception:
            server_proc = None

    # No mock fallback — explicit errors if server is down
    client = LLMClient(base_url="http://127.0.0.1:8080", timeout=30.0)
    srv = UnixSocketServer(sock, service_name="lazy-llm")

    def handle_status(params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "ok",
            "server_running": server_proc.is_running if server_proc else False,
            "healthy": client.is_healthy(),
            "model": manifest.get("model_name", str(model_path) if model_path else "unavailable"),
            "model_file": manifest.get("model_file", "unknown"),
            "license": manifest.get("license", "unknown"),
            "inference_engine": "llama.cpp",
            "simd": manifest.get("simd", "unknown"),
        }

    def handle_generate(params: Dict[str, Any]) -> Dict[str, Any]:
        prompt = params.get("prompt", "")
        grammar = params.get("grammar")
        try:
            intent = client.generate_intent(prompt=prompt, grammar=grammar)
            return {"status": "ok", "intent": intent}
        except RuntimeError as e:
            return {"status": "error", "error": str(e)}

    srv.register_simple("llm.status", handle_status)
    srv.register_simple("llm.health", handle_status)
    srv.register_simple("llm.generate", handle_generate)
    srv.serve_forever()


if __name__ == "__main__":
    main()
