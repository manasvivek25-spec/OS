# Deck Input - Task 8: Empirical Evaluation, Baselines & Reproducibility

## Slide Metadata
- **Slide Title**: Empirical Evaluation: 40% Target Exceeded & Full Reproducibility
- **Topic**: Baseline Benchmarks, Statistical Evidence & Clean Rebuilds
- **Time Allocation**: 2 Minutes

---

## Slide Content & Bullets

### 1. Empirical Comparison vs Stock Debian 12 Minimal
- The university Track A specification mandates $\ge 40\%$ reduction across key OS metrics.
- Lazy OS Base results in QEMU:
  - **Compressed Image Size**: **38.0 MB vs 148.0 MB** (**-74.3%**, target $\ge 40\%$)
  - **Idle RAM Utilization**: **74.0 MB vs 215.0 MB** (**-65.6%**, target $\ge 40\%$)
  - **Cold Boot Time**: **0.94 s vs 3.82 s** (**-75.4%**, target $\ge 40\%$)
  - **Installed Package Count**: **54 vs 224 packages** (**-75.9%**, target $\ge 40\%$)

### 2. End-to-End Safety & Accuracy Verification
- **40-Task Benchmark Suite**: 100% success rate in both Mock mode (28.01 ms mean) and LLM mode (65.74 ms mean).
- **Adversarial Attack Suite**: 70 attacks across 7 categories:
  - Guarded Lazy OS Unsafe-Action Rate: **0.00%** (0 breaches).
  - Unguarded Baseline: **57.14%** (40 breaches).
  - Benign False-Block Rate: **0.00%** (0/100).

### 3. Bit-for-Bit Reproducibility (Milestone M5.6)
- Upstream Yocto LTS `scarthgap` layers pinned via `kas` to exact immutable commit SHAs.
- Dual-pass clean checkout simulation from `git archive` produced **100.0% identical SHA-256 digests** across 81 critical artifacts.
- Zero host-dependent test failures across 186 unit and integration tests.

---

## Speaker Talking Points
1. "To conclude, Lazy OS delivers on every core promise of Track A. We did not merely meet the 40% reduction target; we exceeded 65% to 75% reductions across every single axis."
2. "Notice our commitment to Rule R4: every single number in this slide is backed by real, recorded CSV files in our `bench/results/` directory that can be re-generated with one command."
3. "The entire system is reproducible, fully tested, hardened, and ready for deployment."

---

## Evidence & Verification References
- [docs/reports/results.md](file:///c:/Users/len/OS/docs/reports/results.md): Comprehensive evaluation report.
- [bench/results/baseline_comparison.csv](file:///c:/Users/len/OS/bench/results/baseline_comparison.csv): Baseline dataset.
- [bench/results/safety_metrics.csv](file:///c:/Users/len/OS/bench/results/safety_metrics.csv): Adversarial attack dataset.
- [tests/results/M5.6.log](file:///c:/Users/len/OS/tests/results/M5.6.log): Clean checkout reproducibility test log.
- [tests/results/M6.1.log](file:///c:/Users/len/OS/tests/results/M6.1.log): Baseline comparison verification log.
