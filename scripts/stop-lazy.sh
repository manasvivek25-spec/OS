#!/usr/bin/env bash
# Lazy OS v2 Stop Script
# Gracefully terminates the running Lazy OS QEMU instance.

set -euo pipefail

PID_FILE="/tmp/lazy-os.pid"
MONITOR_SOCK="/tmp/lazy-qemu-monitor.sock"

if [ ! -f "${PID_FILE}" ]; then
    echo "Lazy OS is not running (no PID file found at ${PID_FILE})."
    # Check if any stray QEMU processes exist
    STRAYS=$(pgrep -f "lazy-os-boot.cpio.gz" || true)
    if [ -n "${STRAYS}" ]; then
        echo "Found orphaned QEMU process(es): ${STRAYS}. Terminating..."
        kill -15 ${STRAYS} 2>/dev/null || true
    fi
    exit 0
fi

PID=$(cat "${PID_FILE}")

if ! kill -0 "${PID}" 2>/dev/null; then
    echo "Process ${PID} not running. Removing stale PID file."
    rm -f "${PID_FILE}"
    exit 0
fi

echo "Stopping Lazy OS (PID: ${PID})..."

# Send SIGTERM
kill -15 "${PID}" 2>/dev/null || true

# Wait up to 5 seconds
STOPPED=0
for i in $(seq 1 10); do
    if ! kill -0 "${PID}" 2>/dev/null; then
        STOPPED=1
        break
    fi
    sleep 0.5
done

if [ "${STOPPED}" -eq 0 ]; then
    echo "Process did not stop gracefully. Sending SIGKILL..."
    kill -9 "${PID}" 2>/dev/null || true
fi

rm -f "${PID_FILE}" "${MONITOR_SOCK}"
echo "Lazy OS stopped successfully."
