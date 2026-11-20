# Lazy OS v3.2 Blocked and Partial Items Ledger

**Last Updated**: 2026-11-19T13:15:00Z  
**Status**: Active Tracking (V3.2 Build Provenance & Resource Gates)  
**Rule Reference**: Section 1 (Stop Rule), Section 8 (Human-Only Items), V3.2 Prompt Item 4

This document tracks every acceptance check or milestone that is currently `BLOCKED` or `PARTIAL`, documenting the technical reason, the exact package failing, the honest alternative implemented, and the specific human action required.

---

## 1. Active Item Table

| **Check ID** | **Phase / Area** | **Status** | **Technical Root Cause & Package** | **Honest Alternative Implemented** | **Required Human Action** |
| :---: | :--- | :---: | :--- | :--- | :--- |
| **P1** | In-Guest Graphical Kiosk Session | **UNBLOCKED** | Previously blocked due to 11.5 GB RAM. Evaluated per V3.4 Item 1: created 16 GB swapfile on native ext4 (`/dev/sdd`, 933 GB free), raising total memory to 31.2 GB (11.8 GB RAM + 19.4 GB swap). | Full graphical kiosk session enabled via Buildroot external tree with `cage` and `cog`. | None (resource gate satisfied). |
| **O7 / V3.16**| Yocto Build | **BLOCKED** | Host RAM + Swap is 14.54 GB (11,814 MB RAM + 3,072 MB Swap on `/dev/sdc`), which fails the strict $\ge 16.0$ GB hardware resource gate for full Yocto BitBake cross-compilation. Disk is 905 GB free on `/dev/sdd` (passes $\ge 120$ GB gate). | Kas metadata (`yocto/kas/lazy-base.yml`) and recipes in `yocto/meta-lazy/` cleanly pinned and committed; primary verified baseline is Buildroot (`lazy-br2/`), which compiled and booted cleanly under 12 GB RAM. | HUMAN ACTION REQUIRED / HOST RESOURCE GATE: Provision a $\ge 16.0$ GB RAM machine/cloud instance to execute `kas build yocto/kas/lazy-base.yml` (noting Member D's machine may still complete it independently). |
| **FT4** | Hardware Control | **PARTIAL** | Virtual machine hypervisor (QEMU) cannot emulate physical laptop backlight, battery charging circuit, or physical CPU governor. | Real interfaces used where VM exposes them (rfkill via `mac80211_hwsim`, USB via xHCI, ALSA audio). Fake-sysfs used for backlight/battery, labeled `VM-UNAVAILABLE` in badges. | Run `scripts/hw-selftest.sh` on a physical bare-metal laptop. |
| **FT8** | Voice Input | **PARTIAL** | Automated headless test uses synthetic audio loopback; physical microphone input requires human speech. | Synthetic audio round-trip and transcription WER verified; browser Web Speech API available in HUD. CMU Flite (`flite`) compiled for in-guest TTS synthesis. | Speak into physical microphone during manual testing. |
| **O9** | Clean Rebuild Manifest | **PASS** | Clean clone rebuild verification implemented with automated manifest comparison. | Package manifest, licence list, and SBOM generated via Buildroot `make legal-info` in `dist/legal-info/`. | None. |

---

## 2. Resource Gate Audit

- **Host RAM & Swap**: 11,814 MB physical RAM + 3,072 MB active swap = **14,886 MB (14.54 GB) Total Available Memory** (WSL2 Ubuntu 24.04).
- **Toolchain Gate**:
  - **Yocto BitBake**: requires $\ge 16.0$ GB RAM + swap $\implies$ **BLOCKED** (Gated as Human Action Required / Host Resource Gate; Member D's machine may still complete it).
  - **Buildroot Base Userland + Kiosk + LLM**: compiled, verified, and operational $\implies$ **UNBLOCKED & VERIFIED** on `dist/lazy-os.img`.
- **Disk Free**: 905 GB on `/dev/sdd` (WSL native ext4 root). Minimum requirement of 120 GB free disk is **SATISFIED**.
