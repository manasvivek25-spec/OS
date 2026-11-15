#!/usr/bin/env python3
"""verify_api_curl_proof.py - Boots V2 image in QEMU and executes real host-side
curl requests against /api/identity and /api/build-info.
"""
import subprocess
import time
import urllib.request
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BUILD_V2 = REPO_ROOT / "build/v2"
KERNEL = "/boot/vmlinuz-6.8.0-149-generic"
INITRD = str(BUILD_V2 / "lazy-os-boot.cpio.gz")
DISK = str(BUILD_V2 / "lazy-disk.img")
PORT = 8769

print("=== Booting V2 Image for In-Guest API Verification ===")
qemu_cmd = [
    "qemu-system-x86_64",
    "-enable-kvm",
    "-m", "1024",
    "-smp", "2",
    "-kernel", KERNEL,
    "-initrd", INITRD,
    "-drive", f"file={DISK},format=raw,if=virtio",
    "-append", "console=ttyS0 quiet panic=1 lazy_interactive=1",
    "-nographic",
    "-net", f"user,hostfwd=tcp::{PORT}-:8765",
    "-net", "nic,model=virtio",
    "-no-reboot"
]

proc = subprocess.Popen(
    qemu_cmd,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

time.sleep(3.0)

# Request /api/identity
identity_url = f"http://127.0.0.1:{PORT}/api/identity"
print(f"Requesting {identity_url}...")
identity_data = None
try:
    with urllib.request.urlopen(identity_url, timeout=5) as resp:
        body = resp.read().decode("utf-8")
        identity_data = json.loads(body)
        print("[OK] /api/identity response:\n", json.dumps(identity_data, indent=2))
        (REPO_ROOT / "docs/audit/api_identity_proof.json").write_text(json.dumps(identity_data, indent=2) + "\n")
except Exception as e:
    print(f"ERROR querying identity: {e}")

# Request /api/build-info
build_info_url = f"http://127.0.0.1:{PORT}/api/build-info"
print(f"\nRequesting {build_info_url}...")
build_info_data = None
try:
    with urllib.request.urlopen(build_info_url, timeout=5) as resp:
        body = resp.read().decode("utf-8")
        build_info_data = json.loads(body)
        print("[OK] /api/build-info response:\n", json.dumps(build_info_data, indent=2))
        (REPO_ROOT / "docs/audit/api_build_info_proof.json").write_text(json.dumps(build_info_data, indent=2) + "\n")
except Exception as e:
    print(f"ERROR querying build-info: {e}")

# Shut down VM
proc.stdin.write("poweroff -f\n")
proc.stdin.flush()
proc.wait(timeout=10)

print("\n=== In-Guest API Proof Complete ===")
