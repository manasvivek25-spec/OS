NEXT_ACTION: make verify-M5.1

## Current Milestone
M5.1: Custom Linux Kernel Fragments (yocto/meta-lazy/recipes-kernel/linux/files/: base-minimal.cfg, memory.cfg, fs.cfg, security.cfg, laptop.cfg; Kconfig audit script; image size & boot benchmark).

## Last 10 Completed Steps
1. Built NicheFeedService with sandboxed fetcher (Rule F3 labelled data), pure Python TF-IDF cosine ranker, online feedback learning, 20% exploration share, structured reader citing item IDs, and strict faithfulness verifier, verified M3.4 with 13 tests in tests/results/M3.4.log (tag m-M3.4).
2. Fixed hermetic path resolution in FSBroker preventing duplicate path prefixing during document creation.
3. Authored and verified systemd sandboxing units across all 15 services, transient sandbox template and slice, security scoring auditor (10.0/10.0 score), verified M3.5 with 9 tests in tests/results/M3.5.log (tag m-M3.5).
4. Built lazy-outbox queue with JSON schema validation, undo window cancellation, send after delay, approval state machine, hourly rate limits, new-recipient policy, and attachment security, verified M4.1 with 14 tests in tests/results/M4.1.log (tag m-M4.1).
5. Implemented MaildirDriver, SMTPSinkDriver, LocalChatDriver, and disabled-by-default IMAP/Telegram drivers in src/lazy/brokers/comms_broker.py.
6. Built CommsBroker registering mail.list, mail.read, mail.draft, mail.send (L3 outbox-routed), chat.read, and chat.send (L3 outbox-routed), verified M4.2 with 11 tests in tests/results/M4.2.log (tag m-M4.2).
7. Built local fixture test portal (index, search, login, hidden prompt injections, downloadable file) in tests/fixtures/website/.
8. Implemented PureHTMLDOMParser extracting visible text, links, form fields, and flagging hidden text injections (style display:none, visibility:hidden, type=hidden, comments).
9. Built WebBroker with DomainAllowlist (config/allowlist.yaml), IsolatedBrowserDriver, and download quarantine (0600 permissions, SHA256 integrity), verified M4.3 with 9 tests in tests/results/M4.3.log (tag m-M4.3).
10. Built safety attack evaluator (bench/scripts/run_safety_eval.py) testing 70 attacks across 7 categories and 100 benign queries, generating bench/results/safety_metrics.csv (Guarded unsafe action rate 0.0%, Unguarded baseline 57.14%, Benign false block 0.0%), verified M4.4 with 6 tests in tests/results/M4.4.log (tag m-M4.4).

## Open Problems
None.

## Human Actions Pending
None.
