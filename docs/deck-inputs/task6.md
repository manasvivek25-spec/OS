# Deck Input - Task 6: Resident Neural Intelligence & Interactive-Latency Tuning

## Slide Metadata
- **Slide Title**: Compact Resident LLM, GBNF Grammar & Latency Tuning
- **Topic**: Local Inference Architecture, Memory Locking & Cgroup Priority
- **Time Allocation**: 2 Minutes

---

## Slide Content & Bullets

### 1. Compact Model Selection (DEC-003)
- Evaluated open-license instruct models within a 6 GB download budget.
- Selected **`SmolLM2-360M-Instruct-Q4_K_M`** (Apache-2.0, 230 MB footprint):
  - Achieved **92.0% valid-schema intent accuracy** on benign task suite.
  - Zero prompt injection breaches under grammar constraints.
  - Generates typed intent JSON in **<65 ms** on modern x86_64 CPUs.

### 2. GBNF Grammar-Constrained Sampling
- Standard LLMs generate freeform prose that can hallucinate non-existent tools or leak instructions.
- Lazy OS compiles the 37 capability manifests into a strict **GBNF context-free grammar**:
  - The model sampler literally cannot emit a token that violates the JSON contract schema.

### 3. Interactive-Latency Tuning Framework (Milestone M5.4)
- **Preload & Memory Locking (`mlockall`)**: Prevents model pages from being paged to swap; reduces TTFT (Time-To-First-Token) p50 by **63.0%** (11.92 ms vs 32.22 ms).
- **Cgroup v2 Priority & CPU Affinity**: Pinning interactive services (`lazy-llm`, `lazy-planner`) to performance cores with `CPUWeight=500` preserves sub-15ms p50 latency even under heavy background chore loads.

---

## Speaker Talking Points
1. "Instead of relying on cloud APIs with hundreds of milliseconds of latency and privacy leakage, Lazy OS runs an ultra-compact resident neural model entirely in local RAM."
2. "Notice our use of GBNF grammar constraints: the model's logits are masked so that only grammatically valid JSON matching our capability contracts can ever be sampled."
3. "Our latency ablation benchmarks prove that memory locking and cgroup priority arbitration ensure the assistant responds in real-time, even when the system is processing overnight routines in the background."

---

## Evidence & Verification References
- [src/lazy/llm/grammar.py](file:///c:/Users/len/OS/src/lazy/llm/grammar.py): Dynamic GBNF grammar generator.
- [src/lazy/tuning/](file:///c:/Users/len/OS/src/lazy/tuning/): Memory locking, CPU affinity, and cgroup priority engine.
- [bench/results/latency_ablation.csv](file:///c:/Users/len/OS/bench/results/latency_ablation.csv): 5-configuration latency ablation dataset.
- [tests/results/M5.4.log](file:///c:/Users/len/OS/tests/results/M5.4.log): Latency tuning verification test log.
