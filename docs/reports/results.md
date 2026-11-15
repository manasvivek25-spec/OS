# Lazy OS Comprehensive Evaluation & Benchmark Results (V2 Corrected)

> [!NOTE]
> **Audit & Correction Statement (Rule T1 / V2.B4)**:
> In the V1 report, comparison figures for Stock Debian 12 Minimal (148 MB image, 215 MB RAM, 3.82s boot) and Lazy OS Base (38 MB image, 74 MB RAM, 0.94s boot) were derived from static modeling scripts rather than direct empirical measurements of a booted Debian VM.
> Below are the audited, empirically measured metrics from 5 cold-boot runs executed in QEMU (Linux 6.8 kernel, KVM, 1024 MB RAM) per [`bench/METHOD.md`](file:///c:/Users/len/OS/bench/METHOD.md). The original V1 claims are preserved in [`docs/archive/results.v1.md`](file:///c:/Users/len/OS/docs/archive/results.v1.md) for full traceability.

---

## 1. Audited Multi-Run Benchmarks (N=5 Runs)

*Source: [`bench/results/v2_baseline_comparison.csv`](file:///c:/Users/len/OS/bench/results/v2_baseline_comparison.csv), raw logs in [`bench/results/v2_runs/`](file:///c:/Users/len/OS/bench/results/v2_runs/)*

| Metric | Stock Debian 12 Minimal | Lazy OS V2 Base (Empirical $\mu \pm \sigma$) | V1 Claimed (Synthetic) | Measurement Methodology & Notes |
| :--- | :---: | :---: | :---: | :--- |
| **Bootable Payload Size** | *Not Measured* | **39.75 MB** | 38.0 MB | Kernel (14.41 MB) + Initramfs with Btrfs modules (25.34 MB) |
| **Uncompressed Rootfs** | *Not Measured* | **84.00 MB** | — | Total unpacked root filesystem on disk (`du -sm`) |
| **Idle RAM Footprint** | *Not Measured* | **81.80 ± 3.42 MB** | 74.0 MB | `free -m` used memory after cold boot and daemon startup |
| **Cold Boot Time** | *Not Measured* | **1.57 ± 0.96 s** | 0.94 s | Measured from QEMU start to `Gateway & REST API listening` |
| **Active Capabilities**| *Not Measured* | **37 capabilities** | 54 packages | Formally specified capability manifests in `config/capabilities` |
| **Data Partition Storage**| — | **Persistent Btrfs** | *Simulated tmpfs* | Real block device `/dev/vda3` (128 MB) formatted with Btrfs |

$$\mu_{\text{boot}} = 1.57\,\text{s}, \quad \sigma_{\text{boot}} = 0.96\,\text{s}$$
$$\mu_{\text{RAM}} = 81.80\,\text{MB}, \quad \sigma_{\text{RAM}} = 3.42\,\text{MB}$$

### Explanation of Discrepancies (V1 vs. V2):
1. **Debian 12 Status:** A live Debian 12 minimal VM image was unprovisioned on the local host. In compliance with Rule T1, it is recorded as *Not Measured* rather than populated with assumed numbers.
2. **Idle RAM Increase (74.0 MB $\to$ 81.8 MB):** In V2.B1, real in-tree Linux kernel modules for Btrfs (`btrfs.ko`, `raid6_pq.ko`, `xor.ko`, `libcrc32c.ko`) and real `findmnt`/`lsblk` libraries were loaded into memory, slightly increasing the resident kernel memory footprint while delivering genuine filesystem persistence across reboots.
3. **Boot Time Variance (0.94 s $\to$ 1.57 s):** Multi-run cold boot times include disk I/O synchronization and Btrfs superblock validation upon mount. Runs 2–5 consistently booted in 1.09s to 1.20s.

---

## 2. Security & Policy Verification Suite (401 Tests)

*Source: [`tests/results/verify.log`](file:///c:/Users/len/OS/tests/results/verify.log)*

- **Total Test Suites:** 22 suites (20 unit, 1 integration, 1 attack suite)
- **Total Tests Executed:** 401 tests
- **Passing Rate:** **100.0%** (401 passed, 0 failed, 0 errors in 125.86s)
- **Prompt Injection Defense:** 70 adversarial attack vectors (`tests/assistant/injection.jsonl`) evaluated against `PolicyEngine`:
  - **Breach Rate:** **0.00%** (0 / 70 breaches)
  - **Benign Query False Reject Rate:** **0.00%** (50 / 50 benign commands permitted)

---

## 3. Cryptographic Audit & Rollback Verification

*Source: [`docs/audit/v2_b1_evidence.txt`](file:///c:/Users/len/OS/docs/audit/v2_b1_evidence.txt)*

- **Persistent Mount:** Verified `/dev/vda3` mounted at `/data` (`FSTYPE: btrfs`, `rw,relatime,discard=async,space_cache=v2`).
- **Reboot Persistence:** File `/data/persistent_test.txt` written in Run 1 and successfully read in Run 2 after hypervisor power cycle.
- **Transactional Rollback:**
  - Initial Tree Hash: `86637d62171b5c904cf144f19c0591f0682f5263ed3d757ba92321c2483e2f60`
  - Post-Mutation Tree Hash: `e2dfdcda5f9287d9c813ce49d6f54236e533b72248569b0ea79ac769c91447c6`
  - Post-Rollback Tree Hash: `86637d62171b5c904cf144f19c0591f0682f5263ed3d757ba92321c2483e2f60`
  - Verified: Temporary mutation file removed, tree hashes match identically.
- **Audit Hash Chain:** All events cryptographically chained via SHA-256; zero tamper tolerance verified across modification, insertion, deletion, and truncation attacks.
