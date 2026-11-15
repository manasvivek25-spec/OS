#!/usr/bin/env bash
set -euo pipefail

# scripts/handoff.sh - Generates docs/HANDOFF.md from PLAN.md and STATE.md

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLAN_FILE="${REPO_ROOT}/docs/PLAN.md"
STATE_FILE="${REPO_ROOT}/docs/STATE.md"
HANDOFF_FILE="${REPO_ROOT}/docs/HANDOFF.md"

echo "Generating ${HANDOFF_FILE}..."

cat <<EOF > "${HANDOFF_FILE}"
# Lazy OS Session Handoff Document

Generated: $(date -u +"%Y-%m-%d %H:%M:%SZ")

## Immediate Next Action
$(head -n 1 "${STATE_FILE}")

## Current State Summary
$(cat "${STATE_FILE}")

## Milestone Progress Matrix
$(cat "${PLAN_FILE}")

## Instructions for Next Session
1. Read docs/STATE.md line 1 for NEXT_ACTION.
2. Read docs/PLAN.md to confirm completed vs pending milestones.
3. Verify prior milestone logs in tests/results/.
4. Execute NEXT_ACTION and continue iterative delivery loop.
EOF

echo "Wrote ${HANDOFF_FILE} successfully."
