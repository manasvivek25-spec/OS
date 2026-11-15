#!/usr/bin/env python3
"""audit_repo.py - Collects all repo statistics for V2.A1 REPO_AUDIT.md
"""
import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def run_cmd(cmd):
    return subprocess.check_output(cmd, shell=True, text=True, cwd=REPO_ROOT).strip()

print("Branch:", run_cmd("git branch --show-current"))
print("Last Commit:", run_cmd("git log -1 --format='%H | %an | %ad | %s'"))
print("Commit Count:", run_cmd("git rev-list --count HEAD"))

print("\n--- Line counts per package in src/lazy ---")
lazy_dir = REPO_ROOT / "src/lazy"
total_lines = 0
for pkg in sorted(lazy_dir.iterdir()):
    if pkg.is_dir() and not pkg.name.startswith("__"):
        py_files = list(pkg.rglob("*.py"))
        pkg_lines = 0
        for f in py_files:
            try:
                pkg_lines += len(f.read_text(encoding="utf-8", errors="ignore").splitlines())
            except Exception:
                pass
        total_lines += pkg_lines
        print(f"  lazy.{pkg.name}: {len(py_files)} files, {pkg_lines} lines")
print(f"Total src/lazy Python lines: {total_lines}")

print("\n--- HUD Technology and Size ---")
hud_dir = REPO_ROOT / "hud"
hud_files = list(hud_dir.rglob("*"))
hud_size = 0
for f in hud_files:
    if f.is_file():
        hud_size += f.stat().st_size
        print(f"  {f.relative_to(REPO_ROOT)}: {f.stat().st_size} bytes")
print(f"Total HUD size: {hud_size} bytes")

print("\n--- Gateway routes and WebSocket messages ---")
gateway_dir = REPO_ROOT / "src/lazy/gateway"
for f in sorted(gateway_dir.glob("*.py")):
    lines = f.read_text(encoding="utf-8", errors="ignore").splitlines()
    for idx, l in enumerate(lines, 1):
        if any(kw in l for kw in ["@app.get", "@app.post", "@app.put", "@app.delete", "@app.websocket", "router.get", "router.post", "router.websocket", "self.send", "websocket.send", "ws.send"]):
            print(f"  {f.relative_to(REPO_ROOT)}:{idx}: {l.strip()}")
        elif "path ==" in l or "self.path" in l or "do_GET" in l or "do_POST" in l:
            print(f"  {f.relative_to(REPO_ROOT)}:{idx}: {l.strip()}")

print("\n--- QEMU and boot scripts in scripts/ ---")
scripts_dir = REPO_ROOT / "scripts"
for f in sorted(scripts_dir.glob("*")):
    if f.is_file():
        print(f"  {f.relative_to(REPO_ROOT)} ({f.stat().st_size} bytes)")

print("\n--- Yocto files ---")
for p in [REPO_ROOT / "yocto", REPO_ROOT / "meta-lazy"]:
    if p.exists():
        print(f"Directory {p.relative_to(REPO_ROOT)}:")
        for f in sorted(p.rglob("*")):
            if f.is_file():
                print(f"  {f.relative_to(REPO_ROOT)} ({f.stat().st_size} bytes)")
    else:
        print(f"Directory {p.name}: NOT FOUND")

print("\n--- Test Layout ---")
tests_dir = REPO_ROOT / "tests"
for d in sorted(tests_dir.iterdir()):
    if d.is_dir() and not d.name.startswith("__"):
        py_files = list(d.rglob("*.py"))
        print(f"  tests/{d.name}: {len(py_files)} test files")
