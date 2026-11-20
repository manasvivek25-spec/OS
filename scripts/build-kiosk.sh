#!/usr/bin/env bash
# Lazy OS Kiosk Build Script (Wayland + Cage + Cog + WPE WebKit + Mesa3D)
# Specification: docs/BUILD_PROMPT_V34.md (Item 2 & 3)

set -euo pipefail

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export gl_cv_func_getcwd_path_max=yes
export gl_cv_func_getcwd_abort_bug=no
export ac_cv_func_getcwd_null=yes

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUTPUT_DIR="/home/manas/lazy-build/output"
BUILDROOT_DIR="/mnt/c/Users/len/OS/build/buildroot-2024.02"
LOG_FILE="${REPO_ROOT}/build-logs/kiosk-build.log"
PID_FILE="/tmp/lazy-kiosk-build.pid"

mkdir -p "${REPO_ROOT}/build-logs"

echo "$$" > "${PID_FILE}"

echo "======================================================================" | tee "${LOG_FILE}"
echo "    Starting Lazy OS In-Guest Graphical Kiosk Stack Build (Approach B)" | tee -a "${LOG_FILE}"
echo "======================================================================" | tee -a "${LOG_FILE}"
echo "Packages:    Cage, Cog, WPE WebKit, Mesa3D, Wayland, wlroots" | tee -a "${LOG_FILE}"
echo "Parallelism: 4 jobs (-j4) for safe memory management" | tee -a "${LOG_FILE}"
echo "Log file:    ${LOG_FILE}" | tee -a "${LOG_FILE}"
echo "Start time:  $(date -u +"%Y-%m-%dT%H:%M:%SZ")" | tee -a "${LOG_FILE}"
echo "======================================================================" | tee -a "${LOG_FILE}"

START_TIME=$(date +%s)

# Compile Buildroot target packages with -j4
make -C "${OUTPUT_DIR}" -j4 2>&1 | tee -a "${LOG_FILE}"

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo "======================================================================" | tee -a "${LOG_FILE}"
echo "Build finished in ${ELAPSED} seconds ($(printf '%dm %ds' $((ELAPSED/60)) $((ELAPSED%60))))" | tee -a "${LOG_FILE}"
echo "Copying updated images to dist/..." | tee -a "${LOG_FILE}"

if [ -f "${OUTPUT_DIR}/images/rootfs.squashfs" ]; then
    cp "${OUTPUT_DIR}/images/rootfs.squashfs" "${REPO_ROOT}/dist/rootfs.squashfs"
fi
if [ -f "${OUTPUT_DIR}/images/bzImage" ]; then
    cp "${OUTPUT_DIR}/images/bzImage" "${REPO_ROOT}/dist/bzImage"
fi
if [ -f "${OUTPUT_DIR}/images/lazy-os.img" ]; then
    cp "${OUTPUT_DIR}/images/lazy-os.img" "${REPO_ROOT}/dist/lazy-os.img"
fi

rm -f "${PID_FILE}"
echo "=== Kiosk build complete and dist/ updated. ===" | tee -a "${LOG_FILE}"
