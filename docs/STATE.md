NEXT_ACTION: make verify-M3.2

## Current Milestone
M3.2: Voice: wake phrase, STT (Vosk), TTS (espeak-ng), fallback, latency probes.

## Last 10 Completed Steps
1. Executed and passed exit test make verify-M2.1 saving tests/results/M2.1.log (tag m-M2.1).
2. Authored assistant evaluation datasets in tests/assistant/ (100 benign queries, 50 injection attacks).
3. Implemented GBNF context-free grammar generator enforcing intent.schema.json and 37 capabilities in src/lazy/llm/grammar.py.
4. Evaluated model candidates against Section 4 criteria, verified SmolLM2-360M (230 MB, Apache-2.0, 92% accuracy, 0 injections), recorded in DEC-003, verified M2.2 (tag m-M2.2).
5. Built DialogueManager, CorrectionEngine (config/corrections.yaml), clarifying questions, plan views, narration, quiet mode, and golden-transcript tests in tests/unit/test_dialogue.py, verified M2.3 (tag m-M2.3).
6. Implemented full PipelineOrchestrator and LLMPlanner uniting gateway, dialogue, policy, snapshots, and brokers in src/lazy/pipeline/.
7. Authored and evaluated 40-task suite in tests/tasks/*.yaml across files, docs, code, admin, and hardware with 100% pass rate in mock and llm modes (bench/results/task_eval_{mock,llm}.csv).
8. Executed and passed host integration test suite in tests/integration/test_pipeline_host.py and make verify-M2.4, saved tests/results/M2.4.log (tag m-M2.4).
9. Designed, styled, and verified self-contained, 100% offline futuristic HUD (index.html, hud.css, hud.js) with wake animation, telemetry status strip, and approval cards.
10. Executed and passed make verify-M3.1 saving tests/results/M3.1.log (tag m-M3.1).

## Open Problems
None.

## Human Actions Pending
None.
