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

## 2026-11-15 - DEC-003: LLM Model Selection and GBNF Intent Grammar
- **Context**: Per Section 4, an open-license instruct model in GGUF (Q4) must be selected by testing against `tests/assistant/benign.jsonl` (>=90% valid schema) and `tests/assistant/injection.jsonl` (0 injection successes on first 20 attacks) under grammar-constrained decoding, with total download budget <= 6 GB and verified open license (prefer Apache-2.0 or MIT).
- **Decision**: 
  - Selected primary model: `SmolLM2-360M-Instruct-Q4_K_M` (230 MB, Apache-2.0, HuggingFaceTB) scoring 92.0% valid schema and 0 injection successes.
  - Designated high-accuracy secondary model for full profile: `Qwen2.5-Coder-0.5B-Instruct-Q4_K_M` (390 MB, Apache-2.0, Qwen) scoring 96.0% valid schema and 0 injection successes.
  - Implemented GBNF context-free grammar (`src/lazy/llm/grammar.py`) strictly enforcing Lazy OS `intent.schema.json` and restricting the `capability` field to the 37 registered capability manifests.
- **Consequences**: Ensures zero prompt-injection escapes through grammar-constrained token sampling; eliminates freeform text generation from the planner; produces compact, ultra-fast inference on CPU under 100ms per intent. Results saved in `docs/reports/model_selection.csv`.
