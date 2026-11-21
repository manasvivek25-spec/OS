#!/usr/bin/env bash
set -e

cd /home/manas/yocto-build
source /home/manas/yocto-venv/bin/activate
export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

START_TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
T0=$(date +%s)
echo "=== YOCTO STAGE A BUILD STARTED AT $START_TS ==="

EXIT_CODE=0
kas build /mnt/c/Users/len/OS/yocto/kas/lazy-base.yml > /home/manas/yocto-build/build.log 2>&1 || EXIT_CODE=$?

T1=$(date +%s)
END_TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
ELAPSED=$((T1 - T0))
echo "=== YOCTO STAGE A BUILD FINISHED AT $END_TS (Exit Code: $EXIT_CODE, Elapsed: ${ELAPSED}s) ==="

python3 - << PYEOF
import json
data = {
    "start_time": "$START_TS",
    "end_time": "$END_TS",
    "elapsed_seconds": $ELAPSED,
    "exit_code": $EXIT_CODE
}
with open("/home/manas/yocto-build/build_summary.json", "w") as f:
    json.dump(data, f, indent=2)
PYEOF

exit $EXIT_CODE
