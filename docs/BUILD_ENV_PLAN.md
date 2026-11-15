# Lazy OS Build Environment & Cloud Migration Plan

**Document Status**: Human Action Required (Resource Gate Enforced)  
**Measured Local Host Resources**:
- **Total Physical Memory**: 11.5 GB (11,814 MB total, ~10.5 GB available)
- **Swap**: 3.0 GB
- **Virtual Disk**: 952 GB Available (`/dev/sdd` on ext4)
- **vCPUs**: 16 cores

> [!WARNING]
> **Resource Gate**: Rule V2.E1 strictly prohibits initiating a native BitBake compilation unless WSL2 has at least **16 GB RAM** available. Compiling full toolchains (`gcc-cross`, `glibc`, `python3-native`) with 11.5 GB RAM triggers Out-Of-Memory (OOM) kernel kills during link phases.
> 
> Therefore, this milestone is marked **HUMAN ACTION REQUIRED**. Three supported options are detailed below to complete native BitBake compilation.

---

## Option A: Recommended Cloud VM Runbook (Fastest, Cleanest)

For academic evaluation or continuous integration, compile the native Yocto distribution on a dedicated cloud instance:

### 1. Instance Specification
- **AWS**: `c6i.4xlarge` (16 vCPUs, 32 GB RAM, 150 GB gp3 SSD)
- **GCP**: `c2-standard-16` (16 vCPUs, 32 GB RAM, 150 GB pd-balanced SSD)
- **Azure**: `Standard_D16s_v5` (16 vCPUs, 32 GB RAM, 150 GB Premium SSD)
- **OS Image**: Ubuntu 22.04 LTS (Jammy Jellyfish)

### 2. Execution Runbook
```bash
# 1. Update and install Yocto host prerequisites
sudo apt-get update && sudo apt-get install -y \
    gawk wget git diffstat unzip texinfo gcc build-essential \
    chrpath socat cpio python3 python3-pip python3-pexpect \
    xz-utils debianutils iputils-ping python3-git python3-jinja2 \
    libegl1-mesa libsdl1.2-dev pylint xterm python3-subunit \
    mesa-common-dev zstd liblz4-tool git-lfs

# 2. Install kas build tool
pip3 install kas

# 3. Clone Lazy OS repository
git clone https://github.com/manas/lazy-os.git
cd lazy-os

# 4. Run native BitBake build via Kas
kas build yocto/kas.yml

# 5. Locate generated bootable artifacts
ls -lh build/tmp/deploy/images/qemux86-64/
# Output contains:
# - bzImage (compiled custom kernel)
# - lazy-image-base-qemux86-64.rootfs.wic
# - lazy-image-base-qemux86-64.rootfs.cpio.gz
```

---

## Option B: Expanding Local Windows Host WSL2 Resources

If the Windows host machine has $\ge 32$ GB of physical RAM:

1. Open `%USERPROFILE%\.wslconfig` in Windows (e.g. `C:\Users\len\.wslconfig`).
2. Add or modify the `[wsl2]` section:
   ```ini
   [wsl2]
   memory=24GB
   processors=16
   swap=16GB
   localhostForwarding=true
   ```
3. Restart WSL from PowerShell:
   ```powershell
   wsl --shutdown
   ```
4. Verify new memory allocation in WSL:
   ```bash
   free -m
   ```
5. Once memory exceeds 16 GB, proceed with `kas build yocto/kas.yml`.

---

## Option C: Accelerating with Upstream Sstate Mirrors & DL_DIR

To reduce compilation time from ~4 hours to under 30 minutes, configure shared state caching in `yocto/meta-lazy/conf/layer.conf` or `build/conf/local.conf`:

```bitbake
# Use Yocto project pre-built binary cache
SSTATE_MIRRORS ?= "\
file://.* http://sstate.yoctoproject.org/4.0.12/PATH;downloadfilename=PATH \
file://.* http://sstate.yoctoproject.org/all/PATH;downloadfilename=PATH"

# Persist download cache
DL_DIR ?= "${TOPDIR}/../downloads"
```

---

## Summary of Fast Development vs. Native Yocto Builds

| Dimension | Fast Development Path (Current Verified V2 Image) | Native Yocto BitBake Path (Option A/B) |
| :--- | :--- | :--- |
| **Kernel Used** | In-tree Host Ubuntu generic kernel (`vmlinuz-6.8.0-149-generic`) | Custom compiled Yocto `linux-yocto` kernel |
| **Init System** | BusyBox static init with modular in-guest Python daemons | systemd compiled from source via Yocto recipes |
| **Storage Engine** | In-tree Btrfs module with formatted 128 MB raw partition | `meta-lazy` WIC partition layout with Btrfs |
| **Build Time** | **< 30 seconds** | **~2.5 to 4 hours** (from scratch) |
| **Host Requirements**| 1 GB RAM, 2 GB disk | 16–32 GB RAM, 120 GB disk |
| **Status in Repo** | **100% Bootable, Tested, Verified** | Layer metadata, recipes & Kas YAML ready |
