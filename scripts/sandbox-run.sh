#!/bin/bash
# Sandboxed code execution wrapper using systemd-run (Rule F2)
set -euo pipefail

EXEC_CMD="$*"
if [ -z "$EXEC_CMD" ]; then
    echo "Usage: $0 <command>" >&2
    exit 1
fi

# If running as root with systemd active and systemd-run available
if [ "$(id -u)" -eq 0 ] && command -v systemd-run >/dev/null 2>&1 && [ -d /run/systemd/system ]; then
    exec systemd-run \
        --quiet \
        --slice=lazy-code-sandbox.slice \
        --property=User=lazy-sandbox \
        --property=NoNewPrivileges=yes \
        --property=ProtectSystem=strict \
        --property=ProtectHome=read-only \
        --property=PrivateTmp=yes \
        --property=MemoryMax=256M \
        --property=CPUWeight=50 \
        --property=RestrictAddressFamilies=AF_UNIX \
        --property=SystemCallFilter="@system-service ~@privileged ~@resources" \
        --wait \
        --pipe \
        -- /bin/bash -c "$EXEC_CMD"
else
    # Fallback for environments without systemd PID 1 (e.g. host development container / WSL)
    exec /bin/bash -c "$EXEC_CMD"
fi
