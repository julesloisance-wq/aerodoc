# Experiments

Results that change the system's behaviour are recorded here: date, configuration, metrics, conclusion.

## 2026-11-17 — Embedding model speed (step 3)

Configuration: 128 chunks of 300 words from directives, CPU (4 cores), batch size 32.

| Model | Dimension | Throughput |
|---|---|---|
| BAAI/bge-small-en-v1.5 | 384 | 9.6 chunks/s |
| BAAI/bge-base-en-v1.5 | 768 | 2.7 chunks/s |

Conclusion: bge-small chosen (full index of 5,295 chunks built in 407 s). Quality is to be
recovered by hybrid search and reranking (step 4).

## 2026-11-17 — Dense-only retrieval, qualitative check (configs/default.yaml)

- "landing gear inspection": top 4 from handbook chapter 10 (Inspection), relevant.
- "How do you inspect a fire extinguisher?": exact section "Inspection of Fire Extinguishers"
  (page 1-7) ranked #2.
- "AD 2026-18-03": the right directive only ranked #3 (0.744), behind AD 2026-09-03 (0.751)
  and AD 2025-23-04 (0.745). Dense retrieval does not match identifiers exactly, which
  motivates keyword (hybrid) search.
