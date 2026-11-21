#!/usr/bin/env python3
import os
import sys
import glob
import time
import math
import json
import pexpect

DEPLOY_DIR = "/home/manas/yocto-build/build/tmp/deploy/images/qemux86-64"
OUT_DIR = "/mnt/c/Users/len/OS/bench/results/yocto_runs"
OUT_JSON = "/mnt/c/Users/len/OS/bench/results/yocto_metrics.json"

os.makedirs(OUT_DIR, exist_ok=True)

def find_artifacts():
    kernels = glob.glob(os.path.join(DEPLOY_DIR, "bzImage-qemux86-64.bin")) or glob.glob(os.path.join(DEPLOY_DIR, "bzImage"))
    if not kernels:
        kernels = glob.glob(os.path.join(DEPLOY_DIR, "bzImage*"))
        kernels = [k for k in kernels if not os.path.islink(k) and os.path.isfile(k) and not k.endswith(".bin")] or kernels
    kernel = os.path.realpath(kernels[0]) if kernels else None

    roots = glob.glob(os.path.join(DEPLOY_DIR, "lazy-image-base-qemux86-64.rootfs.ext4"))
    if not roots:
        roots = glob.glob(os.path.join(DEPLOY_DIR, "lazy-image-base-qemux86-64*.ext4"))
    rootfs = os.path.realpath(roots[0]) if roots else None

    manifests = glob.glob(os.path.join(DEPLOY_DIR, "lazy-image-base-qemux86-64.rootfs.manifest")) or glob.glob(os.path.join(DEPLOY_DIR, "*.manifest"))
    manifest = os.path.realpath(manifests[0]) if manifests else None

    return kernel, rootfs, manifest

def count_packages(manifest_path):
    if not manifest_path or not os.path.exists(manifest_path):
        return 0
    with open(manifest_path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]
    return len(lines)

def run_single_boot(kernel, rootfs, run_idx=1, is_sanity=False):
    qemu_cmd = (
        f"qemu-system-x86_64 -enable-kvm -cpu host -m 2048 -smp 2 -display none -serial stdio "
        f"-kernel {kernel} -drive file={rootfs},if=virtio,format=raw "
        f"-append \"root=/dev/vda rw console=ttyS0 quiet systemd.show_status=1\" "
        f"-no-reboot"
    )

    tag = "SANITY" if is_sanity else f"RUN {run_idx}"
    log_lines = [f"=== YOCTO STAGE A {tag} ==="]
    t0 = time.time()

    child = pexpect.spawn(qemu_cmd, encoding="utf-8", timeout=45)
    raw_output = ""

    boot_time_s = None
    mem_total_kb = None
    mem_avail_kb = None
    uname_str = ""
    systemd_state = ""

    try:
        idx = child.expect([r"qemux86-64 login:", r"login:", r"root@qemux86-64:~#", r"# ", pexpect.TIMEOUT, pexpect.EOF])
        t_prompt = time.time()
        boot_time_s = round(t_prompt - t0, 4)
        raw_output += child.before or ""
        raw_output += child.after if isinstance(child.after, str) else ""

        if idx in [0, 1]:
            child.sendline("root")
            child.expect([r"# ", r"root@.*:~#", pexpect.TIMEOUT])
            raw_output += child.before or ""

        # uname check
        child.sendline("uname -r")
        child.expect([r"# ", r"root@.*:~#", pexpect.TIMEOUT])
        lines = child.before.strip().splitlines() if child.before else []
        uname_str = lines[-1].strip() if lines else "6.6.x"
        raw_output += child.before or ""

        if is_sanity:
            child.sendline("systemctl is-system-running || true")
            child.expect([r"# ", r"root@.*:~#", pexpect.TIMEOUT])
            lines = child.before.strip().splitlines() if child.before else []
            systemd_state = lines[-1].strip() if lines else ""
            raw_output += child.before or ""

            child.sendline("btrfs --version; python3 --version; bash --version | head -n 1")
            child.expect([r"# ", r"root@.*:~#", pexpect.TIMEOUT])
            raw_output += child.before or ""

        # meminfo
        child.sendline("cat /proc/meminfo")
        child.expect([r"# ", r"root@.*:~#", pexpect.TIMEOUT])
        meminfo_text = child.before or ""
        raw_output += meminfo_text

        for line in meminfo_text.splitlines():
            if "MemTotal:" in line:
                mem_total_kb = float(line.split()[1])
            elif "MemAvailable:" in line:
                mem_avail_kb = float(line.split()[1])

        child.sendline("poweroff -f")
        child.expect([pexpect.EOF, pexpect.TIMEOUT], timeout=10)
        raw_output += child.before or ""
    except Exception as e:
        log_lines.append(f"Exception during run: {e}")
        try:
            child.close(force=True)
        except:
            pass

    mem_total_mb = round(mem_total_kb / 1024.0, 2) if mem_total_kb else None
    mem_avail_mb = round(mem_avail_kb / 1024.0, 2) if mem_avail_kb else None
    mem_used_mb = round(mem_total_mb - mem_avail_mb, 2) if (mem_total_mb and mem_avail_mb) else None

    log_lines.append(f"Measured Boot Time: {boot_time_s} s")
    log_lines.append(f"MemTotal: {mem_total_mb} MB, MemAvailable: {mem_avail_mb} MB, MemUsed: {mem_used_mb} MB")
    log_lines.append(f"\n=== RAW SERIAL OUTPUT ===\n{raw_output}")

    log_file = os.path.join(OUT_DIR, "sanity_run.log" if is_sanity else f"run_{run_idx}.log")
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

    return {
        "run": run_idx,
        "boot_time_s": boot_time_s,
        "mem_total_mb": mem_total_mb,
        "mem_available_mb": mem_avail_mb,
        "mem_used_mb": mem_used_mb,
        "kernel_release": uname_str,
        "systemd_state": systemd_state,
        "log_path": f"bench/results/yocto_runs/run_{run_idx}.log" if not is_sanity else "bench/results/yocto_runs/sanity_run.log"
    }

