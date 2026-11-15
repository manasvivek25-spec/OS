"""40-task benchmark and evaluation runner for Lazy OS pipeline."""
from __future__ import annotations

import argparse
import csv
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List

import yaml

from lazy.pipeline.orchestrator import PipelineOrchestrator
from lazy.planner.llm_planner import LLMPlanner
from lazy.planner.mock import MockPlanner

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TASKS_DIR = REPO_ROOT / "tests" / "tasks"
BENCH_RESULTS_DIR = REPO_ROOT / "bench" / "results"
BENCH_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
FIXTURE_SYSFS = REPO_ROOT / "tests" / "fixtures" / "sysfs"


def run_evaluation(mode: str = "mock") -> Dict[str, Any]:
    print(f"=== Lazy OS 40-Task Benchmark (Mode: {mode.upper()}) ===")
    task_files = sorted(TASKS_DIR.glob("*.yaml"))
    assert len(task_files) == 40, f"Expected 40 tasks, found {len(task_files)}"

    # Setup isolated temporary workspace and audit log
    temp_dir = Path(tempfile.mkdtemp(prefix="lazy_bench_"))
    workspace = temp_dir / "workspace"
    workspace.mkdir()
    audit_file = temp_dir / "audit.log"

    planner = LLMPlanner(mock_fallback=True) if mode == "llm" else MockPlanner()
    pipeline = PipelineOrchestrator(
        workspace_dir=workspace,
        audit_path=audit_file,
        planner=planner,
        sysfs_root=FIXTURE_SYSFS,
    )

    results: List[Dict[str, Any]] = []
    latencies: List[float] = []
    success_count = 0

    print(f"{'ID':<28} | {'Category':<10} | {'Capability':<18} | {'Tier':<4} | {'Status':<9} | {'Latency (ms)':<12}")
    print("-" * 92)

    for tf in task_files:
        with open(tf, "r", encoding="utf-8") as f:
            task = yaml.safe_load(f)

        t_id = task["task_id"]
        category = task["category"]
        query = task["query"]
        expected_cap = task["expected_capability"]
        tier = task["tier"]

        t0 = time.perf_counter()
        res = pipeline.execute_text(query, auto_approve=True)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        latencies.append(elapsed_ms)

        is_success = res.status == "completed"
        if is_success:
            success_count += 1

        print(f"{t_id:<28} | {category:<10} | {expected_cap:<18} | {tier:<4} | {res.status:<9} | {elapsed_ms:>10.2f} ms")

        results.append({
            "task_id": t_id,
            "category": category,
            "expected_capability": expected_cap,
            "tier": tier,
            "status": res.status,
            "latency_ms": round(elapsed_ms, 2),
            "error": res.error or "",
        })

    # Metrics summary
    latencies.sort()
    mean_lat = sum(latencies) / len(latencies)
    p50_lat = latencies[len(latencies) // 2]
    p95_lat = latencies[int(len(latencies) * 0.95)]
    success_rate = (success_count / len(task_files)) * 100.0

    print("=" * 92)
    print(f"Total Tasks: {len(task_files)} | Passed: {success_count} ({success_rate:.1f}%) | Mean: {mean_lat:.2f} ms | p50: {p50_lat:.2f} ms | p95: {p95_lat:.2f} ms")

    # Save CSV
    csv_file = BENCH_RESULTS_DIR / f"task_eval_{mode}.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["task_id", "category", "expected_capability", "tier", "status", "latency_ms", "error"])
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    print(f"Results CSV written to {csv_file}")

    # Cleanup temp dir
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass

    return {
        "mode": mode,
        "total": len(task_files),
        "passed": success_count,
        "success_rate": success_rate,
        "mean_ms": mean_lat,
        "p50_ms": p50_lat,
        "p95_ms": p95_lat,
    }


def main():
    parser = argparse.ArgumentParser(description="Lazy OS 40-Task Benchmark Runner")
    parser.add_argument("--mode", choices=["mock", "llm"], default="mock", help="Execution mode (mock or llm)")
    args = parser.parse_args()
    summary = run_evaluation(mode=args.mode)
    if summary["passed"] != summary["total"]:
        exit(1)


if __name__ == "__main__":
    main()
