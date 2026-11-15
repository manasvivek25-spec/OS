# Lazy OS Master Makefile
SHELL := /bin/bash
export PYTHONPATH := $(CURDIR)/src:$(CURDIR):$(PYTHONPATH)
PYTHON ?= python3
VENV ?= .venv
VENV_BIN ?= $(VENV)/bin
PYTEST ?= $(if $(wildcard $(VENV_BIN)/pytest),$(VENV_BIN)/pytest,pytest)

.PHONY: all setup status verify verify-image eval-tasks eval-llm eval demo image-base image-full handoff clean

all: status

# 1. Setup host dependencies
setup:
	@chmod +x scripts/*.sh
	@./scripts/setup-host.sh

# 2. Status target - displays milestone table from docs/PLAN.md per M0.1 exit condition
status:
	@echo "=== Lazy OS Milestone Status ==="
	@cat docs/PLAN.md

# 3. Target to verify a specific milestone: make verify-M0.1, make verify-M0.2, etc.
verify-%:
	@mkdir -p tests/results
	@echo "Running verification for $*..."
	@set -o pipefail; $(MAKE) run-verify-$* 2>&1 | tee tests/results/$*.log
	@echo "Verification for $* completed. Log saved to tests/results/$*.log"

# M0.1 exit test runner
run-verify-M0.1:
	@test -f Makefile
	@test -f README.md
	@test -f LICENSE
	@test -f docs/SPEC.md
	@test -f docs/BUILD_PROMPT.md
	@test -f docs/PLAN.md
	@test -f docs/STATE.md
	@test -f docs/DECISIONS.md
	@test -f docs/ASSUMPTIONS.md
	@test -f docs/KNOWN_ISSUES.md
	@test -f docs/LICENCES.md
	@test -f docs/PACKAGES.md
	@test -f docs/ARCHITECTURE.md
	@test -f docs/HARDWARE-CONTROL.md
	@test -f scripts/check-env.sh
	@chmod +x scripts/check-env.sh
	@./scripts/check-env.sh
	@test -f docs/ENV.md
	@echo "Milestone Table:"
	@$(MAKE) status
	@echo "M0.1 VERIFICATION SUCCESSFUL"

# Placeholder runner for milestone verifications
run-verify-M0.2:
	@$(PYTHON) -m pytest tests/unit/test_contracts.py -v
run-verify-M0.3:
	@./scripts/verify-m03.sh
run-verify-M1.1:
	@$(PYTHON) -m pytest tests/unit/test_audit.py -v
run-verify-M1.2:
	@$(PYTHON) -m pytest tests/unit/test_policy.py -v --cov=lazy.policy --cov-report=term-missing
run-verify-M1.3:
	@$(PYTHON) -m pytest tests/unit/test_tasks.py -v --cov=lazy.tasks --cov-report=term-missing
run-verify-M1.4:
	@$(PYTHON) -m pytest tests/unit/test_brokers.py -v
run-verify-M1.5:
	@$(PYTHON) -m pytest tests/unit/test_secrets.py -v
run-verify-M1.6:
	@$(PYTHON) -m pytest tests/unit/test_gateway.py -v
run-verify-M2.1:
	@$(PYTHON) -m pytest tests/unit/test_planner_mock.py -v
run-verify-M2.2:
	@$(PYTHON) -m pytest tests/unit/test_llm.py -v
run-verify-M2.3:
	@$(PYTHON) -m pytest tests/unit/test_dialogue.py -v
run-verify-M2.4:
	@$(PYTHON) -m pytest tests/integration/test_pipeline_host.py -v
run-verify-M3.1:
	@$(PYTHON) -m pytest tests/unit/test_hud.py -v
run-verify-M3.2:
	@$(PYTHON) -m pytest tests/unit/test_voice.py -v
run-verify-M3.3:
	@$(PYTHON) -m pytest tests/unit/test_routines.py -v
run-verify-M3.4:
	@$(PYTHON) -m pytest tests/unit/test_niche_feed.py -v
run-verify-M3.5:
	@$(PYTHON) -m pytest tests/unit/test_systemd_units.py -v
run-verify-M4.1:
	@$(PYTHON) -m pytest tests/unit/test_outbox.py -v
run-verify-M4.2:
	@$(PYTHON) -m pytest tests/unit/test_broker_comms.py -v
run-verify-M4.3:
	@$(PYTHON) -m pytest tests/unit/test_broker_web.py -v
run-verify-M4.4:
	@$(PYTHON) -m pytest tests/attacks/test_attack_suite.py -v
run-verify-M5.1:
	@./scripts/verify-kernel-fragments.sh
run-verify-M5.2:
	@./scripts/verify-recipes.sh
run-verify-M5.3:
	@./scripts/verify-wic.sh
run-verify-M5.4:
	@./scripts/verify-latency-tuning.sh
run-verify-M5.5:
	@./scripts/verify-browser-image.sh
run-verify-M5.6:
	@./scripts/verify-reproducibility.sh
run-verify-M6.1:
	@$(PYTHON) bench/scripts/eval_baselines.py
run-verify-M6.2:
	@$(PYTHON) bench/scripts/eval_full_suite.py
run-verify-M6.3:
	@./scripts/verify-docs.sh
run-verify-M6.4:
	@$(MAKE) verify

# 4. Master verify (all non-LLM, non-image tests)
verify:
	@mkdir -p tests/results
	@echo "Running all non-LLM, non-image verification suites..."
	@set -o pipefail; $(PYTEST) tests/unit tests/attacks -v 2>&1 | tee tests/results/verify.log
	@echo "All verify tests completed."

verify-image:
	@mkdir -p tests/results
	@echo "Verifying image in QEMU over SSH..."
	@$(PYTHON) -m pytest tests/integration/image/ -v | tee tests/results/verify-image.log

eval-tasks:
	@mkdir -p tests/results
	@echo "Running evaluation on 40-task suite..."
	@$(PYTHON) bench/scripts/run_task_eval.py --mode=mock | tee tests/results/eval-tasks.log

eval-llm:
	@mkdir -p tests/results
	@echo "Running LLM evaluation benchmarks..."
	@$(PYTHON) bench/scripts/eval_assistant.py | tee tests/results/eval-llm.log

eval: eval-tasks eval-llm
	@echo "Full evaluation suite complete."

demo:
	@$(PYTHON) src/lazy/demo_runner.py

image-base:
	@./scripts/build-yocto.sh base

image-full:
	@./scripts/build-yocto.sh full

handoff:
	@chmod +x scripts/handoff.sh
	@./scripts/handoff.sh

clean:
	@rm -rf .pytest_cache tests/results/*.tmp build-logs/*
