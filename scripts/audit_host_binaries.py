#!/usr/bin/env python3
"""
Audit all binaries, libraries, and files in rootfs.squashfs / build/v2/lazy-os-rootfs.
Determine origin: (a) build system, (b) compiled kernel, or (c) host Ubuntu packages (dpkg -S).
"""
import os
import subprocess
import json

ROOTFS = "/mnt/c/Users/len/OS/build/v2/lazy-os-rootfs"

def audit_files():
    all_files = []
    for root, dirs, files in os.walk(ROOTFS):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, ROOTFS)
            # Find host path
            host_path = "/" + rel_path
            all_files.append((full_path, host_path, rel_path))

    print(f"Total files in rootfs: {len(all_files)}")
    
    # Check each file against dpkg -S
    host_packages = {}
    repo_files = []
    unmatched = []

    # Filter for ELF files or scripts
    elf_files = []
    for full_path, host_path, rel_path in all_files:
        try:
            with open(full_path, "rb") as fp:
                magic = fp.read(4)
                if magic == b"\x7fELF":
                    elf_files.append((full_path, host_path, rel_path))
        except Exception:
            pass

    print(f"Total ELF binaries and shared libraries: {len(elf_files)}")

    for full_path, host_path, rel_path in elf_files:
        # Check if it exists on host at host_path
        res = subprocess.run(["dpkg", "-S", host_path], capture_output=True, text=True)
        if res.returncode == 0:
            # Output format: "pkgname:arch: /path"
            out = res.stdout.strip().split("\n")[0]
            pkg = out.split(":")[0]
            # Get package version
            v_res = subprocess.run(["dpkg-query", "-W", "-f=${Version}", pkg], capture_output=True, text=True)
            ver = v_res.stdout.strip()
            host_packages[rel_path] = {
                "package": pkg,
                "version": ver,
                "host_path": host_path,
                "class": "(c) Host Ubuntu Binary"
            }
        else:
            # Maybe resolved via realpath on host
            real_host = os.path.realpath(host_path) if os.path.exists(host_path) else None
            if real_host and real_host != host_path:
                res2 = subprocess.run(["dpkg", "-S", real_host], capture_output=True, text=True)
                if res2.returncode == 0:
                    out = res2.stdout.strip().split("\n")[0]
                    pkg = out.split(":")[0]
                    v_res = subprocess.run(["dpkg-query", "-W", "-f=${Version}", pkg], capture_output=True, text=True)
                    ver = v_res.stdout.strip()
                    host_packages[rel_path] = {
                        "package": pkg,
                        "version": ver,
                        "host_path": real_host,
                        "class": "(c) Host Ubuntu Binary"
                    }
                    continue
            unmatched.append(rel_path)

    print(f"Matched host packages: {len(host_packages)}")
    print(f"Unmatched ELF files: {len(unmatched)}")
    for u in unmatched:
        print(f"  Unmatched: {u}")

    out_file = "/mnt/c/Users/len/OS/docs/audit/HOST_PACKAGES_IN_SQUASHFS.json"
    with open(out_file, "w") as fp:
        json.dump(host_packages, fp, indent=2)
    print(f"Saved package provenance JSON to {out_file}")

if __name__ == "__main__":
    audit_files()
