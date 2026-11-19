#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

host_bin = Path("/home/manas/lazy-build/output/host/bin")
target_rpath = "/home/manas/lazy-build/output/host/lib"
old_pattern = "/mnt/c/Users/len/OS/build/br2-output/host/lib"

if not host_bin.is_dir():
    print(f"Directory {host_bin} does not exist")
    exit(0)

for f in host_bin.iterdir():
    if not f.is_file() or f.is_symlink():
        continue
    res = subprocess.run(["readelf", "-d", str(f)], capture_output=True, text=True)
    if old_pattern in res.stdout:
        print(f"Patching {f.name}...")
        subprocess.run(["patchelf", "--set-rpath", target_rpath, str(f)], check=True)

print("RPATH patching completed successfully.")
