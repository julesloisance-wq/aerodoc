"""Retrieval-augmented answer: retrieve passages, ask the LLM to answer only from them."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field

import psycopg

from aerodoc.llm import Completion, chat
from aerodoc.pipeline_config import PipelineConfig
from aerodoc.search import Hit, retrieve

ABSTAIN_MARKER = "NOT_IN_DOCUMENTS"

SYSTEM_PROMPT = f"""You are AeroDoc, an assistant for aircraft maintenance documentation \
(FAA airworthiness directives and the FAA Aviation Maintenance Technician Handbook).

Rules:
1. Answer ONLY with information stated in the numbered passages provided. Never use \
outside knowledge, even if you think you know the answer.
2. After every sentence that states a fact, cite the passage(s) it comes from with \
their numbers in square brackets, e.g. [1] or [2][4].
3. If the passages do not contain the information needed to answer, reply with \
"{ABSTAIN_MARKER}" on the first line, then one short sentence saying what is missing. \
Do not guess. If they answer only part of the question, answer that part with citations \
and state clearly which part is not covered.
4. When a directive only refers to another document (for example an EASA AD) for the \
detailed actions, say so: the detailed actions are then not in the passages.
5. Be concise and precise: quote identifiers (AD numbers, aircraft models, part numbers, \
compliance times) exactly as written.
6. Answer in the language of the question."""


@dataclass
class Answer:
    question: str
    text: str
    abstained: bool
    passages: list[Hit]
    cited: list[int]  # passage numbers (1-based) cited in the answer
    model: str = ""
    timings_ms: dict[str, float] = field(default_factory=dict)
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def citations(self) -> list[tuple[int, Hit]]:
        return [(n, self.passages[n - 1]) for n in self.cited if 0 < n <= len(self.passages)]


def format_passages(hits: list[Hit]) -> str:
    return "\n\n".join(f"[{i}] Source: {hit.citation}\n{hit.text}" for i, hit in enumerate(hits, 1))


def build_messages(question: str, hits: list[Hit]) -> list[dict]:
    user = f"Passages:\n\n{format_passages(hits)}\n\nQuestion: {question}"
    return [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}]


def parse_citations(text: str) -> list[int]:
    """Passage numbers cited as [n], in order of first appearance."""
    return list(dict.fromkeys(int(n) for n in re.findall(r"\[(\d+)\]", text)))


FRENCH_HINTS = set(
    """le la les des du une un est sont quel quels quelle quelles comment pourquoi quoi
    qui que pour par sur avec dans avion avions concernés consigne faut doit""".split()
)


def looks_french(text: str) -> bool:
    """Cheap language check: at least two common French words."""
    words = re.findall(r"[a-zàâçéèêëîïôûùüÿœ']+", text.lower().replace("'", " "))
    return sum(word in FRENCH_HINTS for word in words) >= 2


def english_search_query(question: str, cfg: PipelineConfig) -> str:
    """The documents, embedding model and reranker are English-only: translate French
    questions for retrieval (the answer is still written in the question's language)."""
    if not looks_french(question):
        return question
    completion = chat(
        [
            {
                "role": "system",
                "content": "Translate the user's aircraft maintenance question into English. "
                "Keep identifiers (AD numbers, aircraft models, part numbers) unchanged. "
                "Output only the translation.",
            },
            {"role": "user", "content": question},
        ],
        cfg.llm,
    )
    return completion.text.strip() or question


def answer_question(conn: psycopg.Connection, question: str, cfg: PipelineConfig) -> Answer:
    t = time.perf_counter()
    search_query = english_search_query(question, cfg)
    translate_ms = (time.perf_counter() - t) * 1000 if search_query != question else 0.0
    retrieval = retrieve(conn, search_query, cfg)
    completion: Completion = chat(build_messages(question, retrieval.hits), cfg.llm)

    text = completion.text
    abstained = text.startswith(ABSTAIN_MARKER)
    if abstained:
        text = text.removeprefix(ABSTAIN_MARKER).strip() or "The documents do not say."
    timings = dict(retrieval.timings_ms)
    if translate_ms:
        timings["translate"] = translate_ms
    timings["llm"] = completion.latency_ms
    return Answer(
        question=question,
        text=text,
        abstained=abstained,
        passages=retrieval.hits,
        cited=[] if abstained else parse_citations(text),
        model=completion.model,
        timings_ms=timings,
        prompt_tokens=completion.prompt_tokens,
        completion_tokens=completion.completion_tokens,
    )


def render_answer(ans: Answer) -> str:
    """Plain-text rendering for the command line."""
    lines = [ans.text, ""]
    if ans.abstained:
        lines.insert(0, "I don't know based on the available documents.")
    elif ans.citations:
        lines.append("Sources:")
        for n, hit in ans.citations:
            lines.append(f"  [{n}] {hit.citation}\n      {hit.source_url}")
    total = sum(ans.timings_ms.values()) / 1000
    lines.append(
        f"\n({ans.model}, {total:.1f} s, {ans.prompt_tokens}+{ans.completion_tokens} tokens)"
    )
    return "\n".join(lines)
