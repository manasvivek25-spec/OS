# Lazy OS Open Source Licences and Compliance Audit

## 1. Compliance Statement
Lazy OS is composed entirely of open-source software under permissive and standard copyleft licenses. There are zero proprietary binary blobs, zero closed-source libraries, and zero non-commercial restriction licenses in the entire distribution.

---

## 2. Component Licence Matrix

| Component | Upstream Project / Author | License Identifier | License File Reference | Notes & Usage |
|---|---|---|---|---|
| **Lazy OS Core Code** | Lazy OS Team | `MIT` | `LICENSE` | Services, brokers, dialogue manager, HUD, and tests. |
| **Linux Kernel** | Linus Torvalds / Kernel.org | `GPL-2.0-with-syscall-note` | `LICENSES/preferred/GPL-2.0` | Custom kernel configuration fragments. |
| **systemd** | systemd Authors | `LGPL-2.1-or-later` | `LICENSE.LGPL2.1` | Init system, cgroup v2, sandboxing units. |
| **Btrfs-progs** | Chris Mason / Kernel.org | `GPL-2.0-only` | `COPYING` | Transactional snapshot management. |
| **Squashfs-tools** | Phillip Lougher | `GPL-2.0-or-later` | `COPYING` | Read-only compressed root filesystem generator. |
| **llama.cpp** | Georgi Gerganov | `MIT` | `LICENSE` | C++ LLM inference engine. |
| **SmolLM2-360M Model** | Hugging Face (Loubna Ben Allal et al.) | `Apache-2.0` | `model_card.md` | Permissive weights for instruction planning. |
| **Vosk STT Library** | Alpha Cephei Inc. | `Apache-2.0` | `COPYING` | Speech recognition engine. |
| **Vosk Acoustic Model** | Alpha Cephei Inc. | `Apache-2.0` | `README` | Small English speech recognition acoustic weights. |
| **espeak-ng** | Jonathan Duddington / espeak-ng | `GPL-3.0-or-later` | `COPYING` | Text-to-speech voice synthesizer. |
| **Python 3 Runtime** | Python Software Foundation | `PSF-2.0` | `LICENSE` | Python execution environment. |
| **PyYAML** | Kirill Simonov | `MIT` | `LICENSE` | Capability manifest parser. |
| **jsonschema** | Julian Berman | `MIT` | `COPYING` | System contract schema validator. |
| **Yocto Project / Poky** | Linux Foundation | `MIT` & `GPL-2.0-only` | `poky/LICENSE` | Embedded Linux distribution build framework. |
| **OpenSSH** | The OpenBSD Project | `BSD-2-Clause` / `BSD-3-Clause` | `LICENCE` | Secure remote shell test harness. |

---

## 3. License Isolation & Copyleft Boundary Analysis

1. **GPLv2 Linux Kernel**:
   - The user-space execution of Lazy OS services interacts with the kernel strictly across the standard Linux system call boundary (`Linux-syscall-note`). Under the terms of the syscall exception, user-space code calling standard POSIX syscalls does not become subject to the GPLv2.
2. **LGPLv2.1 systemd**:
   - Lazy OS interacts with systemd dynamically through standard D-Bus IPC and systemd unit specifications. No systemd internal source code is statically linked into Lazy OS binaries.
3. **GPLv3 espeak-ng**:
   - The `TTSEngine` in `src/lazy/voice/tts.py` invokes `espeak-ng` as an independent subprocess using `subprocess.run()`, writing audio to standard pipes or temporary WAV files. Under FSF licensing guidelines, invoking an external program via standard process separation does not create a derivative work.
4. **Apache-2.0 SmolLM2 & Vosk Models**:
   - Model weights are distributed in standard GGUF format and loaded at runtime by `llama.cpp` and `vosk-api`. Both carry permissive Apache-2.0 licenses with full commercial and academic rights granted.

---

## 4. Verification Check
- Total audited packages: **15 / 15** (100% open source).
- Proprietary software count: **0** (Zero exceptions needed).
