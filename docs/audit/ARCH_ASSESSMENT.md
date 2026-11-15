# Lazy OS Architecture Assessment (V2.A5)

**Audit Date:** 2026-11-16T01:15:30+05:30  
**Auditor:** Antigravity Autonomous Systems Engineer  
**Classification:** VERIFIED AUDIT

---

## 1. Core Weaknesses
- **Volatile Storage:** `/data` is currently a RAM-backed `tmpfs`; any file created or modified is lost upon VM reboot.
- **Missing Process Supervisor:** No real `systemd` or service manager runs in the guest; microservices are Python classes imported in-process rather than independently supervised OS daemons.
- **Mock CLI Wrappers:** `/bin/systemctl` and `/bin/lsblk` intercept commands and emit static strings rather than querying the kernel or init system.

## 2. Missing Components
- **In-Guest REST API:** `lazy-gateway` currently only implements WebSocket framing and static HTML asset delivery; standard REST `/api/*` endpoints are missing.
- **In-Guest LLM Engine:** No static `llama.cpp` binary or resident GGUF model runs in the guest; planning is entirely heuristic mock.
- **Kernel Module Tree:** `/lib/modules/` is missing from the guest, preventing dynamic module loading (e.g. `btrfs.ko`, `overlay.ko`).

## 3. Security Issues
- **Unenforced Kernel Sandboxing:** While `PolicyEngine` enforces capability tiers (L0–L4) at the application layer, kernel-level Landlock LSM and Seccomp BPF syscall restrictions are not actively enforced inside the unprivileged Busybox shell.
- **Missing Ephemeral Secrets Lifecycle:** `lazy-secrets` implements AES-256-GCM encryption but does not integrate with Linux kernel keyring (`keyctl`).

## 4. Backend & Frontend Gaps
- **Frontend Breadth:** The existing HUD (`hud/index.html`) is a static 3-card preview; it lacks a process manager, file explorer, security audit inspector, settings drawer, and command center.
- **WebSocket Schema Tightness:** WebSocket events are dispatched without strict contract schema validation on outbound broadcast payloads.

## 5. Build & Environment Gaps
- **BitBake / Yocto Disconnect:** Yocto metadata in `yocto/` is well-formed, but the bootable image was synthesized using host Ubuntu binaries via a Python helper script.
- **WSL2 Resource Constraints:** Host WSL2 has 12 GB RAM and no swap config; native BitBake compilation of a full Linux image risks memory exhaustion without external sstate mirrors.

## 6. Performance Limits
- **Single-Threaded Gateway:** `SimpleHTTPRequestHandler` in `lazy-guest-daemon.py` is single-threaded and blocking.
- **Copy-Backend Overhead:** Task undo uses recursive filesystem copying (`CopyBackend`), which degrades with large directory trees; persistent block devices with snapshot support are required.
