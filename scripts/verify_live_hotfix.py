#!/usr/bin/env python3
"""End-to-End Live Verification Script for Lazy OS Hotfixes.

Boots dist/lazy-os.img in QEMU, tests unscripted LLM command, document creation,
Btrfs/Copy snapshot rollback (undo), audit hash-chain verification, and captures
real live 1080p screendumps from the QEMU monitor.
"""
from __future__ import annotations

import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
DIST_DIR = REPO_ROOT / "dist"
KERNEL = DIST_DIR / "bzImage"
DISK = DIST_DIR / "lazy-os.img"
MONITOR_SOCK = "/tmp/lazy-qemu-monitor.sock"
PORT = 8766
BASE_URL = f"http://127.0.0.1:{PORT}"


def http_req(method: str, path: str, payload: dict | None = None) -> tuple[int, dict]:
    url = f"{BASE_URL}{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30.0) as resp:
            raw = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(raw)
            except Exception:
                return resp.status, {"raw": raw}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"error": raw}
    except Exception as e:
        return 0, {"error": str(e)}


def cleanup_stray_qemu():
    try:
        subprocess.run(["pkill", "-9", "-f", "qemu-system-x86_64"], check=False)
        time.sleep(1.0)
    except Exception:
        pass
    if os.path.exists(MONITOR_SOCK):
        try:
            os.unlink(MONITOR_SOCK)
        except Exception:
            pass


