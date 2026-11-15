# Deck Input - Task 3: Custom Kernel Optimization & Sub-Second Boot

## Slide Metadata
- **Slide Title**: Custom Kernel Fragments: -59.3% Footprint, Sub-Second Boot
- **Topic**: Kernel Engineering, Security LSMs & Footprint Stripping
- **Time Allocation**: 2 Minutes

---

## Slide Content & Bullets

### 1. The Kernel Bloat Problem
- Stock enterprise kernels contain over 2,180 built-in drivers for mainframe storage, obsolete network cards, and virtualization overhead, resulting in 48.2 MB vmlinux images and 3.82s cold boot times.

### 2. Surgical Kconfig Fragments (`meta-lazy`)
1. **`base-minimal.cfg`**: Strips obsolete drivers, retains modern ACPI, PCIe, and SMP.
2. **`memory.cfg`**: Activates cgroup v2, zram swap compression, transparent huge pages (THP).
3. **`fs.cfg`**: Built-in support for SquashFS (read-only root), Btrfs (transactional undo), OverlayFS.
4. **`security.cfg`**: Hardens kernel with Landlock LSM, Seccomp BPF, KASLR, Yama ptrace restrictions.
5. **`laptop.cfg`**: Modular drivers for Intel/AMD backlight, RFKILL, CPUFreq governors, ALSA audio.

### 3. Empirical Results
- **Uncompressed vmlinux**: Reduced from 48.2 MB to **19.6 MB (-59.3%)**.
- **Kernel Modules Directory**: Reduced from 142.5 MB to **38.2 MB (-73.2%)**.
- **QEMU Cold Boot Time**: Dropped from 3.82 s to **0.94 s (-75.4%)**.

---

## Speaker Talking Points
1. "Instead of using a generic distribution kernel, we wrote 5 modular Kconfig fragments that BitBake compiles into the reference LTS kernel."
2. "Notice that every single Kconfig symbol was verified against the kernel configuration tree using our check script to ensure zero dropped options."
3. "Despite stripping over 1,500 symbols, we actually increased security: Landlock LSM and Seccomp BPF are built directly into the kernel binary, enabling unprivileged process sandboxing."

---

## Evidence & Verification References
- [yocto/meta-lazy/recipes-kernel/linux/files/](file:///c:/Users/len/OS/yocto/meta-lazy/recipes-kernel/linux/files/): The 5 custom Kconfig fragments.
- [bench/results/kernel_benchmark.csv](file:///c:/Users/len/OS/bench/results/kernel_benchmark.csv): Empirical kernel size and boot time benchmark.
- [tests/results/M5.1.log](file:///c:/Users/len/OS/tests/results/M5.1.log): Symbol verification and boot test logs.
