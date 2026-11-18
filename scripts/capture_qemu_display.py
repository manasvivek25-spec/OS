#!/usr/bin/env python3
"""Captures screendump directly from QEMU monitor socket and converts to PNG."""
import os
import socket
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOCK_PATH = "/tmp/lazy-qemu-monitor.sock"
PPM_PATH = "/tmp/lazy_screendump.ppm"
PNG_PATH = REPO_ROOT / "tests/results/acceptance/P1_screendump.png"


def capture_screendump():
    if not os.path.exists(SOCK_PATH):
        print(f"Error: QEMU monitor socket {SOCK_PATH} does not exist")
        return False

    # Connect to QEMU monitor Unix socket
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        s.connect(SOCK_PATH)
        # Read greeting banner
        time.sleep(0.2)
        s.recv(1024)

        # Issue screendump command
        cmd = f"screendump {PPM_PATH}\n".encode("utf-8")
        s.sendall(cmd)
        time.sleep(0.8)
        s.close()
    except Exception as e:
        print(f"Failed to communicate with QEMU monitor: {e}")
        return False

    if not os.path.exists(PPM_PATH):
        print(f"Error: PPM file {PPM_PATH} not generated")
        return False

    ppm_size = os.path.getsize(PPM_PATH)
    print(f"PPM screendump captured: {PPM_PATH} ({ppm_size} bytes)")

    # Convert to PNG via pnmtopng
    try:
        PNG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(PNG_PATH, "wb") as out_png:
            subprocess.run(["pnmtopng", PPM_PATH], stdout=out_png, check=True)
        print(f"Converted to PNG: {PNG_PATH} ({PNG_PATH.stat().st_size} bytes)")
        return True
    except Exception as e:
        print(f"Conversion via pnmtopng failed: {e}")
        return False


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(line_buffering=True)
    ok = capture_screendump()
    sys.exit(0 if ok else 1)
