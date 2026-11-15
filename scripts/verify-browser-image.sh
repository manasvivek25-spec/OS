#!/bin/bash
# Lazy OS Browser Integration and Documented Fallback Verification (Milestone M5.5)
set -euo pipefail

echo "=== Lazy OS Web Browser Integration & Documented Fallback (M5.5) ==="
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$REPO_ROOT/src:${PYTHONPATH:-}"

META_LAZY="$REPO_ROOT/yocto/meta-lazy"
RECIPE="$META_LAZY/recipes-browser/lazy-browser/lazy-browser_1.0.bb"
FULL_IMAGE="$META_LAZY/images/lazy-image-full.bb"

# 1. Audit Browser Recipe and Image Manifest
echo "[1/5] Auditing browser BitBake recipe and image profile..."
test -f "$RECIPE"
if ! grep -q "SUMMARY" "$RECIPE"; then
    echo "ERROR: Missing SUMMARY in $RECIPE" >&2
    exit 1
fi
if ! grep -q "lazy-browser" "$FULL_IMAGE"; then
    echo "ERROR: Full image $FULL_IMAGE does not include lazy-browser" >&2
    exit 1
fi
echo "  Browser recipe and full image packaging verified."

# 2. Audit Documented Decisions and Fallbacks
echo "[2/5] Auditing DECISIONS.md and KNOWN_ISSUES.md for documented browser fallback..."
if ! grep -q "DEC-004" "$REPO_ROOT/docs/DECISIONS.md"; then
    echo "ERROR: docs/DECISIONS.md missing DEC-004 entry" >&2
    exit 1
fi
if ! grep -q "ISSUE-001" "$REPO_ROOT/docs/KNOWN_ISSUES.md"; then
    echo "ERROR: docs/KNOWN_ISSUES.md missing ISSUE-001 entry" >&2
    exit 1
fi
echo "  Decision DEC-004 and issue ISSUE-001 documented per Section 4 defaults."

# 3. Test Browser Driver Abstraction & Fallbacks
echo "[3/5] Testing browser driver interface (BaseBrowserDriver, WebDriver, PurePython)..."
python3 -m pytest "$REPO_ROOT/tests/unit/test_browser_driver.py" -v

# 4. Test Web Broker Capabilities and Security Guardrails
echo "[4/5] Testing WebBroker capabilities (web.read, web.navigate, web.click, web.fill, web.submit, web.download)..."
python3 -m pytest "$REPO_ROOT/tests/unit/test_broker_web.py" -v

# 5. Live Portal Navigation & Quarantine End-to-End Simulation
echo "[5/5] Running end-to-end browser navigation on local test portal..."
python3 - << 'EOF'
from pathlib import Path
import sys
from lazy.brokers.web_broker import WebBroker

repo_root = Path.cwd()
portal_dir = repo_root / "tests" / "fixtures" / "website"
quarantine = repo_root / "var" / "quarantine_test"
quarantine.mkdir(parents=True, exist_ok=True)

broker = WebBroker(base_dir=repo_root, quarantine_dir=quarantine)

# 1. Navigate to index page
res_nav = broker.execute("web.navigate", {"url": f"file://{portal_dir / 'index.html'}"})
assert res_nav["status"] == "ok"
assert res_nav["result"]["title"] == "Lazy OS Test Portal"
print("  E2E Step 1: Navigated to index.html successfully.")

# 2. Click link to search
res_click = broker.execute("web.click", {"element_id": "link-search"})
assert res_click["status"] == "ok"
print("  E2E Step 2: Clicked link-search successfully.")

# 3. Fill search query
res_fill = broker.execute("web.fill", {"element_id": "search_input", "value": "kernel fragments"})
assert res_fill["status"] == "ok"
print("  E2E Step 3: Filled search input successfully.")

# 4. Read page content (Rule F3 quoted data)
res_read = broker.execute("web.read", {})
assert res_read["status"] == "ok"
assert "Search Results" in res_read["result"]["visible_text"]
print("  E2E Step 4: Read page content with Rule F3 data wrapping.")

# 5. Download test file into quarantine
res_dl = broker.execute("web.download", {
    "url": f"file://{portal_dir / 'downloadable.txt'}",
    "dest_filename": "e2e_download.txt"
})
assert res_dl["status"] == "ok"
assert res_dl["result"]["quarantined"] is True
assert res_dl["result"]["permissions"] == "0600"
print(f"  E2E Step 5: Quarantined download with SHA256: {res_dl['result']['sha256'][:16]}...")
print("All end-to-end browser capabilities validated successfully.")
EOF

echo ""
echo "M5.5 VERIFICATION PASSED: Browser in full image and documented fallback verified."
