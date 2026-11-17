"""Quick retrieval comparison on `eval/retrieval_probe.jsonl` (16 queries, known answers).

A query counts as found at rank r if the r-th chunk belongs to the expected directive
(or, for handbook questions, to one of the expected handbook pages).
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

from aerodoc.pipeline_config import PipelineConfig
from aerodoc.search import Hit, retrieve

PROBE = Path("eval/retrieval_probe.jsonl")

VARIANTS: dict[str, dict] = {
    "dense": {"mode": "dense", "rerank": False},
    "bm25": {"mode": "bm25", "rerank": False},
    "hybrid (RRF)": {"mode": "hybrid", "rerank": False},
    "hybrid + MiniLM reranker": {
        "mode": "hybrid",
        "rerank": True,
        "reranker_model": "cross-encoder/ms-marco-MiniLM-L6-v2",
    },
    "hybrid + bge reranker": {
        "mode": "hybrid",
        "rerank": True,
        "reranker_model": "BAAI/bge-reranker-base",
    },
}


def is_relevant(hit: Hit, item: dict) -> bool:
    if "document_id_ad" in item:
        return hit.ad_number == item["document_id_ad"]
    return hit.doc_type == "handbook" and hit.page_label in item["pages"]


def first_relevant_rank(hits: list[Hit], item: dict) -> int | None:
    return next((i for i, h in enumerate(hits, 1) if is_relevant(h, item)), None)


def run_probe(conn, base: PipelineConfig, variants: dict[str, dict] = VARIANTS) -> list[dict]:
    items = [json.loads(line) for line in PROBE.read_text().splitlines() if line.strip()]
    results = []
    for name, overrides in variants.items():
        cfg = base.model_copy(
            update={"retrieval": base.retrieval.model_copy(update=overrides)}, deep=True
        )
        retrieve(conn, items[0]["query"], cfg)  # warm-up: load models, build BM25 index
        ranks, latencies, by_kind = [], [], {}
        for item in items:
            result = retrieve(conn, item["query"], cfg, k=10)
            rank = first_relevant_rank(result.hits, item)
            ranks.append(rank)
            latencies.append(sum(result.timings_ms.values()))
            by_kind.setdefault(item["kind"], []).append(rank is not None and rank <= 5)
        results.append(
            {
                "variant": name,
                "recall@1": sum(r == 1 for r in ranks) / len(ranks),
                "recall@5": sum(r is not None and r <= 5 for r in ranks) / len(ranks),
                "mrr@10": sum(1 / r for r in ranks if r) / len(ranks),
                **{f"recall@5 {k}": sum(v) / len(v) for k, v in by_kind.items()},
                "median latency (ms)": statistics.median(latencies),
                "ranks": ranks,
            }
        )
    return results
