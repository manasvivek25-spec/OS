NEXT_ACTION: V2.A1 Repo audit (write docs/audit/REPO_AUDIT.md)

## Current Milestone
V2.A1: Repo audit (Branch, last commit, commit count, tree to depth 3, line counts per package, existing docs, HUD technology and size, gateway routes and WebSocket messages, QEMU and boot scripts, Yocto files, test layout).

## Active Phase
Phase A: Reality Check & Audit (Read-only, no code changes).

## Background Jobs
- task-2009: Host Gateway Server on http://127.0.0.1:8765/ (serve_hud.py)
- task-2565: QEMU GTK guest on DISPLAY=:0 with port forwarding 8766->8765

## Open Problems / Audit Scope
- Verify true build provenance (scripts/build-boot-image.py vs native BitBake/kas).
- Verify storage backing of /data (tmpfs vs persistent block device).
- Real vs simulated LLM in guest.
- Upgrade basic HUD to complete offline desktop-like Command Center SPA.
