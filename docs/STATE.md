NEXT_ACTION: make verify-M4.2

## Current Milestone
M4.2: Comms broker (lazy-broker-comms): maildir driver, local SMTP sink, local chat service fixture, telegram driver stub; mail.list, mail.read, mail.draft, mail.send, chat.read, chat.send capabilities.

## Last 10 Completed Steps
1. Designed, styled, and verified self-contained, 100% offline futuristic HUD (index.html, hud.css, hud.js) with wake animation, telemetry status strip, and approval cards, verified M3.1 (tag m-M3.1).
2. Implemented VoiceEngine, WakeDetector ("wake up, daddy's home"), STTEngine (Vosk), and TTSEngine (espeak-ng) in src/lazy/voice/.
3. Validated round-trip voice recognition with synthetic TTS audio, text fallback, and latency probes in tests/unit/test_voice.py, verified M3.2 (tag m-M3.2).
4. Implemented ChoreManager with transactional snapshot isolation and undo for tidy_downloads, backup_documents, digest_logs, check_updates in src/lazy/routines/chores.py.
5. Implemented BriefingGenerator parsing tasks.md, telemetry, chore receipts, and niche news in src/lazy/routines/briefing.py.
6. Built RoutinesEngine and systemd timers (lazy-chores.timer, lazy-briefing.timer), verified M3.3 with 7 tests in tests/unit/test_routines.py (tag m-M3.3).
7. Built NicheFeedService with sandboxed fetcher (Rule F3 labelled data), pure Python TF-IDF cosine ranker, online feedback learning, 20% exploration share, structured reader citing item IDs, and strict faithfulness verifier, verified M3.4 with 13 tests in tests/results/M3.4.log (tag m-M3.4).
8. Fixed hermetic path resolution in FSBroker preventing duplicate path prefixing during document creation.
9. Authored and verified systemd sandboxing units across all 15 services, transient sandbox template and slice, security scoring auditor (10.0/10.0 score), verified M3.5 with 9 tests in tests/results/M3.5.log (tag m-M3.5).
10. Built lazy-outbox queue with JSON schema validation, undo window cancellation, send after delay, approval state machine, hourly rate limits, new-recipient policy, and attachment security, verified M4.1 with 14 tests in tests/results/M4.1.log (tag m-M4.1).

## Open Problems
None.

## Human Actions Pending
None.
