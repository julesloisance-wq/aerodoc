"""Regenerate docs/EXEMPLES.md: real answers from the current pipeline."""

from datetime import date
from pathlib import Path

from aerodoc import db
from aerodoc.answer import answer_question
from aerodoc.pipeline_config import load_config

QUESTIONS = [
    (
        "Directive by number",
        "Which airplanes are affected by AD 2026-18-03 and what is the unsafe condition?",
    ),
    ("Handbook", "How should a portable fire extinguisher be inspected?"),
    (
        "Directive by topic",
        "What problem was found on the ATR 72 nose landing gear drag brace panels, "
        "and which part numbers are affected?",
    ),
    (
        "Partly outside the corpus",
        "What are the detailed inspection steps required by EASA AD 2026-0142?",
    ),
    ("Outside the corpus", "What is the maximum takeoff weight of the Airbus A350-1000?"),
    ("Question in French", "Quels avions sont concernés par l'AD 2026-18-03 ?"),
]

cfg = load_config()
out = [
    "# Examples",
    "",
    f"Real outputs of `aerodoc ask` generated on {date.today()} with `configs/default.yaml` "
    "(regenerate with `uv run python scripts/make_examples.py`).",
    "",
]
with db.connect() as conn:
    for i, (kind, question) in enumerate(QUESTIONS, 1):
        ans = answer_question(conn, question, cfg)
        out += [f"## {i}. {kind}", "", f"**Question:** {question}", ""]
        if ans.abstained:
            out += [
                "**Answer (abstained):** I don't know based on the available documents. "
                + ans.text,
                "",
            ]
        else:
            out += ["**Answer:**", "", ans.text, ""]
        out += [
            "**Sources cited:**" if ans.citations else "**Passages retrieved (none cited):**",
            "",
        ]
        listed = ans.citations or list(enumerate(ans.passages, 1))
        out += [f"- [{n}] [{hit.citation}]({hit.source_url})" for n, hit in listed]
        total = sum(ans.timings_ms.values()) / 1000
        out += [
            "",
            f"_Model {ans.model}, {total:.1f} s, "
            f"{ans.prompt_tokens} + {ans.completion_tokens} tokens._",
            "",
        ]
        print(f"{i}. done ({'abstained' if ans.abstained else 'answered'}, {ans.model})")
Path("docs/EXEMPLES.md").write_text("\n".join(out), encoding="utf-8")
