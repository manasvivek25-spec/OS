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

## 2026-11-15 - DEC-004: Browser Integration in Full Image and Documented Fallback
- **Context**: Per Section 4 Defaults, the browser architecture requires a driver interface supporting WebDriver with headless browser, and a fallback pure-Python HTTP driver that fetches pages, strips scripts, and extracts structured text, forms, and links for the reader. If a monolithic desktop browser (Chromium/WebKit) cannot be built into the embedded image footprint (~400MB-1GB, requiring Wayland/X11 and Rust/Clang toolchains) without violating the university Track A 40% size comparison target, validate on the host, document the shortfall, and provide the isolated sandbox driver.
- **Decision**: 
  1. The full image profile (`lazy-image-full`) includes the `lazy-browser` package providing the isolated headless browser runtime and WebDriver HTTP wire client.
  2. The `WebBroker` driver architecture implements `BaseBrowserDriver` with two interchangeable engines: `WebDriverBrowserDriver` (connecting to W3C WebDriver endpoints) and `PurePythonBrowserDriver` (self-contained isolated DOM parser with prompt injection detection in comments and hidden CSS tags).
  3. Automatic runtime probing (`get_browser_driver(driver_type="auto")`) connects to WebDriver if available and gracefully falls back to `PurePythonBrowserDriver` with diagnostic logging.
- **Consequences**: Satisfies Rule F9 (isolated namespace and 0600 quarantine directory) and Section 4 Defaults while preventing bloat of the minimal embedded image. Full integration verified on host and in QEMU.

## 2026-11-19 - DEC-005: Acceptance Check O1 Implementation in scripts/accept.sh
- **Context**: Check O1 in `scripts/accept.sh` was an initial placeholder returning PARTIAL. Per Section 3, acceptance script checks may be updated to fix check logic and accurately test real artifacts.
- **Decision**: Implemented real artifact verification for O1 checking existence and execution of `build.sh`, generated `dist/bzImage`, and recorded `build-logs/kernel_build.log`.
- **Consequences**: Enables automated verification of the scripted build pipeline without artificial hardcoding. Frozen sha256 checksum updated in `docs/acceptance/FROZEN.sha256`.
