#!/usr/bin/env python3
"""Milestone R3: Boot dist/ and record raw guest output of system state."""

import subprocess
import time
import os
import sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
kernel = os.path.join(repo_root, "dist/bzImage")
initrd = os.path.join(repo_root, "build/v2/lazy-os-boot.cpio.gz")
disk = os.path.join(repo_root, "build/v2/lazy-disk.img")
out_log = os.path.join(repo_root, "tests/results/acceptance/R3_boot_state.log")

os.makedirs(os.path.dirname(out_log), exist_ok=True)

cmd = [
    "qemu-system-x86_64",
    "-m", "1024",
    "-smp", "2",
    "-kernel", kernel,
    "-initrd", initrd,
    "-drive", f"file={disk},format=raw,if=virtio",
    "-append", "console=ttyS0 panic=1 quiet lazy_interactive=1",
    "-display", "none",
    "-serial", "stdio"
]

print(f"Launching QEMU: {' '.join(cmd)}")
p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

commands = [
    "echo '=== UNAME ==='",
    "uname -a",
    "echo '=== PROC_VERSION ==='",
    "cat /proc/version",
    "echo '=== PS_PID_1 ==='",
    "ps -p 1",
    "echo '=== SYSTEMCTL_SERVICES ==='",
    "systemctl list-units 'lazy-*' 2>&1",
    "echo '=== PS_LAZY_SERVICES ==='",
    "ps -eo user,pid,rss,comm 2>&1",
    "echo '=== PS_ALL ==='",
    "ps 2>&1",
    "echo '=== FINDMNT ==='",
    "findmnt 2>&1",
    "echo '=== MOUNT ==='",
    "mount",
    "echo '=== DF_H ==='",
    "df -h",
    "echo '=== TOUCH_TESTFILE ==='",
    "touch /testfile 2>&1",
    "ls -la /testfile 2>&1",
    "echo '=== FREE_M ==='",
    "free -m",
    "echo '=== PROC_MEMINFO ==='",
    "head -n 15 /proc/meminfo",
    "echo '=== POWEROFF ==='",
    "poweroff -f"
]

# Wait for guest init to start
time.sleep(3)
script = "\n".join(commands) + "\n"

try:
    stdout, stderr = p.communicate(input=script, timeout=25)
except subprocess.TimeoutExpired:
    p.kill()
    stdout, stderr = p.communicate()

print(f"Captured {len(stdout)} bytes of guest output.")
with open(out_log, "w") as f:
    f.write("=== RAW GUEST OUTPUT (MILESTONE R3) ===\n")
    f.write(stdout)
    f.write("\n=== STDERR ===\n")
    f.write(stderr)

print(f"Wrote log to {out_log}")
print(stdout)
