# Architecture and Project Decisions

## 2026-11-15 - DEC-001: Execution Environment and Host Bridging
- **Context**: The build orchestrator runs on a Windows host with native WSL2 Ubuntu 24.04 (Linux 6.6.87.2-microsoft-standard-WSL2 x86_64, 16 vCPUs, 12GB RAM, 953GB disk free).
- **Decision**: All Linux-specific build tasks, services, tests, and Yocto container/QEMU tooling execute in WSL2 Ubuntu directly against the repository mount (`/mnt/c/Users/len/OS`), with helper scripts and Makefile targets configured to run natively inside WSL or via `wsl` commands.
- **Consequences**: Provides authentic Linux kernel, cgroups, systemd/DBus abstractions, POSIX sockets, and native compilation while maintaining synchronization with the workspace.

## 2026-11-15 - DEC-002: Yocto Release and Pinning
- **Context**: Default Yocto LTS release must be chosen and pinned with `kas` per section 4.
- **Decision**: Yocto LTS release `scarthgap` (version 5.0.x), with exact verified upstream commit hashes:
  - `poky`: `https://git.yoctoproject.org/poky` @ `6b7c1066f778db5a6b3e35400617b10342988fa8` (branch `scarthgap`)
  - `meta-openembedded`: `https://git.openembedded.org/meta-openembedded` @ `2db6aece32c7f8ebf6015b468e1b4e21de072e3b` (branch `scarthgap`)
  - `meta-lazy`: local repository layer at `yocto/meta-lazy`
- **Consequences**: Standardized, rock-solid reproducible builds with active LTS security maintenance. Verified via `git ls-remote` per Rule R5.
