# V3 Metrics Provenance and Truth Audit

**Date**: 2026-11-19T06:55:00Z  
**Author**: Antigravity  
**Audit Standard**: Rule U2, Rule T1, Rule T2  
**Purpose**: Trace every metric in the V3 FINAL SUMMARY to its origin, identify synthetic/stale constants, and classify each metric as VERIFIED, STALE, or UNSUPPORTED.

---

## 1. Summary of Provenance Classifications

| Metric Claimed in V3 Final | Value | Classification | Provenance & Origin | Root Cause of Discrepancy |
| :--- | :---: | :---: | :--- | :--- |
| **Debian 12 Kernel Image** | 48.2 MB | **UNSUPPORTED** | Static constant in `bench/scripts/eval_baselines.py:34` | Hardcoded V1 estimate representing uncompressed `vmlinux`, never measured against a running Debian VM. |
| **Debian 12 Rootfs Payload** | 148.0 MB | **UNSUPPORTED** | Static constant in `bench/scripts/eval_baselines.py:30` | Hardcoded V1 estimate from `eval_baselines.py`. No Debian VM was booted. |
| **Debian 12 Idle RAM** | 215.0 MB | **UNSUPPORTED** | Static constant in `bench/scripts/eval_baselines.py:31` | Hardcoded V1 estimate from `eval_baselines.py`. |
| **Debian 12 Boot Time** | 3.82 s | **UNSUPPORTED** | Static constant in `bench/scripts/eval_baselines.py:32` | Hardcoded V1 estimate from `eval_baselines.py`. |
| **Lazy OS Kernel Image** | 5.91 MB | **VERIFIED** | `dist/bzImage` | Real binary on disk compiled via Buildroot (`6.6.21-lazy-os`), but compared uncompressed vs compressed against Debian. |
| **Lazy OS Rootfs Payload** | 38.00 MB | **STALE / MISLABELED** | `build/v2/lazy-os-boot.cpio.gz` | Real CPIO initramfs size, but violates O4 requirement for a read-only squashfs/erofs rootfs. |
| **Lazy OS Idle RAM** | 81.80 ± 3.42 MB | **STALE** | `bench/results/v2_baseline_comparison.csv` | Copied directly from V2 run (Linux 6.8 host kernel, 1024 MB RAM, 5 runs). Not measured on V3 custom kernel with 3072 MB RAM across 10 runs. |
| **Lazy OS Cold Boot Time** | 1.57 ± 0.96 s | **STALE** | `bench/results/v2_baseline_comparison.csv` | Copied directly from V2 run (5 runs). Not measured across 10 runs on V3. |
| **In-Guest LLM TTFT** | 78.18 ms | **VERIFIED (PARTIAL)** | `tests/results/acceptance/FT1_llm_metrics.json` | Real inference measurement with `llama.cpp` + `SmolLM2-360M`, but measured under 1024 MB RAM instead of 3072 MB RAM with median/p95. |
| **In-Guest LLM Throughput** | 97.90 tok/s | **VERIFIED (PARTIAL)** | `tests/results/acceptance/FT1_llm_metrics.json` | Real inference measurement with `llama.cpp` + `SmolLM2-360M`. |
| **Prompt Injection Defense** | 0 breaches / 70 attacks | **VERIFIED (SUBSET)** | `tests/assistant/injection.jsonl` | Evaluated against 70 attacks, but S1 contract requires $\ge 100$ attacks and $\ge 50$ benign queries. |
| **Security Score** | "10.00 / 10.0 = full isolation" | **UNSUPPORTED** | `scripts/generate_security_scores.py` | Inverted interpretation: `systemd-analyze security` measures exposure (0.0 = safe, 10.0 = unsafe). Furthermore, systemd was not PID 1. |
| **Installed Package Count** | 54 packages | **UNSUPPORTED** | Static constant in `bench/scripts/eval_baselines.py:44` | Hardcoded V1 constant from `eval_baselines.py`. |

---

## 2. Repository Search for Old Constants

A repository-wide grep for `148.0`, `215.0`, `3.82`, `38.0`, `48.2`, and `54` revealed:
1. **`bench/scripts/eval_baselines.py`**:
   - Lines 26–37 define `BASELINE_DATA` as a static dictionary containing:
     - `image_size_mb: 148.0`
     - `idle_ram_mb: 215.0`
     - `boot_time_s: 3.82`
     - `kernel_size_mb: 48.2`
     - `package_count: 224`
   - Lines 40–46 define `LAZY_BASE_DATA` as:
     - `image_size_mb: 38.0`
     - `idle_ram_mb: 74.0`
     - `boot_time_s: 0.94`
     - `kernel_size_mb: 19.6`
     - `package_count: 54`
2. **`bench/results/baseline_comparison.csv`**:
   - Exact mirror of the static dictionary from `eval_baselines.py`.
3. **`bench/scripts/eval_full_suite.py`**:
   - Hardcoded formulas computing percentage reductions using `(148.0 - 38.0) / 148.0` ($74.3\%$), `(215.0 - 74.0) / 215.0` ($65.6\%$), and `(3.82 - 0.94) / 3.82` ($75.4\%$).
4. **`docs/audit/CLAIMS.md` (V2 Audit)**:
   - Already documented that these numbers were unverified/fake in V1:
     > "Baseline values were hardcoded Python dictionary constants; no Debian 12 VM was booted or measured."
5. **V3 Final Summary Discrepancy**:
   - The V3 FINAL SUMMARY inadvertently revived the 148.0 MB, 215.0 MB, 3.82 s, and 48.2 MB constants in its summary table, directly violating Rule T1 and Rule U2.

---

## 3. Action Items for Remediation

1. **Delete / Mark Unsupported**:
   - All references to the 148.0, 215.0, 3.82, and 48.2 Debian constants are marked `UNSUPPORTED` until measured against a live Debian 12 VM in Milestone R7.
2. **Re-Measure Lazy OS**:
   - Measure 10 cold-boot runs of Lazy OS under 3072 MB guest RAM, recording both `used` and `MemTotal - MemAvailable`.
   - Measure kernel boot time vs userspace boot time.
3. **Like-for-Like Kernel Comparison**:
   - Compare compressed `bzImage` vs Debian compressed `vmlinuz`, and uncompressed `vmlinux` vs Debian uncompressed `vmlinux`.
4. **Systemd Security Audit**:
   - Re-run `systemd-analyze security` on real systemd units inside the guest, report exposure numbers with the correct scale (lower is better), and explain open capabilities.
