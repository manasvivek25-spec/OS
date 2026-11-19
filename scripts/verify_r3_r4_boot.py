#!/usr/bin/env python3
"""Execute Milestone R3 and R4 verification against genuine dist/lazy-os.img."""

import subprocess
import time
import os
import sys

def main():
    os.system("sudo chmod 666 /dev/kvm 2>/dev/null || true")
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    kernel = os.path.join(repo_root, "dist/bzImage")
    disk = os.path.join(repo_root, "dist/lazy-os.img")
    r3_log = os.path.join(repo_root, "tests/results/acceptance/R3_boot_state.log")
    r4_log = os.path.join(repo_root, "tests/results/acceptance/R4_boot_state.log")
    
    os.makedirs(os.path.dirname(r3_log), exist_ok=True)
    
    cmd = [
        "qemu-system-x86_64",
        "-enable-kvm", "-cpu", "host",
        "-m", "2048", "-smp", "2",
        "-kernel", kernel,
        "-drive", f"file={disk},format=raw,if=virtio",
        "-append", "console=ttyS0 root=/dev/vda2 ro rootwait quiet",
        "-display", "none",
        "-serial", "stdio"
    ]
    
    print(f"Launching QEMU: {' '.join(cmd)}")
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    time.sleep(3.5)
    
    commands = [
        "echo '=== UNAME ==='",
        "uname -a",
        "echo '=== PROC_VERSION ==='",
        "cat /proc/version",
        "echo '=== PS_PID1 ==='",
        "ps -o pid,comm,user | grep ' 1 ' || ps -eo pid,comm,user | head -n 5",
        "echo '=== SYSTEMCTL_LAZY ==='",
        "systemctl list-units 'lazy-*' --no-pager",
        "echo '=== SYSTEMCTL_FAILED ==='",
        "systemctl --failed --no-pager",
        "echo '=== PS_LAZY_SERVICES ==='",
        "ps -eo user,pid,rss,comm | grep lazy || true",
        "echo '=== MOUNT_TABLE ==='",
        "mount",
        "echo '=== DF_H ==='",
        "df -h",
        "echo '=== TOUCH_ROOT_TESTFILE ==='",
        "touch /testfile 2>&1 || true",
        "ls -la /testfile 2>&1 || true",
        "echo '=== TOUCH_PERSISTENT_DATA ==='",
        "touch /data/r4_persist_test && ls -la /data/r4_persist_test",
        "echo '=== FREE_M ==='",
        "free -m",
        "echo '=== PROC_MEMINFO ==='",
        "cat /proc/meminfo | head -n 15",
        "echo '=== POWEROFF ==='",
        "poweroff -f"
    ]
    
    for c in commands:
        p.stdin.write(c + "\n")
        p.stdin.flush()
        time.sleep(0.4)
        
    try:
        out, _ = p.communicate(timeout=20)
    except subprocess.TimeoutExpired:
        p.kill()
        out, _ = p.communicate()
        
    print(f"Captured {len(out)} bytes of output.")
    with open(r3_log, "w") as f:
        f.write("=== RAW GUEST OUTPUT (MILESTONE R3 BOOT STATE) ===\n")
        f.write(out)
        
    with open(r4_log, "w") as f:
        f.write("=== RAW GUEST OUTPUT (MILESTONE R4 READ-ONLY ROOT & PERSISTENT DATA) ===\n")
        f.write(out)
        
    print(f"Saved R3 output to {r3_log}")
    print(f"Saved R4 output to {r4_log}")
    print("\n--- Summary of Guest Boot Output ---")
    print(out)

if __name__ == "__main__":
    main()
