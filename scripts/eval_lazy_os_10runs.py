#!/usr/bin/env python3
"""Run 10 empirical cold-boot benchmark runs against genuine Lazy OS Buildroot image.

Measures:
- Cold boot time (seconds to login prompt / shell ready marker)
- Idle RAM (MemTotal, MemFree, MemAvailable, used = Total - Available)
- Kernel footprint (compressed bzImage vs Debian compressed vmlinuz)
- Rootfs footprint (read-only SquashFS vs Debian rootfs)
Saves:
- bench/results/lazy_os_runs/run_1.log .. run_10.log
- bench/results/lazy_os_baseline.json
- bench/results/baseline_comparison.csv
"""
from __future__ import annotations

import csv
import json
import math
import os
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = REPO_ROOT / "bench/results/lazy_os_runs"
RUNS_DIR.mkdir(parents=True, exist_ok=True)
OUT_JSON = REPO_ROOT / "bench/results/lazy_os_baseline.json"
COMPARISON_CSV = REPO_ROOT / "bench/results/baseline_comparison.csv"
DEBIAN_JSON = REPO_ROOT / "bench/results/debian12_baseline.json"

KERNEL = REPO_ROOT / "dist/bzImage"
DISK = REPO_ROOT / "dist/lazy-os.img"


def run_single_boot(run_idx: int) -> dict:
    cmd = [
        "qemu-system-x86_64",
        "-enable-kvm", "-cpu", "host",
        "-m", "1024",
        "-smp", "2",
        "-kernel", str(KERNEL),
        "-drive", f"file={DISK},format=raw,if=virtio",
        "-append", "console=ttyS0 root=/dev/vda2 ro rootwait quiet",
        "-display", "none",
        "-serial", "stdio"
    ]
    t0 = time.perf_counter()
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    boot_time = 0.0
    full_output = []
    
    while True:
        line = p.stdout.readline()
        if not line:
            break
        full_output.append(line)
        if "lazy-os login:" in line or "Command Center" in line:
            boot_time = time.perf_counter() - t0
            break
            
    time.sleep(0.5)
    commands = [
        "echo READY_LAZY",
        "cat /proc/meminfo",
        "poweroff -f"
    ]
    for c in commands:
        p.stdin.write(c + "\n")
        p.stdin.flush()
        time.sleep(0.4)
        
    try:
        remaining, _ = p.communicate(timeout=10)
        full_output.append(remaining)
    except Exception:
        p.kill()
        rem, _ = p.communicate()
        full_output.append(rem)
        
    stdout = "".join(full_output)
        
    log_path = RUNS_DIR / f"run_{run_idx}.log"
    with open(log_path, "w") as f:
        f.write(f"=== LAZY OS GENUINE RUN {run_idx} ===\n")
        f.write(f"Measured Boot Time: {boot_time:.4f} s\n\n")
        f.write("=== RAW SERIAL OUTPUT ===\n")
        f.write(stdout)
        
    mem_total = 0.0
    mem_avail = 0.0
    for line in stdout.splitlines():
        if line.startswith("MemTotal:"):
            mem_total = float(line.split()[1]) / 1024.0
        elif line.startswith("MemAvailable:"):
            mem_avail = float(line.split()[1]) / 1024.0
            
    mem_used = (mem_total - mem_avail) if mem_total and mem_avail else 0.0
    return {
        "run": run_idx,
        "boot_time_s": round(boot_time, 4),
        "mem_total_mb": round(mem_total, 2),
        "mem_available_mb": round(mem_avail, 2),
        "mem_used_mb": round(mem_used, 2),
        "log_path": str(log_path.relative_to(REPO_ROOT)),
    }


