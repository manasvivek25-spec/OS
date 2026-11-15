NEXT_ACTION: make verify-M4.4

## Current Milestone
M4.4: Safety & attack suite (>=60 attacks across prompt injections, L4 escapes, exfiltration, forwarding rules; unguarded baseline flag; >=50 benign queries; safety metrics CSV and report).

## Last 10 Completed Steps
1. Built RoutinesEngine and systemd timers (lazy-chores.timer, lazy-briefing.timer), verified M3.3 with 7 tests in tests/unit/test_routines.py (tag m-M3.3).
2. Built NicheFeedService with sandboxed fetcher (Rule F3 labelled data), pure Python TF-IDF cosine ranker, online feedback learning, 20% exploration share, structured reader citing item IDs, and strict faithfulness verifier, verified M3.4 with 13 tests in tests/results/M3.4.log (tag m-M3.4).
3. Fixed hermetic path resolution in FSBroker preventing duplicate path prefixing during document creation.
4. Authored and verified systemd sandboxing units across all 15 services, transient sandbox template and slice, security scoring auditor (10.0/10.0 score), verified M3.5 with 9 tests in tests/results/M3.5.log (tag m-M3.5).
5. Built lazy-outbox queue with JSON schema validation, undo window cancellation, send after delay, approval state machine, hourly rate limits, new-recipient policy, and attachment security, verified M4.1 with 14 tests in tests/results/M4.1.log (tag m-M4.1).
6. Implemented MaildirDriver, SMTPSinkDriver, LocalChatDriver, and disabled-by-default IMAP/Telegram drivers in src/lazy/brokers/comms_broker.py.
7. Built CommsBroker registering mail.list, mail.read, mail.draft, mail.send (L3 outbox-routed), chat.read, and chat.send (L3 outbox-routed), verified M4.2 with 11 tests in tests/results/M4.2.log (tag m-M4.2).
8. Built local fixture test portal (index, search, login, hidden prompt injections, downloadable file) in tests/fixtures/website/.
9. Implemented PureHTMLDOMParser extracting visible text, links, form fields, and flagging hidden text injections (style display:none, visibility:hidden, type=hidden, comments).
10. Built WebBroker with DomainAllowlist (config/allowlist.yaml), IsolatedBrowserDriver, and download quarantine (0600 permissions, SHA256 integrity), verified M4.3 with 9 tests in tests/results/M4.3.log (tag m-M4.3).

## Open Problems
None.

## Human Actions Pending
None.
