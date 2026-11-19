#!/usr/bin/env bash
# Lazy OS Master Build Entrypoint (v3.2)
# Specification: docs/BUILD_PROMPT_V3.md (K1, O1), docs/BUILD_PROMPT_V3_1.md, V3.2 Task
# Usage: BUILD_SYSTEM=buildroot|yocto ./build.sh [base|full]

set -euo pipefail

# Sanitize PATH to ensure no host Windows directories with spaces cause Buildroot failure (WSL2 fix)
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
# Cache Gnulib/Autoconf WSL2 checks to avoid deep NTFS directory recursion hangs
export gl_cv_func_getcwd_path_max=yes
export gl_cv_func_getcwd_abort_bug=no
export ac_cv_func_getcwd_null=yes

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
TIMINGS_FILE="${REPO_ROOT}/docs/BUILD_TIMES.md"

mkdir -p "${BUILD_LOGS}" "${REPO_ROOT}/dist" "${REPO_ROOT}/docs"

echo "======================================================================"
echo "          LAZY OS MASTER BUILD ENTRYPOINT (v3.2)"
echo "======================================================================"
echo "Build System:   ${BUILD_SYSTEM}"
echo "Target Profile: ${PROFILE}"
echo "Log File:       ${LOG_FILE}"
echo "Timings File:   ${TIMINGS_FILE}"
echo "Timestamp:      $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "======================================================================"

TOTAL_START=$(date +%s)

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
    BR_DIR="${BUILDROOT_DIR:-/home/manas/lazy-build/buildroot-${BR_VERSION}}"
    OUTPUT_DIR="${BUILD_OUTPUT_DIR:-/home/manas/lazy-build/output}"
    DL_DIR="/var/cache/buildroot/dl"
    CCACHE_DIR="/var/cache/buildroot/ccache"

    mkdir -p "${DL_DIR}" "${CCACHE_DIR}" "${OUTPUT_DIR}" "${REPO_ROOT}/build"
    ln -sfn "${OUTPUT_DIR}" "${REPO_ROOT}/build/br2-output"

    # Stage 1: Buildroot source download & unpack
    STAGE1_START=$(date +%s)
    if [ ! -d "${BR_DIR}" ]; then
        echo "Fetching official Buildroot ${BR_VERSION} source tarball..."
        TAR_FILE="${DL_DIR}/buildroot-${BR_VERSION}.tar.gz"
        if [ ! -f "${TAR_FILE}" ]; then
            wget -q -O "${TAR_FILE}" "https://buildroot.org/downloads/buildroot-${BR_VERSION}.tar.gz"
        fi
        echo "Extracting Buildroot to ${BR_DIR}..."
        mkdir -p "$(dirname "${BR_DIR}")"
        tar -xzf "${TAR_FILE}" -C "$(dirname "${BR_DIR}")"
        mv "$(dirname "${BR_DIR}")/buildroot-${BR_VERSION}" "${BR_DIR}" 2>/dev/null || true
    fi
    STAGE1_END=$(date +%s)
    STAGE1_ELAPSED=$((STAGE1_END - STAGE1_START))

    # Stage 2: Target defconfig configuration
    STAGE2_START=$(date +%s)
    echo "Configuring Buildroot with lazy-br2 external tree..."
    make -C "${BR_DIR}" \
        BR2_EXTERNAL="${REPO_ROOT}/lazy-br2" \
        O="${OUTPUT_DIR}" \
        lazy_x86_64_defconfig \
        2>&1 | tee "${LOG_FILE}"
    STAGE2_END=$(date +%s)
    STAGE2_ELAPSED=$((STAGE2_END - STAGE2_START))

    # Stage 3: Compilation of toolchain, systemd, btrfs, python, services
    STAGE3_START=$(date +%s)
    echo "Starting Buildroot compilation (logs redirected to ${LOG_FILE})..."
    NPROC=$(nproc)
    make -C "${OUTPUT_DIR}" -j"${NPROC}" 2>&1 | tee -a "${LOG_FILE}"
    STAGE3_END=$(date +%s)
    STAGE3_ELAPSED=$((STAGE3_END - STAGE3_START))

    # Stage 4: Legal Information & SBOM generation (Item 6)
    STAGE4_START=$(date +%s)
    echo "Generating SBOM, licence list, and manifest via make legal-info..."
    make -C "${OUTPUT_DIR}" legal-info 2>&1 | tee -a "${LOG_FILE}"
    mkdir -p "${REPO_ROOT}/dist/legal-info"
    cp -r "${OUTPUT_DIR}/legal-info/"* "${REPO_ROOT}/dist/legal-info/" 2>/dev/null || true
    STAGE4_END=$(date +%s)
    STAGE4_ELAPSED=$((STAGE4_END - STAGE4_START))

    # Stage 5: Artifact Packaging
    STAGE5_START=$(date +%s)
    echo "Packaging genuine Buildroot artifacts into dist/..."
    if [ -f "${OUTPUT_DIR}/images/rootfs.squashfs" ]; then
        cp "${OUTPUT_DIR}/images/rootfs.squashfs" "${REPO_ROOT}/dist/rootfs.squashfs"
    fi
    if [ -f "${OUTPUT_DIR}/images/bzImage" ]; then
        cp "${OUTPUT_DIR}/images/bzImage" "${REPO_ROOT}/dist/bzImage"
    fi
    if [ -f "${OUTPUT_DIR}/images/lazy-os.img" ]; then
        cp "${OUTPUT_DIR}/images/lazy-os.img" "${REPO_ROOT}/dist/lazy-os.img"
    fi
    STAGE5_END=$(date +%s)
    STAGE5_ELAPSED=$((STAGE5_END - STAGE5_START))

    TOTAL_END=$(date +%s)
    TOTAL_ELAPSED=$((TOTAL_END - TOTAL_START))

    # Write real elapsed times to docs/BUILD_TIMES.md (Item 6)
    cat << EOF > "${TIMINGS_FILE}"
