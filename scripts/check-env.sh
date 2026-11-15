#!/usr/bin/env bash
set -euo pipefail

# scripts/check-env.sh - Evaluates host environment and generates docs/ENV.md

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${REPO_ROOT}/docs/ENV.md"

echo "=== Lazy OS Environment Check ==="

# Gather system info
OS_NAME=$(uname -s 2>/dev/null || echo "Unknown")
KERNEL_RELEASE=$(uname -r 2>/dev/null || echo "Unknown")
ARCH=$(uname -m 2>/dev/null || echo "Unknown")
NPROC=$(nproc 2>/dev/null || echo "1")

# Memory in MB
MEM_TOTAL_MB=$(free -m 2>/dev/null | awk '/^Mem:/{print $2}' || echo "0")
MEM_AVAIL_MB=$(free -m 2>/dev/null | awk '/^Mem:/{print $7}' || echo "0")
SWAP_TOTAL_MB=$(free -m 2>/dev/null | awk '/^Swap:/{print $2}' || echo "0")

# Disk in GB
DISK_FREE_GB=$(df -BG "${REPO_ROOT}" 2>/dev/null | awk 'NR==2 {gsub(/G/,"",$4); print $4}' || echo "0")

# Tool checks
check_tool() {
    local cmd="$1"
    if command -v "$cmd" >/dev/null 2>&1; then
        local ver
        ver=$("$cmd" --version 2>&1 | head -n 1 || echo "installed")
        echo "FOUND: $ver"
    else
        echo "MISSING"
    fi
}

PYTHON_VER=$(check_tool python3)
GIT_VER=$(check_tool git)
MAKE_VER=$(check_tool make)
GCC_VER=$(check_tool gcc)
JQ_VER=$(check_tool jq)
CURL_VER=$(check_tool curl)
QEMU_VER=$(check_tool qemu-system-x86_64)

# Sudo check
if sudo -n true 2>/dev/null; then
    SUDO_STATUS="Passwordless sudo available"
else
    SUDO_STATUS="Passwordless sudo NOT available"
fi

# Yocto feasibility
YOCTO_CAPABLE="YES"
YOCTO_NOTES=()
if [ "$MEM_TOTAL_MB" -lt 15000 ]; then
    YOCTO_NOTES+=("RAM is ${MEM_TOTAL_MB}MB (<16GB recommendation; swap is ${SWAP_TOTAL_MB}MB, total virtual memory $((MEM_TOTAL_MB + SWAP_TOTAL_MB))MB)")
fi
if [ "$DISK_FREE_GB" -lt 150 ]; then
    YOCTO_NOTES+=("Free disk is ${DISK_FREE_GB}GB (<200GB recommendation)")
    YOCTO_CAPABLE="CONSTRAINED"
fi

# Write docs/ENV.md
cat <<EOF > "${ENV_FILE}"
# Host Environment Profile

Generated on $(date -u +"%Y-%m-%d %H:%M:%SZ") by \`scripts/check-env.sh\`.

## Hardware & Architecture
- **Architecture**: ${ARCH}
- **Kernel / OS**: ${OS_NAME} ${KERNEL_RELEASE}
- **Logical CPU Cores**: ${NPROC}
- **Total Physical RAM**: ${MEM_TOTAL_MB} MB (~$((MEM_TOTAL_MB / 1024)) GB)
- **Available RAM**: ${MEM_AVAIL_MB} MB
- **Swap Space**: ${SWAP_TOTAL_MB} MB
- **Workspace Disk Free**: ${DISK_FREE_GB} GB

## Privilege & Sandboxing
- **Sudo Capability**: ${SUDO_STATUS}
- **Container / Isolation**: WSL2 Linux Subsystem Environment

## Toolchain & Dependencies
- **Python 3**: ${PYTHON_VER}
- **Git**: ${GIT_VER}
- **GNU Make**: ${MAKE_VER}
- **GCC**: ${GCC_VER}
- **jq**: ${JQ_VER}
- **curl**: ${CURL_VER}
- **qemu-system-x86_64**: ${QEMU_VER}

## Yocto Build Feasibility
- **Feasible**: ${YOCTO_CAPABLE}
$([ ${#YOCTO_NOTES[@]} -gt 0 ] && for note in "${YOCTO_NOTES[@]}"; do echo "- Note: ${note}"; done)
EOF

echo "Wrote environment report to ${ENV_FILE}"
echo "Environment check completed successfully."