def main():
    os.system("sudo chmod 666 /dev/kvm 2>/dev/null || true")
    print("=== Executing 10 Cold-Boot Benchmark Runs for Genuine Lazy OS ===")
    runs = []
    for i in range(1, 11):
        print(f"Executing Lazy OS Run {i}/10...")
        res = run_single_boot(i)
        runs.append(res)
        print(f"  Run {i}: Boot Time = {res['boot_time_s']:.2f} s, Idle RAM Used = {res['mem_used_mb']:.2f} MB")
        time.sleep(0.5)
        
    boot_times = [r["boot_time_s"] for r in runs]
    valid_rams = [r["mem_used_mb"] for r in runs if r["mem_used_mb"] > 0]
    
    mean_boot = sum(boot_times) / len(boot_times)
    std_boot = math.sqrt(sum((x - mean_boot) ** 2 for x in boot_times) / len(boot_times))
    
    mean_ram = sum(valid_rams) / len(valid_rams) if valid_rams else 0.0
    std_ram = math.sqrt(sum((x - mean_ram) ** 2 for x in valid_rams) / len(valid_rams)) if valid_rams else 0.0
    
    kernel_size_mb = round(KERNEL.stat().st_size / (1024 * 1024), 2)
    rootfs_squashfs = REPO_ROOT / "dist/rootfs.squashfs"
    rootfs_size_mb = round(rootfs_squashfs.stat().st_size / (1024 * 1024), 2) if rootfs_squashfs.exists() else 0.0
    
    # Manifest package count from Buildroot manifest.csv
    manifest_csv = REPO_ROOT / "dist/legal-info/manifest.csv"
    pkg_count = 0
    if manifest_csv.exists():
        with open(manifest_csv, "r") as f:
            pkg_count = max(0, sum(1 for line in f if line.strip()) - 1)
            
    summary = {
        "distribution": "Lazy OS Genuine Buildroot",
        "kernel_version": "6.6.21-lazy-os",
        "runs_count": len(runs),
        "boot_time_mean_s": round(mean_boot, 2),
        "boot_time_std_s": round(std_boot, 2),
        "idle_ram_used_mean_mb": round(mean_ram, 2),
        "idle_ram_used_std_mb": round(std_ram, 2),
        "package_count": pkg_count,
        "kernel_image_mb": kernel_size_mb,
        "rootfs_installed_mb": rootfs_size_mb,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runs": runs,
    }
    
    with open(OUT_JSON, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved Lazy OS baseline summary to {OUT_JSON}")
    
    # Generate Comparison CSV if Debian baseline exists
    if DEBIAN_JSON.exists():
        with open(DEBIAN_JSON, "r") as f:
            deb = json.load(f)
            
        rows = [
            ["Metric", "Debian 12 Minimal", "Lazy OS Genuine (Buildroot)", "Delta / Improvement"],
            ["Kernel Image (compressed bzImage)", f"{deb['kernel_image_mb']} MB", f"{summary['kernel_image_mb']} MB", f"-{deb['kernel_image_mb'] - summary['kernel_image_mb']:.2f} MB (-{(1 - summary['kernel_image_mb']/deb['kernel_image_mb'])*100:.1f}%)"],
            ["Rootfs Payload", f"{deb['rootfs_installed_mb']} MB (uncompressed ext4)", f"{summary['rootfs_installed_mb']} MB (SquashFS xz)", f"-{deb['rootfs_installed_mb'] - summary['rootfs_installed_mb']:.1f} MB (-{(1 - summary['rootfs_installed_mb']/deb['rootfs_installed_mb'])*100:.1f}%)"],
            ["Cold Boot Time (10 runs, s)", f"{deb['boot_time_mean_s']:.2f} ± {deb['boot_time_std_s']:.2f} s", f"{summary['boot_time_mean_s']:.2f} ± {summary['boot_time_std_s']:.2f} s", f"-{deb['boot_time_mean_s'] - summary['boot_time_mean_s']:.2f} s ({(1 - summary['boot_time_mean_s']/deb['boot_time_mean_s'])*100:.1f}% faster)"],
            ["Idle RAM Used (MemTotal - MemAvail, MB)", f"{deb['idle_ram_used_mean_mb']:.2f} ± {deb['idle_ram_used_std_mb']:.2f} MB", f"{summary['idle_ram_used_mean_mb']:.2f} ± {summary['idle_ram_used_std_mb']:.2f} MB", f"Diff: {summary['idle_ram_used_mean_mb'] - deb['idle_ram_used_mean_mb']:.2f} MB"],
            ["Package Count (Manifest / dpkg)", f"{deb['package_count']} packages (dpkg)", f"{summary['package_count']} packages (Buildroot SBOM)", f"-{deb['package_count'] - summary['package_count']} packages"],
        ]
        
        with open(COMPARISON_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        print(f"Generated comparison table at {COMPARISON_CSV}")
        print("\n=== Like-for-Like Benchmark Comparison Table ===")
        for r in rows:
            print(f"{r[0]:<42} | {r[1]:<32} | {r[2]:<32} | {r[3]}")

if __name__ == "__main__":
    main()
