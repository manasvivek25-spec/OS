# Lazy OS v3 Blocked and Partial Items Ledger

**Last Updated**: 2026-11-19T01:31:00+05:30  
**Status**: Active Tracking (V3 Milestones)  
**Rule Reference**: Section 1 (Stop Rule) & Section 8 (Human-Only Items)

This document tracks every acceptance check or milestone that is currently `BLOCKED` or `PARTIAL`, documenting the technical reason, the honest alternative implemented, and the specific human action required (if any).

---

## 1. Active Item Table

| Check ID | Phase / Area | Status | Technical Root Cause | Honest Alternative Implemented | Required Human Action |
| :---: | :--- | :---: | :--- | :--- | :--- |
| **O1 / O2** | OS Image | **PARTIAL** | Custom Buildroot kernel & rootfs image generation scheduled in milestone V3.1. | Fast-boot dev image (Ubuntu 6.8 + Btrfs kernel modules + raw GPT disk) actively running in QEMU. | None (Automated build in V3.1). |
| **O7 / V3.16**| Yocto Build | **BLOCKED** | Local host RAM is 11.5 GB (< 16.0 GB hardware resource gate for full Yocto cross-compilation). | Kas metadata statically validated; primary native distro target ported to Buildroot (`lazy-br2/`) which compiles cleanly under 12 GB RAM. | Provision $\ge 16$ GB RAM cloud instance to run `kas build yocto/kas.yml` per `docs/BUILD_ENV_PLAN.md`. |
| **FT1** | In-Guest LLM | **PARTIAL** | Native `llama.cpp` Buildroot package & GGUF model download scheduled in milestone V3.3. | In-guest heuristic mock planner and host LLM bridge (`HOST LLM (not in image)`) functional. | None (Automated build in V3.3). |
| **FT4** | Hardware Control | **PARTIAL** | Virtual machine hypervisor (QEMU) cannot emulate physical laptop backlight, battery charging circuit, or physical CPU governor. | Real interfaces used where VM exposes them (rfkill via `mac80211_hwsim`, USB via xHCI, ALSA audio). Fake-sysfs used for backlight/battery, labeled `VM-UNAVAILABLE` in badges. | Run `scripts/hw-selftest.sh` on a physical bare-metal laptop. |
| **FT8** | Voice Input | **PARTIAL** | Automated headless test uses synthetic audio loopback; physical microphone input requires human speech. | Synthetic audio round-trip and transcription WER verified; browser Web Speech API available in HUD. | Speak into physical microphone during manual testing. |
| **P7** | Dist Packaging | **PARTIAL** | `dist/` directory, multi-format images (qcow2, vdi, vmdk) scheduled in milestone V3.13. | Bootable images in `build/v2/` operational. | None (Automated packaging in V3.13). |

---

## 2. Resource Gate Audit

- **Host RAM**: 11.5 GB physical memory (WSL2 Ubuntu 24.04).
- **Toolchain Gate**:
  - Yocto BitBake requires $\ge 16.0$ GB RAM $\implies$ Gated as Human Action Required.
  - Buildroot requires $\approx 4.0$–$8.0$ GB RAM $\implies$ **UNBLOCKED** on this machine.
- **Disk Free**: 952 GB on `/dev/sdd` (WSL root), 98 GB on `/mnt/c`. Minimum requirement of 30 GB free disk is **SATISFIED**.
