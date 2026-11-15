# Lazy OS Repository Audit (V2.A1)

**Audit Date:** 2026-11-16T01:08:00+05:30  
**Auditor:** Antigravity Autonomous Systems Engineer  
**Classification:** VERIFIED (All figures collected directly via empirical repo inspection)

---

## 1. Git Repository State

- **Branch:** `v2-command-center` (forked from `main`)
- **Last Commit on `main`:** `abc3db584ead26e360a5ee772cdf7370de3a019d`
- **Commit Author:** `Lazy OS Engineer <engineer@lazy-os.local>`
- **Commit Date:** `Sun Nov 15 19:21:12 2026 +0000`
- **Commit Subject:** `feat(boot): add interactive QEMU GTK support and live screenshot capture tools`
- **Total Commit Count:** `37` commits
- **Release Tags:** `v0-final`, `m-M0.1` through `m-M6.4` (33 tags total)

---

## 2. Directory Tree (to Depth 3)

```
/
├── LICENSE
├── Makefile
├── README.md
├── bench/
│   ├── results/
│   │   ├── baseline_comparison.csv
│   │   ├── kernel_benchmark.csv
│   │   ├── latency_ablation.csv
│   │   ├── safety_metrics.csv
│   │   ├── task_eval_llm.csv
│   │   ├── task_eval_mock.csv
│   │   └── top20_packages.csv
│   └── scripts/
│       ├── ablation_latency.py
│       ├── eval_baselines.py
│       ├── eval_full_suite.py
│       ├── run_safety_eval.py
│       └── run_task_eval.py
├── build.sh
├── config/
│   ├── allowlist.yaml
│   ├── capabilities/ (37 capability manifest YAML files)
│   ├── corrections.yaml
│   ├── feeds.yaml
│   ├── routines.yaml
│   └── voice.yaml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── ASSUMPTIONS.md
│   ├── BOOT_EXPLORATION.md
│   ├── BUILD_PROMPT.md
│   ├── DECISIONS.md
│   ├── ENV.md
│   ├── HANDOFF.md
│   ├── HARDWARE-CONTROL.md
│   ├── KNOWN_ISSUES.md
│   ├── LICENCES.md
│   ├── PACKAGES.md
│   ├── PLAN.md
│   ├── PLAN_V2.md
│   ├── SPEC.md
│   ├── STATE.md
│   ├── contracts/ (7 JSON Schema specification contracts)
│   ├── deck-inputs/ (task1.md through task8.md)
│   ├── demo/
│   │   └── RUNSHEET.md
│   ├── proposals/
│   ├── qa/
│   ├── reports/
│   │   ├── model_selection.csv
│   │   ├── reproducibility.md
│   │   └── results.md
│   └── screenshots/
│       └── lazy_os_guest_screen.png
├── hud/
│   ├── hud.css
│   ├── hud.js
│   └── index.html
├── scripts/
│   ├── audit_repo.py
│   ├── boot-and-explore.py
│   ├── build-boot-image.py
│   ├── build-yocto.sh
│   ├── capture_screenshot.py
│   ├── check-env.sh
│   ├── eval_models.py
│   ├── generate_40_tasks.py
│   ├── generate_assistant_datasets.py
│   ├── generate_capabilities.py
│   ├── generate_contract_samples.py
│   ├── generate_intent_fixtures.py
│   ├── handoff.sh
│   ├── sandbox-run.sh
│   ├── send_guest_command.py
│   ├── setup-host.sh
│   ├── tune-latency.sh
│   ├── verify-browser-image.sh
│   ├── verify-docs.sh
│   ├── verify-kernel-fragments.sh
│   ├── verify-latency-tuning.sh
│   ├── verify-m03.sh
│   ├── verify-recipes.sh
│   ├── verify-reproducibility.sh
│   ├── verify-wic.sh
│   └── yocto-container.sh
├── src/
│   └── lazy/
│       ├── __init__.py
│       ├── audit/
│       ├── brokers/
│       ├── common/
│       ├── dialogue/
│       ├── gateway/
│       ├── llm/
│       ├── niche/
│       ├── outbox/
│       ├── pipeline/
│       ├── planner/
│       ├── policy/
│       ├── routines/
│       ├── secrets/
│       ├── systemd/
│       ├── tasks/
│       ├── tuning/
│       └── voice/
├── systemd/ (20 service, slice, and template unit files)
├── tests/
│   ├── assistant/ (benign.jsonl, injection.jsonl)
│   ├── attacks/ (test_attack_suite.py)
│   ├── fixtures/ (chat, contracts, feeds, intents, maildir, sysfs, website)
│   ├── integration/ (test_pipeline_host.py)
│   ├── results/ (32 milestone logs + eval logs)
│   ├── tasks/ (40 individual task YAML specs)
│   └── unit/ (20 unit test suites)
└── yocto/
    ├── kas/ (lazy-base.yml, lazy-full.yml)
    └── meta-lazy/ (conf, images, recipes-browser, recipes-kernel, recipes-lazy, wic)
```

