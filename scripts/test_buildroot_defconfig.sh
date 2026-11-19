#!/usr/bin/env bash
set -euo pipefail
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

REPO_ROOT="/mnt/c/Users/len/OS"
BR_DIR="${REPO_ROOT}/build/buildroot-2024.02"
O_DIR="${REPO_ROOT}/build/br2-output"

cat << 'EOF' > /tmp/custom_toolchain_defconfig
BR2_x86_64=y
BR2_TOOLCHAIN_EXTERNAL=y
BR2_TOOLCHAIN_EXTERNAL_CUSTOM=y
BR2_TOOLCHAIN_EXTERNAL_PATH="/home/manas/toolchain"
BR2_TOOLCHAIN_EXTERNAL_CUSTOM_GLIBC=y
BR2_TOOLCHAIN_EXTERNAL_HEADERS_4_19=y
BR2_TOOLCHAIN_EXTERNAL_CUSTOM_VERSION_13_X=y
BR2_TOOLCHAIN_EXTERNAL_CXX=y
BR2_TOOLCHAIN_EXTERNAL_OPENMP=y
# BR2_TOOLCHAIN_EXTERNAL_INET_RPC is not set
BR2_INIT_SYSTEMD=y
BR2_PACKAGE_PYTHON3=y
EOF

make -C "${BR_DIR}" BR2_EXTERNAL="${REPO_ROOT}/lazy-br2" O="${O_DIR}" DEFCONFIG=/tmp/custom_toolchain_defconfig defconfig
make -C "${O_DIR}" toolchain
