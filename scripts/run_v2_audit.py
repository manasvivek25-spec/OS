#!/usr/bin/env python3
"""run_v2_audit.py - Executes Phase A Runtime Audit (V2.A3)

Boots the existing Lazy OS artifacts in QEMU, captures the raw serial log,
executes all required audit inspection commands inside the guest,
saves each individual raw output to docs/audit/runtime/, and verifies
guest port identity from the host.
"""
import subprocess
import time
import sys
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AUDIT_DIR = REPO_ROOT / "docs/audit/runtime"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

KERNEL = "/boot/vmlinuz-6.8.0-149-generic"
INITRD = "/tmp/lazy-os-boot.cpio.gz"
DISK = "/tmp/lazy-disk.img"
FORWARD_PORT = 8768

print("=== Phase A Runtime Audit (V2.A3) ===")
print(f"Kernel: {KERNEL}")
print(f"Initrd: {INITRD}")
print(f"Disk:   {DISK}")

guest_commands = """
echo '=== BEGIN UNAME ==='
uname -a
echo '=== END UNAME ==='

echo '=== BEGIN CMDLINE ==='
cat /proc/cmdline
echo '=== END CMDLINE ==='

echo '=== BEGIN MOUNT ==='
mount
echo '=== END MOUNT ==='

echo '=== BEGIN FINDMNT ==='
if which findmnt >/dev/null 2>&1; then findmnt; else mount; fi
echo '=== END FINDMNT ==='

echo '=== BEGIN DF ==='
df -h
echo '=== END DF ==='

echo '=== BEGIN LSBLK ==='
lsblk
echo '=== END LSBLK ==='

echo '=== BEGIN FREE ==='
free -m
echo '=== END FREE ==='

echo '=== BEGIN PS ==='
ps -eo pid,rss,comm --sort=-rss 2>/dev/null || ps -o pid,comm
echo '=== END PS ==='

echo '=== BEGIN RUN_LAZY ==='
ls -la /run/lazy
echo '=== END RUN_LAZY ==='

echo '=== BEGIN SERVICES ==='
systemctl list-units --type=service
echo '--- PROCESS TABLE CHECK ---'
ps
echo '=== END SERVICES ==='

echo '=== BEGIN GATEWAY_IDENTITY ==='
cat /proc/sys/kernel/random/boot_id
cat /proc/version
echo '=== END GATEWAY_IDENTITY ==='

# Write proof file for host HTTP verification
boot_id=$(cat /proc/sys/kernel/random/boot_id)
mkdir -p /usr/share/lazy/hud
echo "LAZY_OS_BOOT_ID=$boot_id" > /usr/share/lazy/hud/guest_identity_proof.txt

echo '=== AUDIT SCRIPT COMPLETE ==='
sleep 3
poweroff -f
"""

AUDIT_DISK = "/tmp/lazy-disk-audit.img"
subprocess.run(["cp", DISK, AUDIT_DISK], check=True)

qemu_cmd = [
    "qemu-system-x86_64",
    "-enable-kvm",
    "-m", "1024",
    "-smp", "2",
    "-kernel", KERNEL,
    "-initrd", INITRD,
    "-drive", f"file={AUDIT_DISK},format=raw,if=virtio",
    "-append", "console=ttyS0 quiet panic=1 lazy_interactive=1",
    "-nographic",
    "-net", f"user,hostfwd=tcp::{FORWARD_PORT}-:8765",
    "-net", "nic,model=virtio",
    "-no-reboot"
]

print("Launching QEMU audit VM...")
exact_cmd_str = " ".join(qemu_cmd)
(AUDIT_DIR / "exact_launch_command.txt").write_text(exact_cmd_str + "\n")

proc = subprocess.Popen(
    qemu_cmd,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# Start thread to read output
serial_output = []
def reader():
    for line in proc.stdout:
        serial_output.append(line)
        sys.stdout.write(line)
        sys.stdout.flush()

import threading
t = threading.Thread(target=reader, daemon=True)
t.start()

# Feed commands
time.sleep(2.5)
proc.stdin.write(guest_commands)
proc.stdin.flush()

# Query guest identity from host via forwarded port before guest powers down
time.sleep(3.0)
host_proof = []
try:
    port_check = subprocess.check_output(f"ss -tulpn | grep {FORWARD_PORT}", shell=True, text=True)
    host_proof.append("=== HOST LISTENER CHECK ===")
    host_proof.append(port_check.strip())
except Exception as e:
    host_proof.append(f"Port check error: {e}")

try:
    import urllib.request
    url = f"http://127.0.0.1:{FORWARD_PORT}/guest_identity_proof.txt"
    with urllib.request.urlopen(url, timeout=3) as resp:
        body = resp.read().decode("utf-8")
        host_proof.append(f"=== GUEST HTTP RESPONSE FROM {url} ===")
        host_proof.append(body.strip())
        print(f"[OK] Host received guest identity proof: {body.strip()}")
except Exception as e:
    host_proof.append(f"HTTP request error: {e}")
    print(f"[WARN] HTTP proof request error: {e}")

(AUDIT_DIR / "host_port_proof.txt").write_text("\n".join(host_proof) + "\n")

# Give it time to execute and exit
proc.wait(timeout=30)
t.join(timeout=5)

raw_serial = "".join(serial_output)
(AUDIT_DIR / "serial_boot.log").write_text(raw_serial)
print(f"[OK] Full raw serial log written to {AUDIT_DIR / 'serial_boot.log'}")

# Extract sections
def extract_section(tag):
    start_tag = f"=== BEGIN {tag} ==="
    end_tag = f"=== END {tag} ==="
    if start_tag in raw_serial and end_tag in raw_serial:
        return raw_serial.split(start_tag)[1].split(end_tag)[0].strip()
    return "NOT_FOUND"

sections = {
    "uname.txt": extract_section("UNAME"),
    "cmdline.txt": extract_section("CMDLINE"),
    "mount.txt": extract_section("MOUNT"),
    "findmnt.txt": extract_section("FINDMNT"),
    "df.txt": extract_section("DF"),
    "lsblk.txt": extract_section("LSBLK"),
    "free.txt": extract_section("FREE"),
    "ps.txt": extract_section("PS"),
    "run_lazy.txt": extract_section("RUN_LAZY"),
    "services.txt": extract_section("SERVICES"),
    "gateway_identity.txt": extract_section("GATEWAY_IDENTITY"),
}

for fname, content in sections.items():
    (AUDIT_DIR / fname).write_text(content + "\n")
    print(f"  Saved {fname} ({len(content)} bytes)")

print("=== V2.A3 Runtime Audit Data Extraction Complete ===")
