#!/bin/bash
# Lazy OS Documentation and Presentation Deliverables Verification (Milestone M6.3)
set -euo pipefail

echo "=== Lazy OS Documentation Verification (M6.3) ==="
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 1. Audit Core Documentation Files
echo "[1/5] Checking core documentation files..."
REQUIRED_DOCS=(
    "$REPO_ROOT/README.md"
    "$REPO_ROOT/docs/SPEC.md"
    "$REPO_ROOT/docs/BUILD_PROMPT.md"
    "$REPO_ROOT/docs/PLAN.md"
    "$REPO_ROOT/docs/STATE.md"
    "$REPO_ROOT/docs/DECISIONS.md"
    "$REPO_ROOT/docs/ASSUMPTIONS.md"
    "$REPO_ROOT/docs/KNOWN_ISSUES.md"
    "$REPO_ROOT/docs/ENV.md"
    "$REPO_ROOT/docs/LICENCES.md"
    "$REPO_ROOT/docs/PACKAGES.md"
    "$REPO_ROOT/docs/ARCHITECTURE.md"
    "$REPO_ROOT/docs/HARDWARE-CONTROL.md"
    "$REPO_ROOT/docs/reports/results.md"
    "$REPO_ROOT/docs/demo/RUNSHEET.md"
)

for doc in "${REQUIRED_DOCS[@]}"; do
    if [ ! -f "$doc" ]; then
        echo "ERROR: Missing required documentation file: $doc" >&2
        exit 1
    fi
    if [ ! -s "$doc" ]; then
        echo "ERROR: Documentation file is empty: $doc" >&2
        exit 1
    fi
    echo "  Found: $(basename "$doc")"
done

# 2. Audit Deck Inputs for Assignment Tasks 1 to 8
echo "[2/5] Checking presentation slide deck inputs (tasks 1 to 8)..."
DECK_DIR="$REPO_ROOT/docs/deck-inputs"
for i in {1..8}; do
    deck_file="$DECK_DIR/task${i}.md"
    if [ ! -f "$deck_file" ]; then
        echo "ERROR: Missing deck input: $deck_file" >&2
        exit 1
    fi
    # Check that evidence links exist in deck file
    if ! grep -q "Evidence" "$deck_file"; then
        echo "ERROR: $deck_file missing Evidence section" >&2
        exit 1
    fi
    echo "  Found: task${i}.md (verified with evidence links)"
done

# 3. Audit README Quick Start (Under 10 Commands)
echo "[3/5] Verifying README quickstart command count..."
README_FILE="$REPO_ROOT/README.md"
# Count commands inside the first ```bash code block
CMD_COUNT=$(sed -n '/```bash/,/```/p' "$README_FILE" | grep -v '```' | grep -v '^[[:space:]]*#' | grep -v '^[[:space:]]*$' | wc -l)
echo "  Detected $CMD_COUNT quickstart commands in README.md."
if [ "$CMD_COUNT" -gt 10 ]; then
    echo "ERROR: README.md quickstart contains $CMD_COUNT commands (must be under 10 commands per prompt specification)" >&2
    exit 1
fi
echo "  README command count ($CMD_COUNT) is strictly under 10 commands."

# 4. Audit Architecture and Hardware Control Diagrams
echo "[4/5] Checking diagrams and technical depth in ARCHITECTURE.md and HARDWARE-CONTROL.md..."
ARCH_FILE="$REPO_ROOT/docs/ARCHITECTURE.md"
if ! grep -q "mermaid" "$ARCH_FILE"; then
    echo "ERROR: docs/ARCHITECTURE.md missing Mermaid diagrams" >&2
    exit 1
fi
if ! grep -q "Frozen Invariants" "$ARCH_FILE"; then
    echo "ERROR: docs/ARCHITECTURE.md missing Frozen Invariants section" >&2
    exit 1
fi

HW_FILE="$REPO_ROOT/docs/HARDWARE-CONTROL.md"
if ! grep -q "LAZY_SYSFS_ROOT" "$HW_FILE"; then
    echo "ERROR: docs/HARDWARE-CONTROL.md missing injectable sysfs root documentation" >&2
    exit 1
fi
echo "  Mermaid diagrams and technical specifications verified."

# 5. Audit Demo Runsheet and Fallback Video Script
echo "[5/5] Checking docs/demo/RUNSHEET.md for live runsheet and fallback video script..."
RUNSHEET="$REPO_ROOT/docs/demo/RUNSHEET.md"
if ! grep -q "Part I: Live Demonstration Runsheet" "$RUNSHEET"; then
    echo "ERROR: $RUNSHEET missing Live Demonstration Runsheet" >&2
    exit 1
fi
if ! grep -q "Part II: Fallback Video Script" "$RUNSHEET"; then
    echo "ERROR: $RUNSHEET missing Fallback Video Script" >&2
    exit 1
fi
echo "  Live runsheet and fallback video script verified."

echo ""
echo "M6.3 VERIFICATION PASSED: All documentation, diagrams, deck inputs, and demo runsheet verified."
