#!/usr/bin/env python3
import os
from pathlib import Path

ROOTFS = Path("/mnt/c/Users/len/OS/build/v2/lazy-os-rootfs")
OUT = Path("/mnt/c/Users/len/OS/docs/academic/package_manifest.txt")
OUT.parent.mkdir(parents=True, exist_ok=True)

lines = []
lines.append("======================================================================")
lines.append("     LAZY OS v2 BOOTED IMAGE PACKAGE & COMPONENT MANIFEST             ")
lines.append("======================================================================")
lines.append(f"Rootfs Source: {ROOTFS}")
lines.append(f"Kernel Version: 6.8.0-149-generic")
lines.append("======================================================================\n")

# 1. Essential Binaries
lines.append("--- 1. SYSTEM BINARIES & UTILITIES ---")
for p in sorted(list((ROOTFS / "bin").glob("*")) + list((ROOTFS / "sbin").glob("*")) + list((ROOTFS / "usr/bin").glob("*"))):
    if p.is_file() or p.is_symlink():
        target = f" -> {os.readlink(p)}" if p.is_symlink() else f" ({p.stat().st_size} bytes)"
        lines.append(f"  {p.relative_to(ROOTFS).as_posix()}{target}")

# 2. Kernel Modules
lines.append("\n--- 2. IN-TREE KERNEL MODULES ---")
for p in sorted((ROOTFS / "lib/modules").glob("*.ko")):
    lines.append(f"  {p.name} ({round(p.stat().st_size/1024, 1)} KB)")

# 3. Dynamic Shared Libraries
lines.append("\n--- 3. SHARED LIBRARIES ---")
for p in sorted(list((ROOTFS / "lib").glob("*.so*")) + list((ROOTFS / "lib/x86_64-linux-gnu").glob("*.so*")) + list((ROOTFS / "lib64").glob("*.so*"))):
    if p.is_file() or p.is_symlink():
        lines.append(f"  {p.name}")

# 4. Python Environment & Site Packages
lines.append("\n--- 4. PYTHON DIST-PACKAGES & MODULES ---")
dist_pkg = ROOTFS / "usr/lib/python3/dist-packages"
if dist_pkg.exists():
    for p in sorted(dist_pkg.iterdir()):
        lines.append(f"  {p.name}")

# 5. Lazy OS Services & Components
lines.append("\n--- 5. LAZY OS CORE PACKAGES (src/lazy) ---")
lazy_pkg = dist_pkg / "lazy"
if lazy_pkg.exists():
    for p in sorted(lazy_pkg.iterdir()):
        if p.is_dir() and not p.name.startswith("__"):
            lines.append(f"  lazy.{p.name}")

# 6. Command Center Static HUD Assets
lines.append("\n--- 6. COMMAND CENTER SPA (hud/) ---")
hud_dir = ROOTFS / "usr/share/lazy/hud"
if hud_dir.exists():
    for p in sorted(hud_dir.iterdir()):
        lines.append(f"  {p.name} ({round(p.stat().st_size/1024, 1)} KB)")

OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"Generated {OUT} ({len(lines)} lines)")