---

## 3. Python Line Counts per Package (`src/lazy/`)

Total Python files: **67 files**, **7,524 lines of code** (excluding `__pycache__` and tests):

| Package | Files | Lines | Purpose / Scope |
| :--- | :---: | :---: | :--- |
| `lazy.audit` | 3 | 277 | Hash-chained SHA-256 audit ledger & offline chain verifier |
| `lazy.brokers` | 7 | 1,483 | Sandboxed capability brokers: FS, Sys, HW/Sysfs, Web, Comms |
| `lazy.common` | 2 | 167 | Shared contracts loader, schema validator, error models |
| `lazy.dialogue` | 3 | 302 | Interactive clarifying dialogue & user question disambiguation |
| `lazy.gateway` | 5 | 530 | WebSocket gateway, token manager, JSON-RPC IPC router |
| `lazy.llm` | 4 | 264 | SmolLM2-360M resident engine client & mock inference engine |
| `lazy.niche` | 7 | 815 | Niche news feeds, RSS parsers, topic scoring, local behavior tracker |
| `lazy.outbox` | 4 | 435 | Hold-and-approval queue for untrusted communication channels |
| `lazy.pipeline` | 2 | 270 | End-to-end intent decomposition, execution & narration pipeline |
| `lazy.planner` | 4 | 277 | Natural language planner, few-shot decomposition, mock planner |
| `lazy.policy` | 6 | 614 | Tiered capability broker (L0-L4), Landlock/Seccomp enforcement, taint engine |
| `lazy.routines` | 4 | 361 | Scheduled background chores, overnight maintenance, wake-up briefing |
| `lazy.secrets` | 3 | 237 | AES-256-GCM / tmpfs encrypted credentials vault |
| `lazy.systemd` | 4 | 294 | Cgroup slice supervisor (`/lazy-interactive.slice`, `/lazy-background.slice`) |
| `lazy.tasks` | 3 | 410 | Task lifecycle manager, snapshot checkpoints, undo rollback backend |
| `lazy.tuning` | 5 | 459 | Latency optimizer, dirty ratios, CPU governor, warm-up preloader |
| `lazy.voice` | 5 | 329 | Vosk voice transcription engine & Piper TTS narration |
| **Total** | **67** | **7,524** | Complete Lazy OS core Python subsystem |

---

## 4. Existing Documentation (`docs/`)

