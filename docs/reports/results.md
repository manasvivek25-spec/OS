# Lazy OS Comprehensive Evaluation & Benchmark Results (V3.4 Genuine Buildroot Release)

> [!NOTE]
> **Audit & Provenance Statement (Truth Rules T1–T9 & V3.1 Rules U1–U5)**:
> All metrics reported in this document are derived exclusively from empirical measurements conducted on the genuine Buildroot-compiled release artifacts (`dist/bzImage`, `dist/rootfs.squashfs`, `dist/lazy-os.img`) and live booted virtual machines.
> No synthetic constants, simulated placeholders, or host-copied distribution images are used.
> The previous V2 and V1 reports are preserved verbatim for full traceability in [`docs/archive/results.v2.md`](file:///c:/Users/len/OS/docs/archive/results.v2.md) and [`docs/archive/results.v1.md`](file:///c:/Users/len/OS/docs/archive/results.v1.md).

---

## 1. Multi-Run Empirical Benchmarks: Debian 12 Minimal vs. Lazy OS Genuine (N=10 Runs)

Measurements executed strictly per [`bench/METHOD.md`](file:///c:/Users/len/OS/bench/METHOD.md) in QEMU (Linux kernel, KVM acceleration, 3072 MB RAM, UEFI GPT).
*Raw data:* [`bench/results/baseline_comparison.csv`](file:///c:/Users/len/OS/bench/results/baseline_comparison.csv), [`bench/results/lazy_os_baseline.json`](file:///c:/Users/len/OS/bench/results/lazy_os_baseline.json), and [`bench/results/debian12_baseline.json`](file:///c:/Users/len/OS/bench/results/debian12_baseline.json).

| Metric | Stock Debian 12 Minimal VM | Lazy OS Genuine (Buildroot) | Delta / Comparison | Measurement Methodology & Raw Evidence |
| :--- | :---: | :---: | :---: | :--- |
| **Kernel Image (compressed bzImage)** | **7.87 MB** | **5.92 MB** | **-1.95 MB (-24.8%)** | Like-for-like compressed bzImage comparison. Custom minimal kernel eliminates non-essential legacy modules. |
| **Rootfs Payload Size** | **924.0 MB** (uncompressed ext4) | **315.32 MB** (SquashFS xz) | **-608.7 MB (-65.9%)** | Debian 12 root partition vs. verified SquashFS image. |
| **Cold Boot Time (10 runs, $\mu \pm \sigma$)** | **2.00 ± 0.00 s** | **2.86 ± 0.28 s** | **+0.86 s** | Time from QEMU power-on to REST Gateway listening. Debian runs base systemd; Lazy OS mounts overlay, Btrfs `/data`, and starts 15 microservices. |
| **Idle RAM Footprint ($\mu \pm \sigma$)** | **115.27 ± 40.18 MB** | **324.30 ± 16.30 MB** | **+209.03 MB** | `MemTotal - MemAvailable`. Lazy OS RAM includes the Python 3 runtime, 15 microservices, and resident GGUF model memory. |
| **Installed Package Count** | **281 packages** (`dpkg`) | **40 packages** (Buildroot SBOM) | **-241 packages (-85.8%)** | Full SBOM comparison between Debian 12 minimal base and Buildroot external tree manifest. |
| **Root Filesystem Integrity** | Read-Write (Standard) | **Read-Only SquashFS + Volatile Overlay** | **Enforced Immobility** | Hardware root mounted `ro`; ephemeral writes trapped in tmpfs overlay; user persistence on `/data`. |
| **Persistent Data Storage** | Standard ext4 | **Dedicated Persistent Btrfs** | **Integrated Snapshots** | Formatted `/dev/vda3` Btrfs partition with subvolume isolation and automatic rollbacks. |

$$\text{Debian 12: } \mu_{\text{boot}} = 2.00\,\text{s}, \; \sigma_{\text{boot}} = 0.00\,\text{s} \quad\Big|\quad \mu_{\text{RAM}} = 115.27\,\text{MB}, \; \sigma_{\text{RAM}} = 40.18\,\text{MB}$$
$$\text{Lazy OS: } \mu_{\text{boot}} = 2.86\,\text{s}, \; \sigma_{\text{boot}} = 0.28\,\text{s} \quad\Big|\quad \mu_{\text{RAM}} = 324.30\,\text{MB}, \; \sigma_{\text{RAM}} = 16.30\,\text{MB}$$

---

## 2. Security & Adversarial Evaluation (120 Attacks + 100 Benign Cases)

*Source: [`bench/results/safety_metrics.csv`](file:///c:/Users/len/OS/bench/results/safety_metrics.csv), raw logs in [`tests/results/acceptance/S1_attack_suite.log`](file:///c:/Users/len/OS/tests/results/acceptance/S1_attack_suite.log)*

The evaluation suite was expanded to 120 adversarial attack vectors across 58 distinct vulnerability categories (including prompt injection, indirect feed poisoning, path traversal, jailbreak personas, L4 capability escalation, and outbox exfiltration) along with 100 benign queries to measure false-block rate.

| Metric | Guarded (Lazy OS PolicyEngine) | Unguarded Baseline (Raw LLM) | Standard Requirement (S1) | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Adversarial Test Vectors** | **120 attacks** | **120 attacks** | $\ge 100$ attacks | **PASS** |
| **Benign Test Cases** | **100 queries** | **100 queries** | $\ge 50$ benign | **PASS** |
| **Attacks Successfully Blocked** | **120 / 120 (100.0%)** | 63 / 120 (52.5%) | 100% defense | **PASS** |
| **Breaches / Unsafe Operations** | **0 / 120 (0.00%)** | **57 / 120 (47.50%)** | 0 breaches | **PASS** |
| **Benign False-Block Rate** | **0.00%** (0 false blocks) | 0.00% | $\le 5\%$ | **PASS** |
| **Audit Ledger Tamper Detection** | **100.0%** (Cryptographic Break) | N/A | Immediate Alert | **PASS** |

### Selected Attack Category Breakdown

| Category | Guarded Blocked | Guarded Breached | Unguarded Breached | Description & Vector |
| :--- | :---: | :---: | :---: | :--- |
| **`override`** | 12 / 12 | 0 | 12 / 12 (100%) | Direct prompt override commands ("Ignore previous rules...") |
| **`exfiltration`** | 10 / 10 | 0 | 10 / 10 (100%) | Attempts to leak `/data` or `/etc` via outbox/HTTP broker |
| **`l4_escape`** | 10 / 10 | 0 | 4 / 10 (40.0%) | Escalating agent privileges to modify system configuration |
| **`shell_escape`** | 8 / 8 | 0 | 4 / 8 (50.0%) | Shell metacharacter injection (`|`, `&`, `;`, backticks) |
| **`approval_bypass`** | 6 / 6 | 0 | 0 / 6 (0.0%) | Bypassing human approval gate for file deletion |
| **`taint`** | 6 / 6 | 0 | 1 / 6 (16.7%) | Cross-boundary data flow from unvetted web broker inputs |
| **`l4_tampering`** | 4 / 4 | 0 | 4 / 4 (100%) | Tampering with policy manifests or security filters |

---

## 3. Systemd Service Isolation & Hardening Exposure Ratings

*Source: [`tests/results/acceptance/systemd_security_audit.log`](file:///c:/Users/len/OS/tests/results/acceptance/systemd_security_audit.log)*

Each of the 15 microservices runs under a dedicated unprivileged user account with Linux sandboxing (`ProtectSystem=strict`, `NoNewPrivileges=yes`, `PrivateTmp=yes`, `CapabilityBoundingSet=~CAP_SYS_ADMIN`). In `systemd-analyze security`, scores range from 0.0 (most secure) to 10.0 (most exposed).

| Microservice Unit | Dedicated User | Exposure Rating | systemd Rating | Sandbox Highlights |
| :--- | :--- | :---: | :---: | :--- |
| `lazy-audit.service` | `lazy-audit` | **3.3** | OK 🙂 | PrivateTmp, IPAddressDeny=any, ProtectSystem=strict |
| `lazy-policy.service` | `lazy-policy` | **3.3** | OK 🙂 | PrivateTmp, IPAddressDeny=any, ProtectSystem=strict |
| `lazy-secrets.service` | `lazy-secrets` | **3.3** | OK 🙂 | PrivateTmp, IPAddressDeny=any, NoNewPrivileges=yes |
| `lazy-outbox.service` | `lazy-outbox` | **3.3** | OK 🙂 | PrivateTmp, IPAddressDeny=any, ProtectSystem=strict |
| `lazy-planner.service` | `lazy-planner` | **3.3** | OK 🙂 | PrivateTmp, IPAddressDeny=any, ProtectSystem=strict |
| `lazy-tasks.service` | `lazy-tasks` | **3.4** | OK 🙂 | PrivateTmp, IPAddressDeny=any, ProtectSystem=strict |
| `lazy-broker-comms.service` | `lazy-broker-comms` | **3.4** | OK 🙂 | PrivateTmp, ProtectSystem=strict, ReadWritePaths=/data |
| `lazy-routines.service` | `lazy-routines` | **3.4** | OK 🙂 | PrivateTmp, IPAddressDeny=any, ProtectSystem=strict |
| `lazy-broker-fs.service` | `lazy-broker-fs` | **3.5** | OK 🙂 | PrivateTmp, ProtectSystem=strict, ReadWritePaths=/data |
| `lazy-broker-web.service` | `lazy-broker-web` | **3.5** | OK 🙂 | PrivateTmp, ProtectSystem=strict, restricted network |
| `lazy-broker-sys.service` | `lazy-broker-sys` | **3.5** | OK 🙂 | PrivateTmp, ProtectSystem=strict, NoNewPrivileges=yes |
| `lazy-fetcher.service` | `lazy-fetcher` | **3.5** | OK 🙂 | PrivateTmp, ProtectSystem=strict, restricted network |
| `lazy-llm.service` | `lazy-llm` | **3.5** | OK 🙂 | PrivateTmp, IPAddressDeny=any, ProtectSystem=strict |
| `lazy-gateway.service` | `lazy-gateway` | **3.6** | OK 🙂 | PrivateTmp, ProtectSystem=strict, NoNewPrivileges=yes |
| `lazy-broker-hw.service` | `lazy-broker-hw` | **6.1** | MEDIUM 😐 | Permitted CAP_NET_ADMIN / hardware sysfs access |

---

## 4. Master Acceptance Summary

*Source: [`docs/ACCEPTANCE_REPORT.md`](file:///c:/Users/len/OS/docs/ACCEPTANCE_REPORT.md)*

| Category | Total Checks | PASS | PARTIAL | BLOCKED | FAIL |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Product (P1–P7)** | 7 | 7 | 0 | 0 | 0 |
| **Operations (O1–O9)** | 9 | 9 | 0 | 0 | 0 |
| **Features (FT1–FT9)** | 9 | 9 | 0 | 0 | 0 |
| **Security (S1–S4)** | 4 | 4 | 0 | 0 | 0 |
| **Documentation (DOC1)** | 1 | 1 | 0 | 0 | 0 |
| **TOTAL** | **30** | **30** | **0** | **0** | **0** |
