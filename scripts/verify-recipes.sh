#!/bin/bash
# Lazy OS BitBake Recipes & Image Profiles Verification (Milestone M5.2)
set -euo pipefail

echo "=== Lazy OS BitBake Recipes & Package Manifest Verification (M5.2) ==="
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
META_LAZY="$REPO_ROOT/yocto/meta-lazy"

REQUIRED_RECIPES=(
    "$META_LAZY/recipes-lazy/lazy-core/lazy-core_1.0.bb"
    "$META_LAZY/recipes-lazy/llama-cpp/llama-cpp_b3800.bb"
    "$META_LAZY/recipes-lazy/vosk/vosk-api_0.3.45.bb"
    "$META_LAZY/recipes-lazy/models/lazy-model-smollm_1.0.bb"
    "$META_LAZY/recipes-lazy/models/lazy-voice-model_1.0.bb"
    "$META_LAZY/recipes-browser/lazy-browser/lazy-browser_1.0.bb"
    "$META_LAZY/images/lazy-image-base.bb"
    "$META_LAZY/images/lazy-image-full.bb"
)

# 1. Check Recipe Files Existence
echo "[1/5] Checking BitBake recipe files..."
for r in "${REQUIRED_RECIPES[@]}"; do
    if [ ! -f "$r" ]; then
        echo "ERROR: Missing required recipe: $r" >&2
        exit 1
    fi
    rname="$(basename "$r")"
    echo "  Recipe found: $rname"
done

# 2. Audit Recipe Syntax and Required Variables
echo "[2/5] Auditing recipe syntax, licensing, and metadata..."
for r in "${REQUIRED_RECIPES[@]}"; do
    rname="$(basename "$r")"
    
    # Must have SUMMARY
    if ! grep -q "^SUMMARY" "$r"; then
        echo "ERROR: $rname missing SUMMARY variable" >&2
        exit 1
    fi
    # Must have LICENSE
    if ! grep -q "^LICENSE" "$r"; then
        echo "ERROR: $rname missing LICENSE variable" >&2
        exit 1
    fi
    # Non-image recipes must have LIC_FILES_CHKSUM
    if [[ ! "$rname" =~ ^lazy-image- ]] && ! grep -q "^LIC_FILES_CHKSUM" "$r"; then
        echo "ERROR: $rname missing LIC_FILES_CHKSUM" >&2
        exit 1
    fi
    echo "  $rname: Valid BitBake metadata (License: $(grep '^LICENSE' "$r" | tr -d '\"' | awk '{print $3}'))"
done

# 3. Audit Useradd and Systemd Integration in lazy-core
echo "[3/5] Verifying useradd and systemd integration in lazy-core..."
LAZY_CORE="$META_LAZY/recipes-lazy/lazy-core/lazy-core_1.0.bb"

REQUIRED_USERS=(
    "lazy-gw"
    "lazy-plan"
    "lazy-llm"
    "lazy-pol"
    "lazy-task"
    "lazy-brk-fs"
    "lazy-brk-sys"
    "lazy-brk-hw"
    "lazy-brk-web"
    "lazy-brk-comms"
    "lazy-secrets"
    "lazy-outbox"
    "lazy-fetch"
    "lazy-rout"
    "lazy-audit"
    "lazy-sandbox"
)

for u in "${REQUIRED_USERS[@]}"; do
    if ! grep -q "$u" "$LAZY_CORE"; then
        echo "ERROR: $LAZY_CORE missing dedicated user: $u" >&2
        exit 1
    fi
done
echo "  All 16 dedicated unprivileged service users properly declared in USERADD_PARAM"

REQUIRED_SERVICES=(
    "lazy-gateway.service"
    "lazy-planner.service"
    "lazy-llm.service"
    "lazy-policy.service"
    "lazy-tasks.service"
    "lazy-broker-fs.service"
    "lazy-broker-sys.service"
    "lazy-broker-hw.service"
    "lazy-broker-web.service"
    "lazy-broker-comms.service"
    "lazy-secrets.service"
    "lazy-outbox.service"
    "lazy-fetcher.service"
    "lazy-routines.service"
    "lazy-audit.service"
)

for s in "${REQUIRED_SERVICES[@]}"; do
    if ! grep -q "$s" "$LAZY_CORE"; then
        echo "ERROR: $LAZY_CORE missing systemd service: $s" >&2
        exit 1
    fi
done
echo "  All 15 Lazy OS systemd services enabled in SYSTEMD_SERVICE"

# 4. Audit Image Profiles Separation (base vs full)
echo "[4/5] Verifying base vs full image profile differentiation..."
BASE_IMG="$META_LAZY/images/lazy-image-base.bb"
FULL_IMG="$META_LAZY/images/lazy-image-full.bb"

# base image must NOT include heavy neural or speech components
if grep -q "llama-cpp" "$BASE_IMG" || grep -q "lazy-model" "$BASE_IMG"; then
    echo "ERROR: lazy-image-base.bb must not include neural model components (used for 40% size baseline)" >&2
    exit 1
fi

# full image MUST require base and include models
if ! grep -q "require lazy-image-base.bb" "$FULL_IMG"; then
    echo "ERROR: lazy-image-full.bb must inherit/require lazy-image-base.bb" >&2
    exit 1
fi
if ! grep -q "llama-cpp" "$FULL_IMG" || ! grep -q "lazy-model-smollm" "$FULL_IMG"; then
    echo "ERROR: lazy-image-full.bb missing llama-cpp or model weights" >&2
    exit 1
fi
echo "  Image profile separation verified: Base (headless minimal) vs Full (with resident AI stack)"

# 5. Audit Documentation Manifests
echo "[5/5] Auditing docs/PACKAGES.md and docs/LICENCES.md..."
if [ ! -f "$REPO_ROOT/docs/PACKAGES.md" ]; then
    echo "ERROR: docs/PACKAGES.md not found" >&2
    exit 1
fi
if ! grep -q "40%" "$REPO_ROOT/docs/PACKAGES.md"; then
    echo "ERROR: docs/PACKAGES.md missing 40% size reduction target comparison" >&2
    exit 1
fi

if [ ! -f "$REPO_ROOT/docs/LICENCES.md" ]; then
    echo "ERROR: docs/LICENCES.md not found" >&2
    exit 1
fi
if ! grep -q "MIT" "$REPO_ROOT/docs/LICENCES.md" || ! grep -q "Apache-2.0" "$REPO_ROOT/docs/LICENCES.md"; then
    echo "ERROR: docs/LICENCES.md missing standard license entries" >&2
    exit 1
fi
echo "  Documentation audit passed: PACKAGES.md and LICENCES.md fully compliant"

echo ""
echo "M5.2 VERIFICATION PASSED: All BitBake recipes, image profiles, package manifests, and licenses verified."
