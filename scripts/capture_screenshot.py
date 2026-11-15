#!/usr/bin/env python3
"""capture_screenshot.py - Captures live framebuffer screenshot from QEMU monitor.
"""
import socket
import time
import subprocess
import sys
from pathlib import Path

MONITOR_SOCK = "/tmp/qemu-monitor.sock"
PPM_PATH = "/tmp/lazy_os_screen.ppm"
PNG_DIR = Path("/mnt/c/Users/len/OS/docs/screenshots")
PNG_DIR.mkdir(parents=True, exist_ok=True)
PNG_PATH = PNG_DIR / "lazy_os_guest_screen.png"
ARTIFACT_PNG = Path("/mnt/c/Users/len/.gemini/antigravity/brain/9e8c7043-33d9-4a95-b40b-11e2da524dc0/lazy_os_guest_screen.png")

if not Path(MONITOR_SOCK).exists():
    print(f"ERROR: QEMU monitor socket {MONITOR_SOCK} not found.")
    sys.exit(1)

try:
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(MONITOR_SOCK)
    # Read initial greeting
    s.settimeout(2.0)
    try:
        s.recv(1024)
    except Exception:
        pass
    
    # Send screendump command
    s.sendall(f"screendump {PPM_PATH}\n".encode("utf-8"))
    time.sleep(1.0)
    s.close()
    
    if Path(PPM_PATH).exists():
        subprocess.run(f"pnmtopng {PPM_PATH} > {PNG_PATH}", shell=True, check=True)
        if ARTIFACT_PNG.parent.exists():
            subprocess.run(f"cp {PNG_PATH} {ARTIFACT_PNG}", shell=True, check=True)
        print(f"[OK] Screenshot captured: {PNG_PATH} ({PNG_PATH.stat().st_size} bytes)")
    else:
        print("ERROR: screendump did not generate PPM file.")
        sys.exit(1)
except Exception as e:
    print(f"ERROR capturing screenshot: {e}")
    sys.exit(1)
