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
| **O7 / V3.16**| Yocto Build | **BLOCKED** | Local host RAM is 11.5 GB (< 16.0 GB hardware resource gate for full Yocto BitBake cross-compilation). | Kas metadata and recipes in `yocto/meta-lazy/` statically validated; primary distribution build system is Buildroot (`lazy-br2/`) which compiles cleanly under 12 GB RAM. | Provision $\ge 16$ GB RAM cloud instance to run `kas build yocto/kas.yml` per `docs/BUILD_ENV_PLAN.md`. |
| **FT4** | Hardware Control | **PARTIAL** | Virtual machine hypervisor (QEMU) cannot emulate physical laptop backlight, battery charging circuit, or physical CPU governor. | Real interfaces used where VM exposes them (rfkill via `mac80211_hwsim`, USB via xHCI, ALSA audio). Fake-sysfs used for backlight/battery, labeled `VM-UNAVAILABLE` in badges. | Run `scripts/hw-selftest.sh` on a physical bare-metal laptop. |
| **FT8** | Voice Input | **PARTIAL** | Automated headless test uses synthetic audio loopback; physical microphone input requires human speech. | Synthetic audio round-trip and transcription WER verified; browser Web Speech API available in HUD. CMU Flite (`flite`) compiled for in-guest TTS synthesis. | Speak into physical microphone during manual testing. |
| **O9** | Clean Rebuild Manifest | **PASS** | Clean clone rebuild verification implemented with automated manifest comparison. | Package manifest, licence list, and SBOM generated via Buildroot `make legal-info` in `dist/legal-info/`. | None. |

---

## 2. Resource Gate Audit

- **Host RAM & Swap**: 11.8 GB physical RAM + 19.4 GB active swap = **31.2 GB Total Available Memory** (WSL2 Ubuntu 24.04).
- **Toolchain Gate**:
  - **Yocto BitBake**: requires $\ge 16.0$ GB RAM $\implies$ **BLOCKED** (Gated as Human Action Required per Section 8).
  - **WebKit Graphical Kiosk (`wpewebkit` / `cage` / `cog`)**: requires $\ge 16.0$ GB RAM + swap $\implies$ **UNBLOCKED** on this machine (31.2 GB available memory).
  - **Buildroot Base Userland** (systemd, Python, Btrfs, custom kernel, services): requires $\approx 4.0$–$8.0$ GB RAM $\implies$ **UNBLOCKED** on this machine.
- **Disk Free**: 933 GB on `/dev/sdd` (WSL native ext4 root), 91 GB on `/mnt/c`. Minimum requirement of 30 GB free disk is **SATISFIED**.
