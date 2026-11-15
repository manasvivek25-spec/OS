# Package Manifest and Selection Rationale

## Profiles
1. **base**: Minimal hardened headless profile without neural models or speech engines. Designed for high efficiency, tiny footprint, and as the baseline for the university 40% size reduction comparison against stock distribution minimal installations.
2. **full**: Complete Lazy OS deployment with resident `llama.cpp` inference engine, Vosk speech-to-text, espeak-ng text-to-speech, static local HUD server, and isolated browser runtime.

## Core Inclusions
- `busybox` / `base-files`: Minimal core utilities and filesystem hierarchy. (Essential for minimal footprint).
- `systemd`: Init system providing cgroups v2, transient units (`systemd-run`), sandboxing primitives (`ProtectSystem`, `PrivateTmp`, seccomp filters), and D-Bus IPC.
- `python3-core` & required modules: Powers all Lazy OS services (`lazy-gateway`, `lazy-policy`, `lazy-tasks`, `lazy-audit`, brokers).
- `btrfs-progs`: Snapshot and subvolume management for transactional filesystem rollbacks.
- `lazy-services`: Custom package providing systemd units, configuration manifests, and Python services.

## Profile: full Specific Inclusions
- `llama.cpp`: High-performance CPU/accelerator GGUF inference engine.
- `vosk`: Lightweight offline speech recognition library and acoustic model.
- `espeak-ng`: Lightweight offline speech synthesizer.
- `chromium` or `firefox` (headless WebDriver capable): Isolated browser agent for web tasks.

## Key Exclusions
- Full desktop environments (GNOME, KDE, XFCE): Unnecessary overhead; Lazy OS utilizes a dedicated local web HUD on loopback (127.0.0.1:8765).
- Traditional package managers in production image (apt, dnf, opkg in runtime): Read-only root filesystem prevents drift and tamper.
- Free-form interactive shells for planner: Strictly prohibited by Rule F2.
