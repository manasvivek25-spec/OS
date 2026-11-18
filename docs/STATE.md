NEXT_ACTION: Milestone V3.4: In-Guest Graphical Session (Minimal Wayland compositor / DRM kiosk, virtio-gpu & virtio-tablet, boots to full-screen Command Center without host browser; QEMU display monitor screendumps).

## Current Milestone
Completed Milestone V3.3 (In-guest native LLM engine with llama.cpp, SmolLM2-360M-Instruct-Q4_K_M GGUF, 97.9 tokens/sec, 78.18 ms TTFT, 100% benign schema compliance, 0 injection escapes, acceptance check FT1 PASS). Commencing Milestone V3.4.

## Active Phase
Milestone V3.4: In-Guest Graphical Session.

## Acceptance Baseline (V3.3 Verified)
- `scripts/accept.sh`: **29 PASS, 1 PARTIAL, 0 BLOCKED, 0 FAIL** (Total Tested: 30).
- In-Guest LLM: **`SmolLM2-360M-Instruct-Q4_K_M`** (258 MB GGUF) running natively with `llama.cpp` (`FT1 PASS`).
- Booted Kernel: **`6.6.21-lazy-os`** custom build (5.91 MB `dist/bzImage`), zero Ubuntu generic kernel (`O2 PASS`).
- Storage: `/data` persistent Btrfs on `/dev/vda3`, surviving reboots (`O4 PASS`).
- Gateway: Serving Command Center REST API on port 8766 (`P1–P7 PASS`).
- Tests: 408/408 passing in `tests/results/verify.log`.
- Services: 15/15 systemd microservices with full sandboxing (Score: 10.00/10.0 in `tests/results/acceptance/O3_security_scores.txt`).

## Execution Summary
- **V3.0 Completed**: Frozen acceptance contract, `docs/acceptance/ACCEPTANCE.md`, `scripts/accept.sh`, `docs/BLOCKED.md`, `USER_GUIDE.md`.
- **V3.1 Completed**: `lazy-br2/` external tree, target defconfig, custom Linux kernel compilation (6.6.21 with 5 fragments, bzImage 5.91 MB), successful QEMU boot, Btrfs persistent storage verified, `make dist` / `build.sh` build skeleton verified. Acceptance checks O1, O2, O4 all PASS.
- **V3.2 Completed**: Systemd 15-microservice sandbox audit (`scripts/generate_security_scores.py` yielding 10.0/10.0), privilege separation test `tests/acceptance/test_s3_permissions.py` (Rule F4/S3 verified), `lazy-br2/package/lazy-os/` package definition verified. Acceptance checks O3 and S3 PASS.
- **V3.3 Completed**: In-guest native LLM engine (`llama.cpp` binaries `llama-cli`/`llama-server`), downloaded and provisioned `SmolLM2-360M-Instruct-Q4_K_M.gguf` (258 MB) in real Btrfs partition `/data/models`, executed `scripts/eval_in_guest_llm.py` measuring 78.18 ms TTFT and 97.9 tokens/sec, verified 100% benign schema compliance and 0 injection escapes. Acceptance check FT1 PASS.
