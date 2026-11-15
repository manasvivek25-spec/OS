NEXT_ACTION: make verify-M3.4

## Current Milestone
M3.4: Niche feed: fetcher, reader (no-tools LLM call), TF-IDF ranking, feedback learning, exploration share, faithfulness checker.

## Last 10 Completed Steps
1. Built DialogueManager, CorrectionEngine (config/corrections.yaml), clarifying questions, plan views, narration, quiet mode, and golden-transcript tests in tests/unit/test_dialogue.py, verified M2.3 (tag m-M2.3).
2. Implemented full PipelineOrchestrator and LLMPlanner uniting gateway, dialogue, policy, snapshots, and brokers in src/lazy/pipeline/.
3. Authored and evaluated 40-task suite in tests/tasks/*.yaml across files, docs, code, admin, and hardware with 100% pass rate in mock and llm modes (bench/results/task_eval_{mock,llm}.csv).
4. Executed and passed host integration test suite in tests/integration/test_pipeline_host.py and make verify-M2.4, saved tests/results/M2.4.log (tag m-M2.4).
5. Designed, styled, and verified self-contained, 100% offline futuristic HUD (index.html, hud.css, hud.js) with wake animation, telemetry status strip, and approval cards, verified M3.1 (tag m-M3.1).
6. Implemented VoiceEngine, WakeDetector ("wake up, daddy's home"), STTEngine (Vosk), and TTSEngine (espeak-ng) in src/lazy/voice/.
7. Validated round-trip voice recognition with synthetic TTS audio, text fallback, and latency probes in tests/unit/test_voice.py, verified M3.2 (tag m-M3.2).
8. Implemented ChoreManager with transactional snapshot isolation and undo for tidy_downloads, backup_documents, digest_logs, check_updates in src/lazy/routines/chores.py.
9. Implemented BriefingGenerator parsing tasks.md, telemetry, chore receipts, and niche news in src/lazy/routines/briefing.py.
10. Built RoutinesEngine and systemd timers (lazy-chores.timer, lazy-briefing.timer), verified M3.3 with 7 tests in tests/unit/test_routines.py (tag m-M3.3).

## Open Problems
None.

## Human Actions Pending
None.
