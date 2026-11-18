#!/usr/bin/env bash
# Lazy OS Run Script for Windows Subsystem for Linux (WSL2)
# Usage: ./dist/run-wsl.sh [--headless]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${SCRIPT_DIR}/run-lazy-os.sh" "$@"
