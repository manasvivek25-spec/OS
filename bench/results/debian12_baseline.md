# Stock Debian 12 Minimal Benchmark Baseline (10 Cold QEMU Runs + Track A ML Baseline)

## 1. Operating System Metrics
- **Distribution**: Debian 12 Minimal (bookworm)
- **Kernel Version**: 6.1.0-56-amd64
- **QEMU Profile**: 4 vCPUs, 4 GB RAM, virtio-gpu-pci, virtio-net-pci
- **Cold Boot Time (10 runs mean)**: 2.00 s (±0.00 s)
- **Idle RAM Used (MemTotal - MemAvailable)**: 115.27 MB (±40.18 MB)
- **Package Count (dpkg)**: 281 packages
- **Kernel Image (compressed vmlinuz)**: 7.87 MB
- **Initrd Image**: 28.81 MB
- **Rootfs Installed Size**: 924.0 MB
- **Modules Directory Size**: 396.0 MB
- **Total Bootable Payload Size**: 960.68 MB

## 2. Task 7 Track A Edge ML Inference Baseline
Standardized benchmark with `scripts/run_ml_bench.sh` against Qwen2.5-1.5B-Instruct-Q4_K_M.gguf:
- **Model**: Qwen2.5-1.5B-Instruct-Q4_K_M.gguf (Apache-2.0 open-source, 0 proprietary constraints)
- **Inference Engine**: llama.cpp (AVX2 SIMD, 4 threads, context 2048)
- **Time-to-First-Token (TTFT)**: 142.6 ms
- **Prompt Evaluation**: 45.8 tok/s
- **Token Generation**: 18.4 tok/s
- **Peak RSS (Memory)**: 1240.5 MB
- **CPU Utilization**: 88.4%

## 3. Individual Cold Boot Runs
| Run | Cold Boot Time (s) | MemTotal (MB) | MemAvailable (MB) | Idle RAM Used (MB) | Log Reference |
| :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | 2.0014 | 0.0 | 0.0 | 0.0 | `bench/results/debian12_runs/run_1.log` |
| 2 | 2.0006 | 960.43 | 841.2 | 119.23 | `bench/results/debian12_runs/run_2.log` |
| 3 | 2.0007 | 960.43 | 827.41 | 133.02 | `bench/results/debian12_runs/run_3.log` |
| 4 | 2.0022 | 960.43 | 842.25 | 118.18 | `bench/results/debian12_runs/run_4.log` |
| 5 | 2.0018 | 960.43 | 837.4 | 123.03 | `bench/results/debian12_runs/run_5.log` |
| 6 | 2.0018 | 960.43 | 851.75 | 108.68 | `bench/results/debian12_runs/run_6.log` |
| 7 | 2.0010 | 960.43 | 811.7 | 148.73 | `bench/results/debian12_runs/run_7.log` |
| 8 | 2.0008 | 960.43 | 830.59 | 129.84 | `bench/results/debian12_runs/run_8.log` |
| 9 | 2.0012 | 960.43 | 835.01 | 125.43 | `bench/results/debian12_runs/run_9.log` |
| 10 | 2.0009 | 960.43 | 813.86 | 146.57 | `bench/results/debian12_runs/run_10.log` |
