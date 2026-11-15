# Architecture and Project Decisions

## 2026-11-15 - DEC-001: Execution Environment and Host Bridging
- **Context**: The build orchestrator runs on a Windows host with native WSL2 Ubuntu 24.04 (Linux 6.6.87.2-microsoft-standard-WSL2 x86_64, 16 vCPUs, 12GB RAM, 953GB disk free).
- **Decision**: All Linux-specific build tasks, services, tests, and Yocto container/QEMU tooling execute in WSL2 Ubuntu directly against the repository mount (`/mnt/c/Users/len/OS`), with helper scripts and Makefile targets configured to run natively inside WSL or via `wsl` commands.
- **Consequences**: Provides authentic Linux kernel, cgroups, systemd/DBus abstractions, POSIX sockets, and native compilation while maintaining synchronization with the workspace.

## 2026-11-15 - DEC-002: Yocto Release and Pinning
- **Context**: Default Yocto LTS release must be chosen and pinned with `kas` per section 4.
- **Decision**: Yocto LTS release `scarthgap` (version 5.0.x), supported until April 2028, with pinned git revisions for `poky` (scarthgap branch) and `meta-openembedded`.
- **Consequences**: Standardized, rock-solid reproducible builds with active LTS security maintenance.
