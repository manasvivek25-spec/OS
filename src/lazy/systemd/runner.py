"""Transient sandboxed code execution runner (Rule F2, systemd-run)."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


def build_systemd_run_cmd(
    command: str,
    user: str = "lazy-sandbox",
    slice_name: str = "lazy-code-sandbox.slice",
    memory_max: str = "256M",
    cpu_weight: int = 50,
    timeout_sec: int = 30,
) -> List[str]:
    """Generate systemd-run command line arguments for sandboxed execution."""
    return [
        "systemd-run",
        "--quiet",
        f"--slice={slice_name}",
        f"--property=User={user}",
        "--property=NoNewPrivileges=yes",
        "--property=ProtectSystem=strict",
        "--property=ProtectHome=read-only",
        "--property=PrivateTmp=yes",
        f"--property=MemoryMax={memory_max}",
        f"--property=CPUWeight={cpu_weight}",
        "--property=RestrictAddressFamilies=AF_UNIX",
        '--property=SystemCallFilter=@system-service ~@privileged ~@resources',
        f"--property=TimeoutSec={timeout_sec}",
        "--wait",
        "--pipe",
        "--",
        "/bin/bash",
        "-c",
        command,
    ]


class SandboxedRunner:
    """Executes transient commands under systemd-run sandbox with fallback."""

    def __init__(self, wrapper_script: Optional[Path | str] = None):
        self.wrapper_script = Path(wrapper_script) if wrapper_script else Path("scripts/sandbox-run.sh")

    def run(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute command in sandbox."""
        is_root = (hasattr(os, "geteuid") and os.geteuid() == 0)
        has_systemd_run = (
            is_root
            and shutil.which("systemd-run") is not None
            and Path("/run/systemd/system").is_dir()
        )

        if has_systemd_run:
            cmd = build_systemd_run_cmd(command, timeout_sec=timeout)
        else:
            cmd = ["/bin/bash", "-c", command]

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        return {
            "command": command,
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "sandboxed": has_systemd_run,
        }
