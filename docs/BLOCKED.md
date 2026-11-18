# Lazy OS v3 Blocked and Partial Items Ledger

**Last Updated**: 2026-11-19T01:31:00+05:30  
**Status**: Active Tracking (V3 Milestones)  
**Rule Reference**: Section 1 (Stop Rule) & Section 8 (Human-Only Items)

This document tracks every acceptance check or milestone that is currently `BLOCKED` or `PARTIAL`, documenting the technical reason, the honest alternative implemented, and the specific human action required (if any).

---

## 1. Active Item Table

| **Check ID** | **Phase / Area** | **Status** | **Technical Root Cause** | **Honest Alternative Implemented** | **Required Human Action** |
| :---: | :--- | :---: | :--- | :--- | :--- |
| **O7 / V3.16**| Yocto Build | **BLOCKED** | Local host RAM is 11.5 GB (< 16.0 GB hardware resource gate for full Yocto cross-compilation). | Kas metadata statically validated; primary native distro target ported to Buildroot (`lazy-br2/`) which compiles cleanly under 12 GB RAM. | Provision $\ge 16$ GB RAM cloud instance to run `kas build yocto/kas.yml` per `docs/BUILD_ENV_PLAN.md`. |
| **FT1** | In-Guest LLM | **RESOLVED (PASS)** | Completed in milestone V3.3. In-guest native `llama.cpp` + `SmolLM2-360M-Instruct-Q4_K_M` operational. | 100% benign schema compliance, 0 injection escapes, 97.9 tok/s, 78.18 ms TTFT. | None. |
| **FT4** | Hardware Control | **PARTIAL** | Virtual machine hypervisor (QEMU) cannot emulate physical laptop backlight, battery charging circuit, or physical CPU governor. | Real interfaces used where VM exposes them (rfkill via `mac80211_hwsim`, USB via xHCI, ALSA audio). Fake-sysfs used for backlight/battery, labeled `VM-UNAVAILABLE` in badges. | Run `scripts/hw-selftest.sh` on a physical bare-metal laptop. |
| **FT8** | Voice Input | **PARTIAL** | Automated headless test uses synthetic audio loopback; physical microphone input requires human speech. | Synthetic audio round-trip and transcription WER verified; browser Web Speech API available in HUD. | Speak into physical microphone during manual testing. |
| **O9** | Clean Rebuild | **PARTIAL** | Full clean-checkout manifest verification scheduled for milestone V3.14. | Initial build provenance and manifests tracked in `docs/academic/`. | None (Automated build in V3.14). |

---

## 2. Resource Gate Audit

- **Host RAM**: 11.5 GB physical memory (WSL2 Ubuntu 24.04).
- **Toolchain Gate**:
  - Yocto BitBake requires $\ge 16.0$ GB RAM $\implies$ Gated as Human Action Required.
  - Buildroot requires $\approx 4.0$–$8.0$ GB RAM $\implies$ **UNBLOCKED** on this machine.
- **Disk Free**: 952 GB on `/dev/sdd` (WSL root), 98 GB on `/mnt/c`. Minimum requirement of 30 GB free disk is **SATISFIED**.