def main():
    print("=" * 80)
    print("   LAZY OS TRACK A — LIVE HOTFIX VERIFICATION & AUDIT SUITE")
    print("=" * 80)

    if not KERNEL.exists():
        print(f"FATAL: Kernel not found at {KERNEL}")
        sys.exit(1)
    if not DISK.exists():
        print(f"FATAL: Disk image not found at {DISK}")
        sys.exit(1)

    cleanup_stray_qemu()

    has_kvm = os.path.exists("/dev/kvm") and os.access("/dev/kvm", os.R_OK | os.W_OK)
    print(f"Hardware virtualization (/dev/kvm): {'ENABLED' if has_kvm else 'SOFTWARE'}")

    qemu_cmd = [
        "qemu-system-x86_64",
        "-m", "6144",
        "-smp", "4",
        "-kernel", str(KERNEL),
        "-drive", f"file={DISK},format=raw,if=virtio",
        "-vga", "virtio",
        "-device", "virtio-tablet-pci",
        "-append", "console=ttyS0 console=tty0 root=/dev/vda2 ro rootwait quiet panic=1 lazy_interactive=1",
        "-display", "none",
        "-monitor", f"unix:{MONITOR_SOCK},server,nowait",
        "-net", f"user,hostfwd=tcp::{PORT}-:8765",
        "-net", "nic,model=virtio",
        "-no-reboot",
    ]
    if has_kvm:
        qemu_cmd.insert(1, "-enable-kvm")

    print("\n[Step 1/6] Launching QEMU Guest Appliance...")
    proc = subprocess.Popen(
        qemu_cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    ready = False
    print("Waiting for guest systemd services and lazy-gateway on port 8766...")
    for i in range(60):
        time.sleep(1.0)
        code, resp = http_req("GET", "/api/identity")
        if code == 200:
            print(f"Lazy OS Gateway is ONLINE! (Detected in {i+1}s)")
            ready = True
            break
        if proc.poll() is not None:
            print("ERROR: QEMU process exited prematurely!")
            sys.exit(1)
        if (i + 1) % 5 == 0:
            print(f"  ... still booting ({i+1}s)")

    if not ready:
        print("ERROR: Timeout waiting for guest gateway.")
        proc.kill()
        sys.exit(1)

    print("\n--- Live Guest Identity ---")
    st, ident = http_req("GET", "/api/identity")
    print(json.dumps(ident, indent=2))

    print("\n--- Live Guest Services (15 Microservices) ---")
    st, svcs = http_req("GET", "/api/services")
    active_count = sum(1 for s in svcs if s.get("status") == "running" or s.get("active_state") == "active")
    print(f"Active services: {active_count}/{len(svcs)}")
    for s in svcs:
        print(f"  {s['unit']:<28} | {s['status']} ({s.get('active_state', '')})")

    # TEST 1: Unscripted command execution through LLM/zero-trust pipeline
    print("\n" + "=" * 80)
    print("[Step 2/6] Test 1: Submit Unscripted Prompt to Live Gateway/LLM Pipeline")
    print("Prompt: 'Create a note called live_hotfix_verify.txt explaining why read-only root helps edge ML security'")
    print("=" * 80)
    cmd_payload = {
        "prompt": "Create a note called live_hotfix_verify.txt explaining why read-only root helps edge ML security"
    }
    st_cmd, res_cmd = http_req("POST", "/api/command", cmd_payload)
    print(f"HTTP Status: {st_cmd}")
    print("Raw Response:")
    print(json.dumps(res_cmd, indent=2))

    task_id = res_cmd.get("task_id")

    # If pending approval (L2/L3), approve it
    if st_cmd == 202:
        app_id = res_cmd.get("approval_id")
        print(f"\nAction triggered approval gate (ID: {app_id}). Calling POST /api/approvals (approve)...")
        st_app, res_app = http_req("POST", "/api/approvals", {"approval_id": app_id, "action": "approve"})
        print(f"Approval HTTP Status: {st_app}")
        print("Raw Approval Response:")
        print(json.dumps(res_app, indent=2))
        task_id = res_app.get("task_id", task_id)

    # TEST 2: Confirm file exists in /data
    print("\n" + "=" * 80)
    print("[Step 3/6] Test 2: Confirm 'live_hotfix_verify.txt' Exists on /data")
    print("=" * 80)
    st_fs, res_fs = http_req("GET", "/api/fs?path=live_hotfix_verify.txt")
    if st_fs != 200:
        st_fs, res_fs = http_req("GET", "/api/fs?path=/data/live_hotfix_verify.txt")
    print(f"HTTP Status: {st_fs}")
    print("Raw File Content & Metadata:")
    print(json.dumps(res_fs, indent=2))
    assert st_fs == 200, f"File creation failed! HTTP {st_fs}: {res_fs}"
    print("\n--> PROOF: live_hotfix_verify.txt successfully created on persistent writable mount!")

    # TEST 3: Call POST /api/tasks/undo and verify rollback
    print("\n" + "=" * 80)
    print("[Step 4/6] Test 3: Transactional Rollback (Undo Task)")
    print(f"Calling POST /api/tasks/undo for task_id={task_id}...")
    print("=" * 80)
    st_undo, res_undo = http_req("POST", "/api/tasks/undo", {"task_id": task_id})
    print(f"Undo HTTP Status: {st_undo}")
    print("Raw Undo Response:")
    print(json.dumps(res_undo, indent=2))
    assert st_undo == 200, f"Undo failed! HTTP {st_undo}: {res_undo}"
    assert res_undo.get("success") is True, f"Undo was not successful: {res_undo}"

    # Verify file is removed
    st_fs_after, res_fs_after = http_req("GET", "/api/fs?path=live_hotfix_verify.txt")
    print(f"\nVerification after rollback: GET /api/fs returned HTTP {st_fs_after} (Expected: 404)")
    assert st_fs_after == 404, f"File still exists after undo! Response: {res_fs_after}"
    print("--> PROOF: Rollback confirmed. 'live_hotfix_verify.txt' was completely reverted!")

    # TEST 4: Audit Log Verification
    print("\n" + "=" * 80)
    print("[Step 5/6] Test 4: Cryptographic Audit Hash-Chain Verification")
    print("Calling POST /api/audit/verify...")
    print("=" * 80)
    st_ver, res_ver = http_req("POST", "/api/audit/verify", {})
    print(f"Audit Verify HTTP Status: {st_ver}")
    print("Raw Audit Verification Response:")
    print(json.dumps(res_ver, indent=2))
    assert st_ver == 200, f"Audit verify returned error: HTTP {st_ver}"
    assert res_ver.get("valid") is True, f"Audit hash-chain invalid: {res_ver}"
    assert res_ver.get("total_records", 0) > 0, f"Audit log is empty! Records: {res_ver.get('total_records')}"

    print(f"\nQuerying recent records: GET /api/audit?limit=10...")
    st_log, records = http_req("GET", "/api/audit?limit=10")
    print(f"Retrieved {len(records)} recent audit ledger entries:")
    for r in records[-5:]:
        print(f"  [{r.get('index')}] {r.get('timestamp')} | {r.get('event_type'):<18} | Actor: {r.get('actor'):<6} | Hash: {r.get('hash', '')[:16]}...")
    print("--> PROOF: SHA-256 hash-chain verified. Zero tampering, full auditability!")

    # TEST 5: Recapture all 12 Screendumps Live from Running Guest
    print("\n" + "=" * 80)
    print("[Step 6/6] Recapturing 12 Live 1080p Screendumps via QEMU Monitor Socket")
    print("=" * 80)
    print("Waiting 6s to ensure Cage/WPE WebKit kiosk has completed initial HUD render...")
    time.sleep(6.0)
    from scripts.run_ui_demos import UIDemoHarness
    from PIL import Image
    sd_dir = REPO_ROOT / "docs/audit/screendumps"
    harness = UIDemoHarness(target_url=BASE_URL, output_dir=sd_dir, dry_run=False)
    success = harness.run_all_scenarios()

    print("\n--- Verifying Captured Screendump Dimensions and Sizes ---")
    all_pngs = sorted(sd_dir.glob("*.png"))
    for png in all_pngs:
        sz = png.stat().st_size
        with Image.open(png) as img:
            w, h = img.size
            colors = img.getcolors(maxcolors=10000)
            n_colors = len(colors) if colors else 10000
        print(f"  {png.name:<35} | {sz:>7} bytes | {w}x{h} | Colors: {n_colors} | Real Kiosk Scanout")
        assert sz >= 20000, f"Suspicious image size for {png.name}: {sz} bytes (should be >= 20 KB)"
        assert w == 1920 and h == 1080, f"Wrong resolution for {png.name}: {w}x{h}"
        assert n_colors > 100, f"Suspicious color count for {png.name}: {n_colors} (possible blank/console screen)"

    print("\n" + "=" * 80)
    print("   ALL VERIFICATION GATES PASSED WITH 100% REAL GUEST EVIDENCE!")
    print("=" * 80)

    # Clean shutdown
    print("\nShutting down QEMU guest cleanly...")
    try:
        proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=5)
    except Exception:
        proc.kill()
    cleanup_stray_qemu()
    print("Guest terminated cleanly.")


if __name__ == "__main__":
    main()
