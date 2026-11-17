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

from aerodoc.answer import ABSTAIN_MARKER, Answer, answer_question
from aerodoc.llm import chat
from aerodoc.pipeline_config import PipelineConfig
from aerodoc.search import Hit

QUESTIONS = Path("eval/questions/smoke.jsonl")
RESULTS_DIR = Path("eval/results")


CLOSED_BOOK_PROMPT = f"""You are an assistant for aircraft maintenance (FAA airworthiness \
directives, aircraft maintenance practices). Answer the question from your own knowledge. \
If you do not know the answer or are not sure, reply with "{ABSTAIN_MARKER}" on the first \
line, then one short sentence. Be concise and quote identifiers exactly. Answer in the \
language of the question."""


def closed_book_answer(question: str, cfg: PipelineConfig) -> Answer:
    """Baseline without retrieval: the LLM answers from memory."""
    completion = chat(
        [{"role": "system", "content": CLOSED_BOOK_PROMPT}, {"role": "user", "content": question}],
        cfg.llm,
    )
    text = completion.text
    abstained = text.startswith(ABSTAIN_MARKER)
    return Answer(
        question=question,
        text=text.removeprefix(ABSTAIN_MARKER).strip() if abstained else text,
        abstained=abstained,
        passages=[],
        cited=[],
        model=completion.model,
        timings_ms={"llm": completion.latency_ms},
        prompt_tokens=completion.prompt_tokens,
        completion_tokens=completion.completion_tokens,
    )


def wilson(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95 % Wilson score interval for a proportion (well behaved for small n and 0 %/100 %)."""
    if n == 0:
        return (0.0, 0.0)
    p = successes / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * ((p * (1 - p) / n + z**2 / (4 * n**2)) ** 0.5) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def is_relevant(hit: Hit, source: dict) -> bool:
    if "ad_number" in source:
        return hit.ad_number == source["ad_number"]
    if "ad_numbers" in source:
        return hit.ad_number in source["ad_numbers"]
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
            "retrieved": (
                any(is_relevant(h, source) for h in ans.passages) if ans.passages else None
            ),
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


def _rate(values: list) -> dict | None:
    values = [v for v in values if v is not None]
    if not values:
        return None
    k, n = sum(bool(v) for v in values), len(values)
    low, high = wilson(k, n)
    return {"k": k, "n": n, "rate": k / n, "ci95": [round(low, 3), round(high, 3)]}


def summarize(rows: list[dict]) -> dict:
    answerable = [r for r in rows if r["type"] != "unanswerable"]
    unanswerable = [r for r in rows if r["type"] == "unanswerable"]
    precisions = [
        r["citation_precision"] for r in answerable if r["citation_precision"] is not None
    ]
    summary = {
        "questions": len(rows),
        "retrieval_hit@5": _rate([r["retrieved"] for r in answerable]),
        "answer_correct": _rate([r["correct"] for r in answerable]),
        "false_abstention": _rate([r["false_abstention"] for r in answerable]),
        "correct_abstention": _rate([r["correct_abstention"] for r in unanswerable]),
        # answered an unanswerable question = made something up
        "hallucination_on_unanswerable": _rate([not r["correct_abstention"] for r in unanswerable]),
        "citation_precision": statistics.mean(precisions) if precisions else None,
        "median_latency_s": statistics.median(r["latency_s"] for r in rows),
        "max_latency_s": max(r["latency_s"] for r in rows),
        "mean_tokens": statistics.mean(r["tokens"] for r in rows),
    }
    by_type: dict[str, list] = {}
    for r in answerable:
        by_type.setdefault(r["type"], []).append(r["correct"])
    summary["answer_correct_by_type"] = {k: _rate(v) for k, v in sorted(by_type.items())}
    return summary


def run_eval(
    conn,
    cfg: PipelineConfig,
    config_name: str,
    questions: Path = QUESTIONS,
    system: str = "rag",
    pause_s: float = 1.0,
) -> dict:
    """system: "rag" (the pipeline described by cfg) or "closed_book" (LLM only)."""
    items = [json.loads(line) for line in questions.read_text().splitlines() if line.strip()]
    if system == "rag":
        answer_question(conn, "warm-up: landing gear inspection", cfg)  # load models first

    def answer(question: str) -> Answer:
        if system == "closed_book":
            return closed_book_answer(question, cfg)
        return answer_question(conn, question, cfg)

    rows = []
    for item in items:
        rows.append(score_one(item, answer(item["question"])))
        print(f"  {item['id']} done", flush=True)
        time.sleep(pause_s)  # stay under the free-tier rate limit
    label = f"{questions.stem}_{system}_{Path(config_name).stem}"
    result = {
        "date": datetime.now().isoformat(timespec="seconds"),
        "questions_file": str(questions),
        "system": system,
        "config": config_name,
        "config_values": cfg.model_dump(),
        "summary": summarize(rows),
        "rows": rows,
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"{datetime.now():%Y-%m-%d_%H%M}_{label}.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    result["path"] = str(out)
    return result