| Document | Size (Bytes) | Content Summary |
| :--- | :---: | :--- |
| `docs/ARCHITECTURE.md` | 7,926 | System architecture, trust model, security tiers, Mermaid diagrams |
| `docs/ASSUMPTIONS.md` | 955 | Explicit engineering defaults applied throughout build |
| `docs/BOOT_EXPLORATION.md`| 25,813 | Phase 1-5 boot investigation and interactive verification logs |
| `docs/BUILD_PROMPT.md` | 20,822 | Master Build Prompt v1 rules (R1-R7, F1-F9) |
| `docs/DECISIONS.md` | 4,286 | Architectural Decision Records (ADR 001 - ADR 012) |
| `docs/ENV.md` | 1,189 | Host environment prerequisites, toolchain versions, paths |
| `docs/HANDOFF.md` | 7,120 | Full session handoff block and execution summary |
| `docs/HARDWARE-CONTROL.md`| 4,049 | Laptop sysfs control specifications and mock hardware roots |
| `docs/KNOWN_ISSUES.md` | 1,197 | Tracked anomalies and hardware constraints |
| `docs/LICENCES.md` | 3,544 | Academic and open-source licence declarations |
| `docs/PACKAGES.md` | 5,441 | Complete package manifest for base and full profiles |
| `docs/PLAN.md` | 4,233 | V1 milestone execution tracker (M0.1 - M6.4) |
| `docs/PLAN_V2.md` | 2,946 | V2 milestone execution tracker (V2.A1 - V2.E4) |
| `docs/SPEC.md` | 5,558 | System requirements specification |
| `docs/STATE.md` | 849 | Current active execution state and Next Action |
| `docs/contracts/*.json` | 7 schemas | Machine-enforced JSON schemas for all IPC and data models |
| `docs/deck-inputs/*.md` | 8 files | Slide-by-slide raw narrative inputs for academic presentation |
| `docs/demo/RUNSHEET.md` | 6,828 | Demonstration run sheet and terminal commands |
| `docs/reports/results.md` | 11,041 | Empirical benchmark report (Debian 12 vs Lazy OS) |
| `docs/reports/reproducibility.md`| 3,862 | Reproducibility protocol and validation commands |

---

## 5. HUD Technology & Footprint (`hud/`)

The HUD is a zero-dependency static web application:
- `hud/index.html`: 4,524 bytes (HTML5 markup, 6 grid cards, status strip, chat terminal)
- `hud/hud.css`: 8,659 bytes (Pure CSS custom properties, grid layout, glowing cyan borders, scanline effect)
- `hud/hud.js`: 7,327 bytes (Pure ES6 JavaScript, RFC 6455 WebSocket client, auto-reconnect, token handshake)
- **Total HUD Payload:** **20,510 bytes** (~20.5 KB total)
- **External Dependencies:** Zero (no external CDNs, fonts, or JS libraries).

---

## 6. Gateway Server Routes & WebSocket Messages

Audit of `src/lazy/gateway/server.py`:

### HTTP Routes (`_serve_http`, line 141)
- `""` or `"index.html"` (line 144): Serves `hud/index.html` (`Content-Type: text/html`)
- `"hud.css"` (line 147): Serves `hud/hud.css` (`Content-Type: text/css`)
- `"hud.js"` (line 150): Serves `hud/hud.js` (`Content-Type: application/javascript`)
- All other routes (line 154): Return `HTTP/1.1 404 Not Found`
- **Finding:** No REST `/api/*` endpoints exist in the V1 gateway.

### WebSocket Interface (`_upgrade_and_handle_ws`, line 177)
- Protocol: RFC 6455 compliant handshake using `Sec-WebSocket-Key` / SHA-1 `258EAFA5...` (line 184)
- **Incoming Message Types:**
  - `"auth"` (line 227): Validates token against `HUDTokenManager` (lines 228-238). Replies with `auth_ok` or `auth_failed`.
  - `"user_input"` (line 245): Dispatches text/voice input payload to registered `_input_handlers`.
  - `"approval_response"` (line 249): Dispatches user confirmation/rejection to policy engine.
- **Outgoing Broadcasts (`broadcast`, line 83):**
  - Sends arbitrary JSON events to all active authenticated client sockets via `encode_ws_frame`.

---

## 7. Scripts (`scripts/`)

