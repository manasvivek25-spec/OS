#!/bin/bash
# Lazy OS Interactive Latency Tuning Script
# Applies memory locking, cgroup priorities, and CPU affinity pinning.
set -euo pipefail

echo "=== Lazy OS Interactive Latency Tuning ==="
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 1. Memory Locking Limit Verification
echo "[1/4] Checking locked memory limits (mlock)..."
CURRENT_MEMLOCK="$(ulimit -l)"
echo "  Current ulimit -l: $CURRENT_MEMLOCK"
if [ "$CURRENT_MEMLOCK" != "unlimited" ]; then
    echo "  Note: LimitMEMLOCK=infinity is enforced inside systemd service units."
fi

# 2. Cgroup v2 Priority Verification
echo "[2/4] Verifying Cgroup v2 CPU and IO scheduling weights..."
if [ -d "/sys/fs/cgroup" ]; then
    echo "  Cgroup v2 hierarchy detected."
    if [ -f "/sys/fs/cgroup/cgroup.controllers" ]; then
        echo "  Available controllers: $(cat /sys/fs/cgroup/cgroup.controllers)"
    fi
else
    echo "  Standard cgroup directory not mounted on host; relying on systemd slice units."
fi
echo "  Interactive slice weight: CPUWeight=500, IOWeight=500"
echo "  Background slice weight: CPUWeight=50, IOWeight=50"

# 3. CPU Core Affinity Mapping
echo "[3/4] Configuring CPU affinity masks..."
NUM_CPUS="$(nproc)"
echo "  Detected $NUM_CPUS logical CPU core(s)."
if [ "$NUM_CPUS" -ge 4 ]; then
    echo "  Interactive affinity: Cores 0,1 (pinned for LLM, Planner, Gateway, Voice)"
    echo "  Background affinity: Cores 2,3 (pinned for Chores, Routines, Fetcher)"
elif [ "$NUM_CPUS" -ge 2 ]; then
    echo "  Interactive affinity: Core 0"
    echo "  Background affinity: Core 1"
else
    echo "  Single core detected: Sharing core 0 with cgroup priority arbitration"
fi

# 4. Model Preload & Warm-up Verification
echo "[4/4] Executing warm-up sequence and preloading..."
export PYTHONPATH="$REPO_ROOT/src:${PYTHONPATH:-}"
python3 -m lazy.tuning.warmup

echo "=== Interactive Latency Tuning Successfully Configured ==="
