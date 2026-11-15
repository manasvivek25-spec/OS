# Lazy OS Empirical Benchmark Methodology (V2.B4)

**Document Version:** 2.0 (Strict Empirical Compliance)  
**Date:** 2026-11-16T01:36:00+05:30  
**Authors:** Antigravity Autonomous Systems Engineering Team

---

## 1. Standardization & Like-for-Like Definitions

To ensure academic rigor, all benchmarks between stock distributions and Lazy OS must share identical measurement boundaries:

### A. Boot Time
- **Start Point:** Timestamp of QEMU hypervisor process start ($t_0$).
- **Kernel & Initramfs Handover ($t_1$):** Timestamp when the Linux kernel completes initialization and transfers execution to `/init` userspace.
- **Ready Marker ($t_2$):** Timestamp when the userspace init script reaches the primary interactive readiness marker:
  - For Lazy OS: The `/init` shell prints `[OK] Gateway & REST API listening on 0.0.0.0:8765`.
  - For Stock Linux (Debian): `systemd-analyze` reaches `startup finished in ... (kernel) + ... (userspace) = ...s (graphical.target or multi-user.target)`.
- **Metrics Recorded:**
  - $\Delta t_{\text{kernel}} = t_1 - t_0$ (Kernel + decompression time)
  - $\Delta t_{\text{userspace}} = t_2 - t_1$ (Userspace service initialization)
  - $\Delta t_{\text{total}} = t_2 - t_0$ (Total cold boot time to ready)

### B. Idle RAM Utilization
- **Hypervisor Allocation:** 1,024 MB virtual RAM (`-m 1024`), 2 virtual CPUs (`-smp 2`).
- **Settling Window:** System settles for 60 seconds with zero network or user input.
- **Measurement Tool:** `free -m` inside the guest.
- **Value Captured:** The `used` column (RAM actively reserved by kernel, resident daemons, and cgroups, excluding buffers/cache).

### C. Distribution Footprint & Payload Size
- **Total Bootable Payload Size:**
  - The aggregate byte count of all artifacts required to cold-boot the operating system:
    $$\text{Size}_{\text{bootable}} = \text{Size}(\text{kernel}) + \text{Size}(\text{modules}) + \text{Size}(\text{initramfs}) + \text{Size}(\text{rootfs})$$
- **Root Filesystem Only:**
  - Uncompressed root filesystem size on disk (`du -sb`).

### D. Installed Package Count
- **Stock Linux (Debian):** Query package management database (`dpkg-query -f '${binary:Package}\n' -W | wc -l`).
- **Lazy OS:** Total number of functional packages / recipes deployed in the image manifest.

---

## 2. Multi-Run Statistical Protocol
- **Sample Size:** 5 independent cold boots per system ($N=5$).
- **Statistical Measures:** Mean ($\mu$) and Sample Standard Deviation ($\sigma$):
  $$\mu = \frac{1}{N}\sum_{i=1}^N x_i, \quad \sigma = \sqrt{\frac{1}{N-1}\sum_{i=1}^N (x_i - \mu)^2}$$
- **Data Capture:** All raw serial console outputs and timestamp logs must be archived in `bench/results/v2_runs/`.

---

## 3. Stock Baseline Availability Declaration
- If a stock Debian 12 minimal image is not present on the host or cannot be instantiated with identical hypervisor flags, it is explicitly classified as **Not Measured**, rather than populated with synthetic estimates.