- **Boot & Assembly:**
  - `scripts/build-boot-image.py` (22.9 KB): Assembles rootfs in `/tmp/lazy-os-rootfs`, creates compressed CPIO initramfs (`/tmp/lazy-os-boot.cpio.gz`), and GPT partitioned disk (`/tmp/lazy-disk.img`).
  - `scripts/boot-and-explore.py` (6.0 KB): Automates non-interactive QEMU serial boot and exploration.
  - `scripts/capture_screenshot.py` (1.5 KB): Dumps live framebuffer from QEMU monitor socket to PNG.
  - `scripts/send_guest_command.py` (1.2 KB): Sends keystrokes to guest console via QEMU monitor `sendkey`.
- **Yocto & Build Verification:**
  - `scripts/build-yocto.sh` (1.5 KB), `scripts/yocto-container.sh` (936 B), `scripts/check-env.sh` (2.9 KB)
  - Verification scripts: `verify-recipes.sh`, `verify-kernel-fragments.sh`, `verify-wic.sh`, `verify-docs.sh`, `verify-browser-image.sh`, `verify-reproducibility.sh`.
- **Generators & Helpers:**
  - `generate_capabilities.py`, `generate_40_tasks.py`, `generate_assistant_datasets.py`, `eval_models.py`, `handoff.sh`.

---

## 8. Yocto & Layer Structure (`yocto/`)

- Configuration: `yocto/kas/lazy-base.yml`, `yocto/kas/lazy-full.yml`
- Custom Layer: `yocto/meta-lazy/` (Layer Conf: `conf/layer.conf`, priority 10)
- Image Recipes:
  - `yocto/meta-lazy/images/lazy-image-base.bb`: Minimal non-model baseline image
  - `yocto/meta-lazy/images/lazy-image-full.bb`: Autonomous assistant image
- Kernel Config Fragments:
  - `yocto/meta-lazy/recipes-kernel/linux/linux-yocto_%.bbappend`
  - Fragments: `base-minimal.cfg`, `fs.cfg`, `laptop.cfg`, `memory.cfg`, `security.cfg`
- Service & Package Recipes:
  - `lazy-core_1.0.bb` (Lazy OS Python microservices)
  - `lazy-first-boot_1.0.bb` (systemd setup and partition init)
  - `lazy-browser_1.0.bb` (isolated Chromium profile)
  - `llama-cpp_b3800.bb`, `lazy-model-smollm_1.0.bb`, `lazy-voice-model_1.0.bb`, `vosk-api_0.3.45.bb`
- Disk Layout: `yocto/meta-lazy/wic/lazy-disk.wks`

---

## 9. Test Suite Layout (`tests/`)

- **Total Test Suites:** 22 Python test suites across `tests/unit/`, `tests/attacks/`, and `tests/integration/`
- **Unit Suites (`tests/unit/`):** 20 files
  - `test_audit.py`, `test_broker_comms.py`, `test_broker_web.py`, `test_brokers.py`, `test_browser_driver.py`, `test_contracts.py`, `test_dialogue.py`, `test_gateway.py`, `test_hud.py`, `test_latency_tuning.py`, `test_llm.py`, `test_niche_feed.py`, `test_outbox.py`, `test_planner_mock.py`, `test_policy.py`, `test_routines.py`, `test_secrets.py`, `test_systemd_units.py`, `test_tasks.py`, `test_voice.py`
- **Adversarial Security Suites (`tests/attacks/`):**
  - `test_attack_suite.py`: 70 prompt injection / capability jailbreak attack vectors
- **Integration Suites (`tests/integration/`):**
  - `test_pipeline_host.py`: Host pipeline integration testing
- **Assistant Benchmark Datasets (`tests/assistant/`):**
  - `benign.jsonl` (50 benign assistant prompts)
  - `injection.jsonl` (70 adversarial prompt injection attempts)
- **Task Fixtures (`tests/tasks/`):** 40 discrete YAML task definitions covering all 37 capabilities.
