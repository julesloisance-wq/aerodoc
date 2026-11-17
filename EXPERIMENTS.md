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


## 2026-11-17 — Retrieval variants on the probe set (step 4)

Probe: `eval/retrieval_probe.jsonl`, 16 queries with a known relevant document
(4 by AD number, 6 by AD topic, 6 on the handbook). Base config: `configs/default.yaml`
(bge-small embeddings, 30 candidates per retriever, RRF k=60, 20 candidates reranked).
Latency: median per query, models already loaded, CPU (4 cores).

| Variant | Recall@1 | Recall@5 | MRR@10 | Recall@5 (AD number) | Median latency |
|---|---|---|---|---|---|
| dense | 0.75 | 0.81 | 0.78 | 0.25 | 20 ms |
| bm25 | 0.88 | 1.00 | 0.92 | 1.00 | 1 ms |
| hybrid (RRF) | 0.75 | 1.00 | 0.85 | 1.00 | 17 ms |
| hybrid + ms-marco-MiniLM-L6-v2 | 0.88 | 1.00 | 0.94 | 1.00 | 989 ms |
| hybrid + bge-reranker-base | 0.94 | 1.00 | 0.97 | 1.00 | 4,901 ms |

Conclusion: default set to hybrid + MiniLM reranker (most of the gain for ~1 s).
Caveats: 16 queries only (one query = 6 points); queries were written from the passages,
which favours BM25 (lexical overlap).
