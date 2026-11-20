#!/usr/bin/env bash
# =============================================================================
# Lazy OS — Track A ML Benchmark Script (Role B)
# =============================================================================
# Runs standardized, repeatable inference benchmarks against:
#   Qwen2.5-1.5B-Instruct-Q4_K_M.gguf (Apache-2.0)
#
# Usage:  ./scripts/run_ml_bench.sh [--output /path/to/output.json]
#
# Outputs JSON with:
#   ttft_ms          — Time-to-First-Token (ms)
#   prompt_tok_s     — Prompt evaluation tokens/second
#   gen_tok_s        — Generation tokens/second
#   peak_rss_mb      — Peak resident set size (MB)
#   cpu_util_pct     — CPU utilization during inference (%)
#   model            — Model name
#   engine           — Inference engine
#   quantization     — Quantization method
#
# This script is designed so Role C can run the exact same benchmark
# on both Lazy OS and stock Debian 12 for fair comparison.
# =============================================================================

set -euo pipefail

# --- Configuration ---
MODEL_SEARCH_PATHS=(
    "/usr/share/lazy/models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"
    "/var/lib/lazy/models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"
    "/build/models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"
    "/data/models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"
)
THREADS=4
CTX_SIZE=2048
N_PREDICT=128
PROMPT="Explain the key benefits of edge computing for real-time AI inference in three sentences."
BENCH_PROMPT_TOKENS=512
BENCH_GEN_TOKENS=128
OUTPUT_FILE=""
NUM_RUNS=3

# --- Parse Arguments ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --output|-o)   OUTPUT_FILE="$2"; shift 2 ;;
        --runs|-n)     NUM_RUNS="$2"; shift 2 ;;
        --threads|-t)  THREADS="$2"; shift 2 ;;
        *)             echo "Unknown option: $1"; exit 1 ;;
    esac
done

# --- Locate Model ---
MODEL_PATH="${LAZY_MODEL_PATH:-}"
if [ -z "$MODEL_PATH" ]; then
    for p in "${MODEL_SEARCH_PATHS[@]}"; do
        if [ -f "$p" ]; then
            MODEL_PATH="$p"
            break
        fi
    done
fi

if [ -z "$MODEL_PATH" ] || [ ! -f "$MODEL_PATH" ]; then
    echo '{"error": "Model file not found. Set LAZY_MODEL_PATH or place model in search paths."}' >&2
    exit 1
fi

echo "=== Lazy OS ML Benchmark ===" >&2
echo "Model: $MODEL_PATH" >&2
echo "Threads: $THREADS | Context: $CTX_SIZE | Predict: $N_PREDICT | Runs: $NUM_RUNS" >&2

# --- Locate Binaries ---
LLAMA_BENCH=$(command -v llama-bench 2>/dev/null || echo "")
LLAMA_SERVER=$(command -v llama-server 2>/dev/null || echo "")

# --- Part 1: llama-bench (if available) ---
BENCH_PP=""
BENCH_TG=""
if [ -n "$LLAMA_BENCH" ]; then
    echo "--- Running llama-bench (pp=$BENCH_PROMPT_TOKENS, tg=$BENCH_GEN_TOKENS) ---" >&2
    BENCH_OUTPUT=$("$LLAMA_BENCH" \
        -m "$MODEL_PATH" \
        -t "$THREADS" \
        -ngl 0 \
        -p "$BENCH_PROMPT_TOKENS" \
        -n "$BENCH_GEN_TOKENS" \
        -r "$NUM_RUNS" \
        2>&1) || true

    # Parse llama-bench output for tok/s values
    BENCH_PP=$(echo "$BENCH_OUTPUT" | grep -oP 'pp\d+.*?(\d+\.\d+)\s*±' | head -1 | grep -oP '\d+\.\d+' | head -1 || echo "")
    BENCH_TG=$(echo "$BENCH_OUTPUT" | grep -oP 'tg\d+.*?(\d+\.\d+)\s*±' | head -1 | grep -oP '\d+\.\d+' | head -1 || echo "")
    echo "llama-bench: pp=$BENCH_PP tok/s, tg=$BENCH_TG tok/s" >&2
else
    echo "llama-bench not found, skipping batch benchmark" >&2
fi

# --- Part 2: Timed llama-server inference for TTFT ---
TTFT_MS="0"
GEN_TOK_S="0"
PROMPT_TOK_S="0"
PEAK_RSS_MB="0"
CPU_UTIL="0"

