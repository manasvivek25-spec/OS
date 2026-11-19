#!/usr/bin/env python3
import subprocess
import time
import os
import sys

def main():
    os.system("sudo chmod 666 /dev/kvm 2>/dev/null")
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    kernel = os.path.join(repo_root, "dist/bzImage")
    disk = os.path.join(repo_root, "dist/lazy-os.img")
    
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
    
    time.sleep(1)
    if p.poll() is not None:
        out, _ = p.communicate()
        print("QEMU exited immediately with code", p.returncode)
        print("Output was:\n", out)
        return
    p.stdin.write("root\n")
    p.stdin.flush()
    time.sleep(1)
    
    time.sleep(3)
    commands = [
        "ls -la /etc/lazy",
        "ls -la /etc/lazy/capabilities | head -n 5",
        "su -s /bin/sh lazy-gw -c 'ls -la /etc/lazy/capabilities | head -n 5'",
        "su -s /bin/sh lazy-gw -c \"python3 -c 'from lazy.policy.manifest import ManifestLoader; m = ManifestLoader(); print(\\\"LOADER DIRS:\\\", m.manifest_dirs); print(\\\"CAPS:\\\", m.list_capabilities())'\"",
        "poweroff -f"
    ]
    for c in commands:
        p.stdin.write(c + "\n")
        p.stdin.flush()
        time.sleep(1)
        
    try:
        out, _ = p.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        p.kill()
        out, _ = p.communicate()
        
    print("=== QEMU OUTPUT ===")
    print(out)

if __name__ == "__main__":
    main()
