"""Lightweight quality test of the whole assistant on `eval/questions.jsonl`.

For each question we run the full pipeline (`answer_question`) and check, without any
LLM judge:
- retrieval: is a relevant passage among the passages given to the LLM?
- correctness: for answerable questions, does the answer contain every expected key fact
  (`must_include`, each term may list alternatives separated by "|")?
- citations: what share of the cited passages come from the expected source?
- abstention: unanswerable questions must be abstained on; answerable ones must not.
"""

from __future__ import annotations

import json
import statistics
import time
from datetime import datetime
from pathlib import Path

from aerodoc.answer import Answer, answer_question
from aerodoc.pipeline_config import PipelineConfig
from aerodoc.search import Hit

QUESTIONS = Path("eval/questions.jsonl")
RESULTS_DIR = Path("eval/results")


def is_relevant(hit: Hit, source: dict) -> bool:
    if "ad_number" in source:
        return hit.ad_number == source["ad_number"]
    if "pages" in source:
        return hit.doc_type == "handbook" and hit.page_label in source["pages"]
    return False


def contains_facts(answer: str, must_include: list[str]) -> tuple[bool, list[str]]:
    """All key facts present? Returns (ok, missing terms)."""
    text = answer.lower()
    missing = [
        term
        for term in must_include
        if not any(alt.strip().lower() in text for alt in term.split("|"))
    ]
    return not missing, missing


def score_one(item: dict, ans: Answer) -> dict:
    answerable = item["type"] != "unanswerable"
    source = item.get("source", {})
    row = {
        "id": item["id"],
        "type": item["type"],
        "question": item["question"],
        "answer": ans.text,
        "abstained": ans.abstained,
        "model": ans.model,
        "latency_s": round(sum(ans.timings_ms.values()) / 1000, 2),
        "tokens": ans.prompt_tokens + ans.completion_tokens,
        "cited": [hit.citation for _, hit in ans.citations],
    }
    if answerable:
        ok, missing = contains_facts(ans.text, item["must_include"])
        relevant_cited = [is_relevant(hit, source) for _, hit in ans.citations]
        row |= {
            "retrieved": any(is_relevant(h, source) for h in ans.passages),
            "correct": (not ans.abstained) and ok,
            "missing_facts": missing,
            "citation_precision": (
                sum(relevant_cited) / len(relevant_cited) if relevant_cited else None
            ),
            "false_abstention": ans.abstained,
        }
    else:
        row["correct_abstention"] = ans.abstained
    return row


def summarize(rows: list[dict]) -> dict:
    answerable = [r for r in rows if r["type"] != "unanswerable"]
    unanswerable = [r for r in rows if r["type"] == "unanswerable"]
    precisions = [
        r["citation_precision"] for r in answerable if r["citation_precision"] is not None
    ]
    summary = {
        "questions": len(rows),
        "retrieval_hit@5": sum(r["retrieved"] for r in answerable) / len(answerable),
        "answer_correct": sum(r["correct"] for r in answerable) / len(answerable),
        "citation_precision": statistics.mean(precisions) if precisions else 0.0,
        "false_abstention": sum(r["false_abstention"] for r in answerable) / len(answerable),
        "correct_abstention": (
            sum(r["correct_abstention"] for r in unanswerable) / len(unanswerable)
            if unanswerable
            else 0.0
        ),
        "median_latency_s": statistics.median(r["latency_s"] for r in rows),
        "max_latency_s": max(r["latency_s"] for r in rows),
        "mean_tokens": statistics.mean(r["tokens"] for r in rows),
    }
    by_type = {}
    for r in answerable:
        by_type.setdefault(r["type"], []).append(r["correct"])
    summary["answer_correct_by_type"] = {k: sum(v) / len(v) for k, v in by_type.items()}
    return summary


def run_eval(conn, cfg: PipelineConfig, config_name: str, pause_s: float = 1.0) -> dict:
    items = [json.loads(line) for line in QUESTIONS.read_text().splitlines() if line.strip()]
    answer_question(conn, "warm-up: landing gear inspection", cfg)  # load models first
    rows = []
    for item in items:
        rows.append(score_one(item, answer_question(conn, item["question"], cfg)))
        print(f"  {item['id']} done")
        time.sleep(pause_s)  # stay under the free-tier rate limit
    result = {
        "date": datetime.now().isoformat(timespec="seconds"),
        "config": config_name,
        "config_values": cfg.model_dump(),
        "summary": summarize(rows),
        "rows": rows,
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"{datetime.now():%Y-%m-%d_%H%M}_{Path(config_name).stem}.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    result["path"] = str(out)
    return result
