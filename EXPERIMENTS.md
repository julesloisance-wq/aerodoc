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


## 2026-11-17 — LLM availability and answer latency (step 5)

Free tier of Google AI Studio, OpenAI-compatible endpoint.
- gemini-2.5-flash: HTTP 404 (not available to new users).
- gemini-3.8-flash: HTTP 503 (overloaded, after ~7 s) or 429 (rate limit) on most calls.
- gemini-3.1-flash-lite: available, 1-5 s per answer.

A first fallback policy (retry the overloaded model with backoff, then fall back) took up to
85 s for one answer. Fail-fast policy (switch model immediately, back off only after a full
round) with flash-lite first: warm end-to-end latency 1.6-5.6 s
(dense ~20 ms, BM25 ~1 ms, rerank 0.7-0.9 s, LLM 0.9-4.8 s).

French questions: without translation, "Quels avions sont concernés par l'AD 2026-18-03 ?"
retrieved no applicability passage and the assistant abstained; with LLM translation of
French queries for retrieval it answers correctly (in French).


## 2026-11-17 — Quality test, 20 questions (step 6)

Question set `eval/questions.jsonl` reviewed and validated by Jules before the run
(16 answerable: 4 AD by number, 4 AD by topic, 3 applicability, 5 handbook; 4 unanswerable).
Config `configs/default.yaml` (hybrid + MiniLM reranker, gemini-3.1-flash-lite).
Raw results: `eval/results/2026-11-17_1722_default.json`.

| Metric | Value |
|---|---|
| Relevant passage among the 5 given to the LLM | 16/16 (100 %) |
| Correct answers (all key facts present, no abstention) | 16/16 (100 %) |
| Citation precision (cited passages from the expected source) | 86 % |
| Correct abstentions (unanswerable questions) | 4/4 (100 %) |
| Wrong abstentions (answerable questions) | 0/16 (0 %) |
| Latency median / max | 5.2 s / 30.4 s |
| Tokens per question (mean) | 1,992 |

Manual check: the answers were read one by one and are consistent with the key-fact check.
All 7 questions with citation precision < 100 % cite passages that are relevant but not the
expected source: neighbouring handbook page (14-11), handbook glossary (G-2, G-6), or another
directive on the same issue (AD 2023-25-15, AD 2024-11-01). Citation precision as measured
here is therefore a lower bound.

Latency: the first questions took 12-30 s because of free-tier rate limiting (model switch and
back-off); median 5.2 s.

Caveats: 20 questions only (one question = 6 points on answerable metrics); key-fact matching is
a coarse proxy for correctness; questions were written from the passages.
