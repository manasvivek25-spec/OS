# Assumptions Log

## 2026-11-15 - ASM-001: Python Runtime and Virtual Environment
- **Context**: Python 3.12 is the system Python in Ubuntu 24.04 WSL2.
- **Assumption**: A dedicated virtual environment (`.venv`) inside the repo or `/opt/lazy-venv` will isolate runtime dependencies (such as `jsonschema`, `pyyaml`, `pytest`) without modifying system packages, following PEP 668.
- **Impact**: Clean isolation, reproducible test results, no dependency drift.

## 2026-11-15 - ASM-002: Service IPC Directory and User IDs
- **Context**: Services communicate via `/run/lazy/*.sock` and each runs under a dedicated systemd user.
- **Assumption**: For host-level development and testing before image deployment, `/tmp/run-lazy` or `/run/lazy` (when running with sudo) will be used as the runtime socket directory with proper permissions (0755/0700).
- **Impact**: Enables full protocol integration testing on the host as well as inside the final target image.