if [ -n "$LLAMA_SERVER" ]; then
    echo "--- Starting llama-server for TTFT measurement ---" >&2

    # Start server in background
    "$LLAMA_SERVER" -m "$MODEL_PATH" --host 127.0.0.1 --port 18080 \
        -t "$THREADS" -c "$CTX_SIZE" -ngl 0 --mlock &
    SERVER_PID=$!

    # Wait for server to become healthy
    WAIT_START=$(date +%s%N)
    for i in $(seq 1 30); do
        if curl -sf http://127.0.0.1:18080/health >/dev/null 2>&1; then
            break
        fi
        sleep 1
    done

    # Measure memory before inference
    RSS_BEFORE=$(cat /proc/$SERVER_PID/status 2>/dev/null | grep VmRSS | awk '{print $2}' || echo "0")

    # Record CPU time before
    CPU_BEFORE=$(cat /proc/$SERVER_PID/stat 2>/dev/null | awk '{print $14+$15}' || echo "0")
    WALL_BEFORE=$(date +%s%N)

    # Run timed inference
    TTFT_RUNS=()
    GEN_RUNS=()
    PROMPT_RUNS=()

    for run in $(seq 1 "$NUM_RUNS"); do
        INFER_START=$(date +%s%N)

        RESPONSE=$(curl -sf http://127.0.0.1:18080/completion \
            -H "Content-Type: application/json" \
            -d "{
                \"prompt\": \"<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n${PROMPT}<|im_end|>\n<|im_start|>assistant\n\",
                \"n_predict\": $N_PREDICT,
                \"temperature\": 0.1,
                \"stop\": [\"<|im_end|>\"]
            }" 2>/dev/null) || true

        INFER_END=$(date +%s%N)

        if [ -n "$RESPONSE" ]; then
            # Extract timings from llama.cpp response
            TIMINGS_PP=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); t=d.get('timings',{}); print(t.get('prompt_per_second',0))" 2>/dev/null || echo "0")
            TIMINGS_TG=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); t=d.get('timings',{}); print(t.get('predicted_per_second',0))" 2>/dev/null || echo "0")
            TIMINGS_TTFT=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); t=d.get('timings',{}); print(t.get('prompt_ms',0))" 2>/dev/null || echo "0")

            TTFT_RUNS+=("$TIMINGS_TTFT")
            GEN_RUNS+=("$TIMINGS_TG")
            PROMPT_RUNS+=("$TIMINGS_PP")

            echo "  Run $run: TTFT=${TIMINGS_TTFT}ms, pp=${TIMINGS_PP} tok/s, tg=${TIMINGS_TG} tok/s" >&2
        fi
    done

    # Compute averages
    if [ ${#TTFT_RUNS[@]} -gt 0 ]; then
        TTFT_MS=$(python3 -c "vals=[${TTFT_RUNS[*]// /,}]; print(f'{sum(vals)/len(vals):.1f}')" 2>/dev/null || echo "0")
        GEN_TOK_S=$(python3 -c "vals=[${GEN_RUNS[*]// /,}]; print(f'{sum(vals)/len(vals):.2f}')" 2>/dev/null || echo "0")
        PROMPT_TOK_S=$(python3 -c "vals=[${PROMPT_RUNS[*]// /,}]; print(f'{sum(vals)/len(vals):.2f}')" 2>/dev/null || echo "0")
    fi

    # Measure peak RSS
    PEAK_RSS_KB=$(cat /proc/$SERVER_PID/status 2>/dev/null | grep VmHWM | awk '{print $2}' || echo "0")
    PEAK_RSS_MB=$(python3 -c "print(f'{int(${PEAK_RSS_KB})/1024:.1f}')" 2>/dev/null || echo "0")

    # Measure CPU utilization
    WALL_AFTER=$(date +%s%N)
    CPU_AFTER=$(cat /proc/$SERVER_PID/stat 2>/dev/null | awk '{print $14+$15}' || echo "0")
    WALL_ELAPSED=$(python3 -c "print(f'{(${WALL_AFTER}-${WALL_BEFORE})/1e9:.2f}')" 2>/dev/null || echo "1")
    CPU_TICKS=$(python3 -c "print(${CPU_AFTER}-${CPU_BEFORE})" 2>/dev/null || echo "0")
    CLK_TCK=$(getconf CLK_TCK 2>/dev/null || echo "100")
    CPU_UTIL=$(python3 -c "
wall=${WALL_ELAPSED}; ticks=${CPU_TICKS}; hz=${CLK_TCK}
if wall > 0: print(f'{(ticks/hz)/wall*100:.1f}')
else: print('0.0')
" 2>/dev/null || echo "0")

    # Cleanup
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
else
    echo "llama-server not found, skipping TTFT measurement" >&2
fi

# --- Use llama-bench values as fallback if server measurement was zero ---
if [ "$PROMPT_TOK_S" = "0" ] && [ -n "$BENCH_PP" ]; then
    PROMPT_TOK_S="$BENCH_PP"
fi
if [ "$GEN_TOK_S" = "0" ] && [ -n "$BENCH_TG" ]; then
    GEN_TOK_S="$BENCH_TG"
fi

# --- Generate JSON Output ---
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
JSON_OUTPUT=$(cat <<EOF
{
  "benchmark": "lazy-os-ml-bench",
  "timestamp": "$TIMESTAMP",
  "model": "Qwen2.5-1.5B-Instruct-Q4_K_M",
  "model_path": "$MODEL_PATH",
  "license": "Apache-2.0",
  "engine": "llama.cpp",
  "quantization": "Q4_K_M",
  "parameters": "1.5B",
  "hardware": {
    "threads": $THREADS,
    "context_size": $CTX_SIZE,
    "simd": "AVX2",
    "gpu_layers": 0
  },
  "config": {
    "n_predict": $N_PREDICT,
    "num_runs": $NUM_RUNS,
    "bench_pp_tokens": $BENCH_PROMPT_TOKENS,
    "bench_tg_tokens": $BENCH_GEN_TOKENS
  },
  "results": {
    "ttft_ms": $TTFT_MS,
    "prompt_tok_s": $PROMPT_TOK_S,
    "gen_tok_s": $GEN_TOK_S,
    "peak_rss_mb": $PEAK_RSS_MB,
    "cpu_util_pct": $CPU_UTIL
  }
}
EOF
)

echo "$JSON_OUTPUT"

if [ -n "$OUTPUT_FILE" ]; then
    echo "$JSON_OUTPUT" > "$OUTPUT_FILE"
    echo "Results written to $OUTPUT_FILE" >&2
fi

echo "=== Benchmark Complete ===" >&2
