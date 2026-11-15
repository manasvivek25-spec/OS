#!/usr/bin/env bash
set -euo pipefail

# scripts/yocto-container.sh - Containerized build runner for Yocto using crops/poky

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONTAINER_IMAGE="crops/poky:ubuntu-22.04"

echo "=== Lazy OS Yocto Container Runner ==="
echo "Target Container Image: ${CONTAINER_IMAGE}"

# Check for container runtime (docker or podman)
RUNTIME=""
if command -v docker >/dev/null 2>&1; then
    RUNTIME="docker"
elif command -v podman >/dev/null 2>&1; then
    RUNTIME="podman"
fi

if [ -z "${RUNTIME}" ]; then
    echo "WARNING: Neither docker nor podman found on host."
    echo "If host Yocto resources are constrained, install docker/podman or run native bitbake/kas."
    exit 1
fi

echo "Using container runtime: ${RUNTIME}"
echo "Running containerized build command..."

${RUNTIME} run --rm -it \
    -v "${REPO_ROOT}:/workdir" \
    --workdir=/workdir \
    "${CONTAINER_IMAGE}" \
    "$@"
