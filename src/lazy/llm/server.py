"""llama.cpp server process management and lifecycle for lazy-llm."""
from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import List, Optional

import urllib.request


class LLMServerProcess:
    """Manages spawning, monitoring, and terminating a llama-server instance."""

    def __init__(
        self,
        model_path: Path | str,
        host: str = "127.0.0.1",
        port: int = 8080,
        threads: int = 4,
        context_size: int = 2048,
        llama_server_bin: Optional[str] = None,
    ):
        self.model_path = Path(model_path)
        self.host = host
        self.port = port
        self.threads = threads
        self.context_size = context_size
        self.llama_server_bin = llama_server_bin or shutil.which("llama-server") or "llama-server"
        self._proc: Optional[subprocess.Popen] = None

    @property
    def is_running(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    def start(self, timeout: float = 15.0) -> bool:
        """Start the llama-server process and wait until healthy."""
        if not shutil.which(self.llama_server_bin):
            return False

        if not self.model_path.is_file():
            return False

        cmd = [
            self.llama_server_bin,
            "-m", str(self.model_path),
            "--host", self.host,
            "--port", str(self.port),
            "-t", str(self.threads),
            "-c", str(self.context_size),
            "-ngl", "0",
        ]

        self._proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.is_running:
                return False
            try:
                url = f"http://{self.host}:{self.port}/health"
                with urllib.request.urlopen(url, timeout=0.5) as resp:
                    if resp.status == 200:
                        return True
            except Exception:
                time.sleep(0.5)

        return False

    def stop(self) -> None:
        """Terminate the server process."""
        if self._proc:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=3.0)
            except Exception:
                try:
                    self._proc.kill()
                except Exception:
                    pass
            finally:
                self._proc = None
