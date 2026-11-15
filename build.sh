#!/usr/bin/env bash
# Lazy OS Master Build Entrypoint
# Section 4 DEFAULTS: "One command: ./build.sh base|full"
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${SCRIPT_DIR}/scripts/build-yocto.sh" "$@"
