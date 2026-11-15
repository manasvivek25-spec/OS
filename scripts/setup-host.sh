#!/usr/bin/env bash
set -euo pipefail

# scripts/setup-host.sh - Sets up Python venv and host dependencies

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${REPO_ROOT}/.venv"

echo "=== Lazy OS Host Setup ==="

# 1. Ensure Python virtualenv exists
if [ ! -d "${VENV_DIR}" ]; then
    echo "Creating virtual environment at ${VENV_DIR}..."
    python3 -m venv "${VENV_DIR}"
fi

# 2. Activate venv
source "${VENV_DIR}/bin/activate"

# 3. Upgrade pip and install minimal required packages
echo "Installing runtime and testing dependencies..."
pip install --upgrade pip --quiet
pip install --quiet jsonschema pyyaml pytest

# 4. Install repo in editable mode if pyproject/setup exists, or set PYTHONPATH
export PYTHONPATH="${REPO_ROOT}/src:${PYTHONPATH:-}"

echo "Host setup completed successfully. Python environment ready in ${VENV_DIR}."