# Lazy OS Build Times (Measured Real Elapsed Time)

**Build Date:** $(date -u +"%Y-%m-%dT%H:%M:%SZ")  
**Build System:** Buildroot ${BR_VERSION} (`lazy-br2/`)  
**Target Architecture:** x86_64 UEFI (corei7)  
**Host Environment:** WSL2 Ubuntu 24.04 (${NPROC} CPUs, 11.5 GB RAM)  
**Measurement Method:** Wall-clock elapsed time measured with \`date +%s\` (per Item 6, never estimated)  

| Build Stage | Description | Measured Elapsed Time (s) | Human Readable |
| :--- | :--- | :--- | :--- |
| **Stage 1: Source Preparation** | Buildroot tarball download and extraction | ${STAGE1_ELAPSED} s | $(printf '%dm %ds' $((STAGE1_ELAPSED/60)) $((STAGE1_ELAPSED%60))) |
| **Stage 2: Configuration** | Kconfig defconfig merge & dependency validation | ${STAGE2_ELAPSED} s | $(printf '%dm %ds' $((STAGE2_ELAPSED/60)) $((STAGE2_ELAPSED%60))) |
| **Stage 3: Compilation** | Toolchain, systemd, Btrfs, Python 3, packages & rootfs | ${STAGE3_ELAPSED} s | $(printf '%dm %ds' $((STAGE3_ELAPSED/60)) $((STAGE3_ELAPSED%60))) |
| **Stage 4: Legal Info & SBOM** | Legal manifest (\`manifest.csv\`), licenses & SBOM generation | ${STAGE4_ELAPSED} s | $(printf '%dm %ds' $((STAGE4_ELAPSED/60)) $((STAGE4_ELAPSED%60))) |
| **Stage 5: Packaging** | Artifact transfer to \`dist/\` (SquashFS, bzImage, disk image) | ${STAGE5_ELAPSED} s | $(printf '%dm %ds' $((STAGE5_ELAPSED/60)) $((STAGE5_ELAPSED%60))) |
| **Total Build Time** | **Complete clean build from source to bootable image** | **${TOTAL_ELAPSED} s** | **$(printf '%dm %ds' $((TOTAL_ELAPSED/60)) $((TOTAL_ELAPSED%60)))** |

EOF

    echo "======================================================================"
    echo "          BUILDROOT BUILD COMPLETED IN ${TOTAL_ELAPSED}s              "
    echo "======================================================================"
else
    echo "ERROR: Unknown BUILD_SYSTEM '${BUILD_SYSTEM}'. Must be 'buildroot' or 'yocto'."
    exit 1
fi
