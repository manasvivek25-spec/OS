NEXT_ACTION: make verify-M3.1

## Current Milestone
M3.1: HUD: transcript, plan view, step status, approvals diff, status strip, wake animation, futuristic offline style.

## Last 10 Completed Steps
1. Implemented MockPlanner with multi-strategy matching (query, capability, token overlap) in src/lazy/planner/mock.py.
2. Implemented comprehensive test suite in tests/unit/test_planner_mock.py verifying all 37 capabilities with 90% coverage.
3. Executed and passed exit test make verify-M2.1 saving tests/results/M2.1.log (tag m-M2.1).
4. Authored assistant evaluation datasets in tests/assistant/ (100 benign queries, 50 injection attacks).
5. Implemented GBNF context-free grammar generator enforcing intent.schema.json and 37 capabilities in src/lazy/llm/grammar.py.
6. Evaluated model candidates against Section 4 criteria, verified SmolLM2-360M (230 MB, Apache-2.0, 92% accuracy, 0 injections), recorded in DEC-003, verified M2.2 (tag m-M2.2).
7. Built DialogueManager, CorrectionEngine (config/corrections.yaml), clarifying questions, plan views, narration, quiet mode, and golden-transcript tests in tests/unit/test_dialogue.py, verified M2.3 (tag m-M2.3).
8. Implemented full PipelineOrchestrator and LLMPlanner uniting gateway, dialogue, policy, snapshots, and brokers in src/lazy/pipeline/.
9. Authored and evaluated 40-task suite in tests/tasks/*.yaml across files, docs, code, admin, and hardware with 100% pass rate in mock and llm modes (bench/results/task_eval_{mock,llm}.csv).
10. Executed and passed host integration test suite in tests/integration/test_pipeline_host.py and make verify-M2.4, saved tests/results/M2.4.log (tag m-M2.4).

## Open Problems
None.

## Human Actions Pending
None.