def main():
    kernel, rootfs, manifest = find_artifacts()
    print(f"Kernel:   {kernel}")
    print(f"Rootfs:   {rootfs}")
    print(f"Manifest: {manifest}")

    if not kernel or not rootfs:
        print("ERROR: Kernel or rootfs not found in deploy directory!")
        sys.exit(1)

    kernel_size_mb = round(os.path.getsize(kernel) / (1024.0 * 1024.0), 2)
    rootfs_size_mb = round(os.path.getsize(rootfs) / (1024.0 * 1024.0), 2)
    pkg_count = count_packages(manifest)

    print(f"Kernel Size: {kernel_size_mb} MB")
    print(f"Rootfs Size: {rootfs_size_mb} MB")
    print(f"Package Count: {pkg_count}")

    print("\n--- Running Sanity Boot (Checks 02-04) ---")
    sanity_res = run_single_boot(kernel, rootfs, run_idx=0, is_sanity=True)
    print(f"Sanity Boot Time: {sanity_res['boot_time_s']} s")
    print(f"Sanity Kernel: {sanity_res['kernel_release']}")
    print(f"Sanity RAM Used: {sanity_res['mem_used_mb']} MB")

    runs = []
    print("\n--- Running 10 Cold Boot Benchmark Runs ---")
    for i in range(1, 11):
        print(f"Executing Run {i}/10...")
        res = run_single_boot(kernel, rootfs, run_idx=i, is_sanity=False)
        runs.append(res)
        print(f"  Run {i}: Boot Time = {res['boot_time_s']} s, Idle RAM = {res['mem_used_mb']} MB")
        time.sleep(1)

    boot_times = [r["boot_time_s"] for r in runs if r["boot_time_s"] is not None]
    mem_used_list = [r["mem_used_mb"] for r in runs if r["mem_used_mb"] is not None]

    boot_mean = round(sum(boot_times) / len(boot_times), 2)
    boot_std = round(math.sqrt(sum((x - boot_mean) ** 2 for x in boot_times) / len(boot_times)), 2)

    mem_mean = round(sum(mem_used_list) / len(mem_used_list), 2)
    mem_std = round(math.sqrt(sum((x - mem_mean) ** 2 for x in mem_used_list) / len(mem_used_list)), 2)

    metrics = {
        "distribution": "Yocto Project (Poky 5.0 Scarthgap)",
        "target_image": "lazy-image-base",
        "machine": "qemux86-64",
        "kernel_version": runs[0].get("kernel_release", "6.6.x"),
        "runs_count": len(runs),
        "boot_time_mean_s": boot_mean,
        "boot_time_std_s": boot_std,
        "idle_ram_used_mean_mb": mem_mean,
        "idle_ram_used_std_mb": mem_std,
        "package_count": pkg_count,
        "kernel_image_mb": kernel_size_mb,
        "rootfs_installed_mb": rootfs_size_mb,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runs": runs
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"\nSuccessfully wrote metrics to {OUT_JSON}")
    print(f"Boot Time: {boot_mean} s (+/- {boot_std} s)")
    print(f"Idle RAM:  {mem_mean} MB (+/- {mem_std} MB)")
    print(f"Image Size: {rootfs_size_mb} MB")
    print(f"Packages:  {pkg_count}")

if __name__ == "__main__":
    main()
