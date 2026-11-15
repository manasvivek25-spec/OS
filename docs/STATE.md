NEXT_ACTION: make verify-M2.4

## Current Milestone
M2.4: End-to-end text pipeline on host & 40-task suite in tests/tasks/*.yaml.

## Last 10 Completed Steps
1. Implemented PlannerInterface base contract factory in src/lazy/planner/base.py.
2. Generated and validated recorded-intent fixtures for all 37 Lazy OS capabilities in tests/fixtures/intents/.
3. Implemented MockPlanner with multi-strategy matching (query, capability, token overlap) in src/lazy/planner/mock.py.
4. Implemented comprehensive test suite in tests/unit/test_planner_mock.py verifying all 37 capabilities with 90% coverage.
5. Executed and passed exit test make verify-M2.1 saving tests/results/M2.1.log (tag m-M2.1).
6. Authored assistant evaluation datasets in tests/assistant/ (100 benign queries, 50 injection attacks).
7. Implemented GBNF context-free grammar generator enforcing intent.schema.json and 37 capabilities in src/lazy/llm/grammar.py.
8. Implemented LLMClient and LLMServerProcess with grammar constraints and safe fallback in src/lazy/llm/.
9. Evaluated model candidates against Section 4 criteria, verified SmolLM2-360M (230 MB, Apache-2.0, 92% accuracy, 0 injections), recorded in DEC-003, verified M2.2 (tag m-M2.2).
10. Built DialogueManager, CorrectionEngine (config/corrections.yaml), clarifying questions, plan views, narration, quiet mode, and golden-transcript tests in tests/unit/test_dialogue.py, verified M2.3 (tag m-M2.3).

## Open Problems
None.

## Human Actions Pending
None.
