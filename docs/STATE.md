NEXT_ACTION: make verify-M2.3

## Current Milestone
M2.3: Dialogue manager: clarifying questions, plan view, narration, pause/stop/redirect/undo, YAML correction rules, quiet mode.

## Last 10 Completed Steps
1. Built lazy-gateway: HUDTokenManager with constant-time verification, RPCBus JSON-RPC 2.0 router, RFC 6455 WebSocket protocol server, verified M1.6 with 21 unit tests (tag m-M1.6).
2. Implemented PlannerInterface base contract factory in src/lazy/planner/base.py.
3. Generated and validated recorded-intent fixtures for all 37 Lazy OS capabilities in tests/fixtures/intents/.
4. Implemented MockPlanner with multi-strategy matching (query, capability, token overlap) in src/lazy/planner/mock.py.
5. Implemented comprehensive test suite in tests/unit/test_planner_mock.py verifying all 37 capabilities with 90% coverage.
6. Executed and passed exit test make verify-M2.1 saving tests/results/M2.1.log (tag m-M2.1).
7. Authored assistant evaluation datasets in tests/assistant/ (100 benign queries, 50 injection attacks).
8. Implemented GBNF context-free grammar generator enforcing intent.schema.json and 37 capabilities in src/lazy/llm/grammar.py.
9. Implemented LLMClient and LLMServerProcess with grammar constraints and safe fallback in src/lazy/llm/.
10. Evaluated model candidates against Section 4 criteria, verified SmolLM2-360M (230 MB, Apache-2.0, 92% accuracy, 0 injections), recorded in DEC-003, verified M2.2 (tag m-M2.2).

## Open Problems
None.

## Human Actions Pending
None.
