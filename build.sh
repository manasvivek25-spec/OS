#!/usr/bin/env bash
# Lazy OS Master Build Entrypoint
# Specification: docs/BUILD_PROMPT_V3.md (K1, O1)
# Usage: BUILD_SYSTEM=buildroot|yocto ./build.sh [base|full]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SCRIPT_DIR}"
BUILD_SYSTEM="${BUILD_SYSTEM:-buildroot}"
PROFILE="${1:-base}"
if [ "$PROFILE" != "base" ] && [ "$PROFILE" != "full" ]; then
    echo "ERROR: Invalid target profile '$PROFILE'. Usage: ./build.sh [base|full]" >&2
    exit 1
fi
BUILD_LOGS="${REPO_ROOT}/build-logs"
LOG_FILE="${BUILD_LOGS}/build.log"

mkdir -p "${BUILD_LOGS}" "${REPO_ROOT}/dist"

echo "======================================================================"
echo "          LAZY OS MASTER BUILD ENTRYPOINT (v3)"
echo "======================================================================"
echo "Build System: ${BUILD_SYSTEM}"
echo "Target Profile: ${PROFILE}"
echo "Log File:     ${LOG_FILE}"
echo "Timestamp:    $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "======================================================================"

if [ "${BUILD_SYSTEM}" = "yocto" ]; then
    echo "Checking Yocto hardware resource gate (>= 16 GB RAM required)..."
    TOTAL_RAM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    TOTAL_RAM_GB=$((TOTAL_RAM_KB / 1048576))
    if [ "${TOTAL_RAM_GB}" -lt 16 ]; then
        echo "RESOURCE GATE ENFORCED: Host has ${TOTAL_RAM_GB} GB RAM (< 16 GB threshold)."
        echo "See docs/BUILD_ENV_PLAN.md for cloud runbook instructions."
        echo "Exiting Yocto build. Use BUILD_SYSTEM=buildroot on this machine."
        exit 2
    fi
    exec "${REPO_ROOT}/scripts/build-yocto.sh" "$@"

elif [ "${BUILD_SYSTEM}" = "buildroot" ]; then
    BR_VERSION="2024.02"
    BR_DIR="${REPO_ROOT}/build/buildroot-${BR_VERSION}"
    OUTPUT_DIR="${REPO_ROOT}/build/br2-output"
    DL_DIR="/var/cache/buildroot/dl"
    CCACHE_DIR="/var/cache/buildroot/ccache"

    mkdir -p "${DL_DIR}" "${CCACHE_DIR}" "${OUTPUT_DIR}"

    if [ ! -d "${BR_DIR}" ]; then
        echo "Fetching official Buildroot ${BR_VERSION} source tarball..."
        TAR_FILE="${DL_DIR}/buildroot-${BR_VERSION}.tar.gz"
        if [ ! -f "${TAR_FILE}" ]; then
            wget -q -O "${TAR_FILE}" "https://buildroot.org/downloads/buildroot-${BR_VERSION}.tar.gz"
        fi
        echo "Extracting Buildroot to ${BR_DIR}..."
        mkdir -p "${REPO_ROOT}/build"
        tar -xzf "${TAR_FILE}" -C "${REPO_ROOT}/build/"
    fi

    echo "Configuring Buildroot with lazy-br2 external tree..."
    make -C "${BR_DIR}" \
        BR2_EXTERNAL="${REPO_ROOT}/lazy-br2" \
        O="${OUTPUT_DIR}" \
        lazy_x86_64_defconfig \
        2>&1 | tee "${LOG_FILE}"

    echo "Starting Buildroot build (logs redirected to ${LOG_FILE})..."
    make -C "${OUTPUT_DIR}" 2>&1 | tee -a "${LOG_FILE}"

    # Package artifacts into dist/
    if [ -f "${OUTPUT_DIR}/images/lazy-os.img" ]; then
        cp "${OUTPUT_DIR}/images/lazy-os.img" "${REPO_ROOT}/dist/lazy-os.img"
    elif [ -f "${OUTPUT_DIR}/images/bzImage" ]; then
        cp "${OUTPUT_DIR}/images/bzImage" "${REPO_ROOT}/dist/bzImage"
    fi

    echo "Buildroot build completed successfully."
else
    echo "ERROR: Unknown BUILD_SYSTEM '${BUILD_SYSTEM}'. Must be 'buildroot' or 'yocto'."
    exit 1
fi
