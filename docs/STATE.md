NEXT_ACTION: make verify-M4.1

## Current Milestone
M4.1: lazy-outbox queue (delay window, undo window, approval state machine, hourly rate limits, new-recipient approval, attachment rules).

## Last 10 Completed Steps
1. Executed and passed host integration test suite in tests/integration/test_pipeline_host.py and make verify-M2.4, saved tests/results/M2.4.log (tag m-M2.4).
2. Designed, styled, and verified self-contained, 100% offline futuristic HUD (index.html, hud.css, hud.js) with wake animation, telemetry status strip, and approval cards, verified M3.1 (tag m-M3.1).
3. Implemented VoiceEngine, WakeDetector ("wake up, daddy's home"), STTEngine (Vosk), and TTSEngine (espeak-ng) in src/lazy/voice/.
4. Validated round-trip voice recognition with synthetic TTS audio, text fallback, and latency probes in tests/unit/test_voice.py, verified M3.2 (tag m-M3.2).
5. Implemented ChoreManager with transactional snapshot isolation and undo for tidy_downloads, backup_documents, digest_logs, check_updates in src/lazy/routines/chores.py.
6. Implemented BriefingGenerator parsing tasks.md, telemetry, chore receipts, and niche news in src/lazy/routines/briefing.py.
7. Built RoutinesEngine and systemd timers (lazy-chores.timer, lazy-briefing.timer), verified M3.3 with 7 tests in tests/unit/test_routines.py (tag m-M3.3).
8. Built NicheFeedService with sandboxed fetcher (Rule F3 labelled data), pure Python TF-IDF cosine ranker, online feedback learning, 20% exploration share, structured reader citing item IDs, and strict faithfulness verifier, verified M3.4 with 13 tests in tests/results/M3.4.log (tag m-M3.4).
9. Fixed hermetic path resolution in FSBroker preventing duplicate path prefixing during document creation.
10. Authored and verified systemd sandboxing units across all 15 services, transient sandbox template and slice, security scoring auditor (10.0/10.0 score), verified M3.5 with 9 tests in tests/results/M3.5.log (tag m-M3.5).

## Open Problems
None.

## Human Actions Pending
None.
