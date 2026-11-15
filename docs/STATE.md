NEXT_ACTION: make verify-M3.5

## Current Milestone
M3.5: systemd sandbox units for every service (dedicated users, filesystem & syscall limits, cgroups, systemd-run code sandbox).

## Last 10 Completed Steps
1. Implemented full PipelineOrchestrator and LLMPlanner uniting gateway, dialogue, policy, snapshots, and brokers in src/lazy/pipeline/.
2. Authored and evaluated 40-task suite in tests/tasks/*.yaml across files, docs, code, admin, and hardware with 100% pass rate in mock and llm modes (bench/results/task_eval_{mock,llm}.csv).
3. Executed and passed host integration test suite in tests/integration/test_pipeline_host.py and make verify-M2.4, saved tests/results/M2.4.log (tag m-M2.4).
4. Designed, styled, and verified self-contained, 100% offline futuristic HUD (index.html, hud.css, hud.js) with wake animation, telemetry status strip, and approval cards, verified M3.1 (tag m-M3.1).
5. Implemented VoiceEngine, WakeDetector ("wake up, daddy's home"), STTEngine (Vosk), and TTSEngine (espeak-ng) in src/lazy/voice/.
6. Validated round-trip voice recognition with synthetic TTS audio, text fallback, and latency probes in tests/unit/test_voice.py, verified M3.2 (tag m-M3.2).
7. Implemented ChoreManager with transactional snapshot isolation and undo for tidy_downloads, backup_documents, digest_logs, check_updates in src/lazy/routines/chores.py.
8. Implemented BriefingGenerator parsing tasks.md, telemetry, chore receipts, and niche news in src/lazy/routines/briefing.py.
9. Built RoutinesEngine and systemd timers (lazy-chores.timer, lazy-briefing.timer), verified M3.3 with 7 tests in tests/unit/test_routines.py (tag m-M3.3).
10. Built NicheFeedService with sandboxed fetcher (Rule F3 labelled data), pure Python TF-IDF cosine ranker, online feedback learning, 20% exploration share, structured reader citing item IDs, and strict faithfulness verifier, verified M3.4 with 13 tests in tests/results/M3.4.log (tag m-M3.4).

## Open Problems
None.

## Human Actions Pending
None.
