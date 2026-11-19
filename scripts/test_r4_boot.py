#!/usr/bin/env python3
"""Milestone R4: Test booting real read-only SquashFS root with volatile overlay and systemd."""

import subprocess
import time
import os
import sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
kernel = os.path.join(repo_root, "dist/bzImage")
initrd = os.path.join(repo_root, "build/v2/lazy-initramfs.cpio.gz")
disk = os.path.join(repo_root, "build/v2/lazy-disk.img")
out_log = os.path.join(repo_root, "tests/results/acceptance/R4_boot_state.log")

os.makedirs(os.path.dirname(out_log), exist_ok=True)

cmd = [
    "qemu-system-x86_64",
    "-m", "1024",
    "-smp", "2",
    "-kernel", kernel,
    "-initrd", initrd,
    "-drive", f"file={disk},format=raw,if=virtio",
    "-append", "console=ttyS0 panic=1 quiet",
    "-display", "none",
    "-serial", "stdio"
]

print(f"Launching QEMU: {' '.join(cmd)}")
p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

commands = [
    "echo '=== UNAME ==='",
    "uname -a",
    "echo '=== MOUNT_TABLE ==='",
    "mount",
    "echo '=== DF_H ==='",
    "df -h",
    "echo '=== TOUCH_ROOT_TESTFILE ==='",
    "touch /testfile 2>&1",
    "ls -la /testfile 2>&1",
    "echo '=== TOUCH_ETC_OVERLAY ==='",
    "touch /etc/volatile_test 2>&1",
    "ls -la /etc/volatile_test 2>&1",
    "echo '=== SYSTEMCTL_SERVICES ==='",
    "systemctl list-units 'lazy-*' --no-pager 2>&1",
    "echo '=== PS_SERVICES ==='",
    "ps -eo user,pid,comm 2>&1 | grep lazy || true",
    "echo '=== FREE_M ==='",
    "free -m",
    "echo '=== POWEROFF ==='",
    "poweroff -f 2>&1 || systemctl poweroff -ff 2>&1"
]

time.sleep(4)
script = "\n".join(commands) + "\n"

try:
    stdout, stderr = p.communicate(input=script, timeout=25)
except subprocess.TimeoutExpired:
    p.kill()
    stdout, stderr = p.communicate()

print(f"Captured {len(stdout)} bytes of guest output.")
with open(out_log, "w") as f:
    f.write("=== RAW GUEST OUTPUT (MILESTONE R4) ===\n")
    f.write(stdout)
    f.write("\n=== STDERR ===\n")
    f.write(stderr)

print(f"Wrote log to {out_log}")
print(stdout)
