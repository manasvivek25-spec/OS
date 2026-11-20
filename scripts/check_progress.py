#!/usr/bin/env python3
import os
import glob
import subprocess

log_file = "/mnt/c/Users/len/OS/build-logs/kiosk-build.log"
build_dir = "/home/manas/lazy-build/output/build"

# Targets in build
target_installed = len(glob.glob(os.path.join(build_dir, "*", ".stamp_target_installed")))
staging_installed = len(glob.glob(os.path.join(build_dir, "*", ".stamp_staging_installed")))
host_installed = len(glob.glob(os.path.join(build_dir, "host-*", ".stamp_host_installed")))

# Total target packages from defconfig
total_target_pkgs = 58  # 40 original + 18 kiosk & deps

# Last lines from log
last_lines = []
if os.path.exists(log_file):
    with open(log_file, "r", errors="ignore") as f:
        lines = f.readlines()
        last_lines = [l.strip() for l in lines if l.strip()]

curr_pkg = "host-icu"
curr_action = "Downloading / Compiling"
for l in reversed(last_lines):
    if l.startswith(">>>"):
        parts = l.split()
        if len(parts) >= 3:
            curr_pkg = parts[1]
            curr_action = " ".join(parts[2:])
            break

# Get last download line if any
last_pct = ""
for l in reversed(last_lines):
    if "%" in l:
        parts = l.split()
        for p in parts:
            if p.endswith("%"):
                last_pct = p
                break
        if last_pct:
            break

print(f"TARGET_INSTALLED={target_installed}")
print(f"STAGING_INSTALLED={staging_installed}")
print(f"HOST_INSTALLED={host_installed}")
print(f"CURRENT_PACKAGE={curr_pkg}")
print(f"CURRENT_ACTION={curr_action}")
print(f"DOWNLOAD_PCT={last_pct}")
