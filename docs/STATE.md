NEXT_ACTION: make verify-M3.3

## Current Milestone
M3.3: Routines: wake sequence, briefing, chores in snapshot with undo, systemd timers.

## Last 10 Completed Steps
1. Authored assistant evaluation datasets in tests/assistant/ (100 benign queries, 50 injection attacks).
2. Implemented GBNF context-free grammar generator enforcing intent.schema.json and 37 capabilities in src/lazy/llm/grammar.py.
3. Evaluated model candidates against Section 4 criteria, verified SmolLM2-360M (230 MB, Apache-2.0, 92% accuracy, 0 injections), recorded in DEC-003, verified M2.2 (tag m-M2.2).
4. Built DialogueManager, CorrectionEngine (config/corrections.yaml), clarifying questions, plan views, narration, quiet mode, and golden-transcript tests in tests/unit/test_dialogue.py, verified M2.3 (tag m-M2.3).
5. Implemented full PipelineOrchestrator and LLMPlanner uniting gateway, dialogue, policy, snapshots, and brokers in src/lazy/pipeline/.
6. Authored and evaluated 40-task suite in tests/tasks/*.yaml across files, docs, code, admin, and hardware with 100% pass rate in mock and llm modes (bench/results/task_eval_{mock,llm}.csv).
7. Executed and passed host integration test suite in tests/integration/test_pipeline_host.py and make verify-M2.4, saved tests/results/M2.4.log (tag m-M2.4).
8. Designed, styled, and verified self-contained, 100% offline futuristic HUD (index.html, hud.css, hud.js) with wake animation, telemetry status strip, and approval cards, verified M3.1 (tag m-M3.1).
9. Implemented VoiceEngine, WakeDetector ("wake up, daddy's home"), STTEngine (Vosk), and TTSEngine (espeak-ng) in src/lazy/voice/.
10. Validated round-trip voice recognition with synthetic TTS audio, text fallback, and latency probes in tests/unit/test_voice.py, verified M3.2 (tag m-M3.2).

## Open Problems
None.

## Human Actions Pending
None.
