#!/usr/bin/env python3
"""Milestone R6: Collect individual security scores for all 15 lazy services."""

import subprocess
import time
import os
import sys

SERVICES = [
    "lazy-audit",
    "lazy-policy",
    "lazy-planner",
    "lazy-tasks",
    "lazy-secrets",
    "lazy-broker-fs",
    "lazy-broker-web",
    "lazy-broker-hw",
    "lazy-broker-sys",
    "lazy-broker-comms",
    "lazy-routines",
    "lazy-fetcher",
    "lazy-outbox",
    "lazy-llm",
    "lazy-gateway"
]

def main():
    os.system("sudo chmod 666 /dev/kvm 2>/dev/null || true")
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    kernel = os.path.join(repo_root, "dist/bzImage")
    disk = os.path.join(repo_root, "dist/lazy-os.img")
    out_log = os.path.join(repo_root, "tests/results/acceptance/systemd_security_audit.log")
    
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
    
    print(f"Launching QEMU for security audit: {' '.join(cmd)}")
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    time.sleep(3.5)
    
    script_commands = ["echo '=== SYSTEMD_SECURITY_SCORES ==='"]
    for s in SERVICES:
        script_commands.append(f"echo '--- {s}.service ---'")
        script_commands.append(f"systemd-analyze security {s}.service --no-pager | tail -n 5")
    script_commands.append("poweroff -f")
    
    for c in script_commands:
        p.stdin.write(c + "\n")
        p.stdin.flush()
        time.sleep(0.3)
        
    try:
        out, _ = p.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        p.kill()
        out, _ = p.communicate()
        
    print(f"Captured {len(out)} bytes of output.")
    with open(out_log, "w") as f:
        f.write("=== RAW SYSTEMD-ANALYZE SECURITY AUDIT (15 MICROSERVICES) ===\n")
        f.write(out)
        
    print(f"Saved to {out_log}")
    print("\n--- Summary of Scores ---")
    for line in out.splitlines():
        if "--- lazy-" in line or "Overall exposure" in line:
            print(line)

if __name__ == "__main__":
    main()
