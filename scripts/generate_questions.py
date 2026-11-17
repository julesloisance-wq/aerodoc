"""Generate realistic evaluation questions from randomly sampled passages (seeded).

The LLM writes, for each passage, a paraphrased question, a reference answer and 1-3 key
facts copied from the passage. Automatic filters then drop unusable items:
- every key fact must appear in the passage (no invented facts);
- no key fact may appear in the question (no giveaways).
Output: eval/questions/generated.jsonl. A human reviews a random sample afterwards.
"""

from __future__ import annotations

import json
import random
import re
import time
from pathlib import Path

from aerodoc import db
from aerodoc.llm import chat
from aerodoc.pipeline_config import load_config

SEED = 42
N_DIRECTIVE, N_HANDBOOK = 50, 25
OUT = Path("eval/questions/generated.jsonl")

# Documents and pages already used in other question sets, examples or the retrieval probe.
USED_ADS = {
    "2026-18-03",
    "2025-07-05",
    "2023-17-01",
    "2025-13-12",
    "2024-14-10",
    "2023-22-09",
    "2026-15-13",
    "2023-20-12",
    "2025-24-51",
    "2024-08-02",
    "2023-12-11",
    "2022-27-01",
    "2022-08-05",
    "2025-17-17",
    "2024-08-08",
    "2024-20-01",
    "2025-18-03",
    "2025-20-12",
    "2025-25-12",
    "2026-13-05",
    "2026-14-11",
    "2025-04-04",
    "2024-02-51",
    "2025-20-19",
}
USED_PAGES = {
    "1-5",
    "1-7",
    "1-8",
    "1-14",
    "6-12",
    "7-8",
    "7-27",
    "12-74",
    "14-10",
    "5-7",
    "5-8",
    "5-24",
    "5-25",
    "5-2",
    "5-3",
    "5-46",
    "5-47",
}
AD_SECTIONS = r"Summary|Background|\(c\) Applicability|\(e\) Unsafe|\(e\) Reason|\(g\)|Costs"

SYSTEM = """You write evaluation questions for a question-answering system over FAA \
aircraft maintenance documents. Return only a JSON object with keys: \
"usable" (boolean), "question", "answer", "key_facts" (list of strings)."""

STYLES = {
    "ad_number": "Mention the AD number in the question (e.g. 'What does AD 2024-11-01 ...').",
    "ad_topic": "Do NOT mention the AD number. Mention the aircraft model and enough details "
    "of the issue for the question to point to this directive only.",
    "handbook": "Ask a general aircraft maintenance knowledge question. Do not mention a "
    "handbook, chapter, page or 'the passage'.",
}

INSTRUCTIONS = """Passage (source: {header}):
\"\"\"{text}\"\"\"

Write ONE question that this passage alone answers precisely (one fact or a short list).
Style: {style}
Rules:
- Phrase it the way an aircraft maintenance technician would ask it. Paraphrase: do not \
copy any sequence of 4 or more words from the passage, except identifiers (AD numbers, \
model names, part numbers).
- "answer": a one-sentence reference answer.
- "key_facts": 1 to 3 short strings (1 to 4 words each) copied EXACTLY from the passage, \
that any correct answer must contain. You may give alternatives separated by "|" \
(other wording or number format). Never use a fact that already appears in the question.
- Set "usable": false if the passage is boilerplate, a figure label list, a table without \
context, or has no clear fact to ask about."""


def sample_passages(conn, rng: random.Random) -> list[tuple[str, tuple]]:
    ads = conn.execute(
        """SELECT c.id, c.header, c.text, d.ad_number, c.page_label FROM chunks c
           JOIN documents d ON d.id = c.document_id
           WHERE d.doc_type = 'directive' AND d.ad_number IS NOT NULL
             AND c.section ~ %s AND length(c.text) > 600 ORDER BY c.id""",
        (AD_SECTIONS,),
    ).fetchall()
    ads = [r for r in ads if r[3] not in USED_ADS]
    hb = conn.execute(
        """SELECT c.id, c.header, c.text, NULL, c.page_label FROM chunks c
           WHERE c.document_id = 'FAA-H-8083-30B' AND length(c.text) > 1000
             AND c.page_label ~ '^[0-9]+-[0-9]+$' ORDER BY c.id"""
    ).fetchall()
    hb = [r for r in hb if r[4] not in USED_PAGES]
    # One passage per directive at most, for variety.
    rng.shuffle(ads)
    seen, picked_ads = set(), []
    for row in ads:
        if row[3] not in seen:
            seen.add(row[3])
            picked_ads.append(row)
    picked = [
        (rng.choice(["ad_number", "ad_topic", "ad_topic"]), r) for r in picked_ads[:N_DIRECTIVE]
    ]
    picked += [("handbook", r) for r in rng.sample(hb, N_HANDBOOK)]
    return picked


def parse_json(text: str) -> dict | None:
    match = re.search(r"\{.*\}", text, flags=re.S)
    try:
        return json.loads(match.group()) if match else None
    except json.JSONDecodeError:
        return None


def valid(item: dict, passage: str) -> str | None:
    """Return the reason for rejection, or None if the item is usable."""
    if not item or not item.get("usable"):
        return "not usable"
    facts = item.get("key_facts") or []
    if not item.get("question") or not facts or len(facts) > 3:
        return "missing fields"
    low_passage, low_question = passage.lower(), item["question"].lower()
    for fact in facts:
        alternatives = [a.strip().lower() for a in fact.split("|") if a.strip()]
        if not any(a in low_passage for a in alternatives):
            return f"fact not in passage: {fact}"
        if any(a in low_question for a in alternatives):
            return f"fact given away in question: {fact}"
    return None


def main() -> None:
    cfg = load_config()
    rng = random.Random(SEED)
    out, rejected = [], {}
    with db.connect() as conn:
        picked = sample_passages(conn, rng)
    for i, (style, (chunk_id, header, text, ad_number, page_label)) in enumerate(picked, 1):
        prompt = INSTRUCTIONS.format(header=header, text=text, style=STYLES[style])
        try:
            completion = chat(
                [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
                cfg.llm,
            )
        except RuntimeError as exc:
            rejected[f"chunk {chunk_id}"] = str(exc)
            continue
        item = parse_json(completion.text)
        reason = valid(item, text)
        if reason:
            rejected[f"chunk {chunk_id}"] = reason
        else:
            source = {"ad_number": ad_number} if ad_number else {"pages": [page_label]}
            out.append(
                {
                    "id": f"g{len(out) + 1:02d}",
                    "type": style,
                    "question": item["question"].strip(),
                    "expected_answer": item.get("answer", "").strip(),
                    "must_include": item["key_facts"],
                    "source": source,
                    "from_chunk": chunk_id,
                }
            )
        print(f"{i}/{len(picked)} {'rejected: ' + reason if reason else 'ok'}")
        time.sleep(1)
    OUT.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in out) + "\n")
    print(f"\n{len(out)} questions kept, {len(rejected)} rejected -> {OUT}")


if __name__ == "__main__":
    main()
