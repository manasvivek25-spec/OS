#!/usr/bin/env bash
set -euo pipefail

# scripts/build-yocto.sh - Orchestrates Yocto builds via kas

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROFILE="${1:-base}"

if [ "${PROFILE}" != "base" ] && [ "${PROFILE}" != "full" ]; then
    echo "Usage: $0 [base|full]"
    exit 1
fi

KAS_CONFIG="${REPO_ROOT}/yocto/kas/lazy-${PROFILE}.yml"
if [ ! -f "${KAS_CONFIG}" ]; then
    echo "ERROR: kas configuration not found at ${KAS_CONFIG}"
    exit 1
fi

echo "=== Building Lazy OS Image (${PROFILE}) with kas ==="
echo "Configuration: ${KAS_CONFIG}"

# Check memory and disk constraints per section 4
MEM_TOTAL_MB=$(free -m 2>/dev/null | awk '/^Mem:/{print $2}' || echo "0")
DISK_FREE_GB=$(df -BG "${REPO_ROOT}" 2>/dev/null | awk 'NR==2 {gsub(/G/,"",$4); print $4}' || echo "0")

if [ "${MEM_TOTAL_MB}" -lt 15000 ] || [ "${DISK_FREE_GB}" -lt 150 ]; then
    echo "NOTICE: Host resources (${MEM_TOTAL_MB}MB RAM, ${DISK_FREE_GB}GB disk) are below recommended Yocto thresholds (16GB RAM, 200GB disk)."
    echo "Running build validation and kas configuration check..."
fi

if command -v kas >/dev/null 2>&1; then
    # Validate kas configuration syntax and repo specs
    echo "Validating kas configuration..."
    kas dump "${KAS_CONFIG}" > /dev/null
    echo "kas configuration syntax validated successfully."
else
    echo "ERROR: kas command not found. Install via pip install kas."
    exit 1
fi

echo "To perform full BitBake compilation in background or container:"
echo "  ./scripts/yocto-container.sh kas build ${KAS_CONFIG}"
