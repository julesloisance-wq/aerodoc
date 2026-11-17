"""Retrieve the chunks most relevant to a question.

Three retrievers, combined as configured in `configs/*.yaml`:
- dense: cosine similarity between embeddings (good at meaning, weak on exact identifiers);
- bm25: keyword ranking (exact terms such as "2026-18-03" or "A321-271NX");
- hybrid: both rankings merged with Reciprocal Rank Fusion (RRF);
then an optional cross-encoder *reranker* re-reads the best candidates and reorders them.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np
import psycopg

from aerodoc.embeddings import embed_query
from aerodoc.pipeline_config import PipelineConfig


@dataclass
class Hit:
    chunk_id: int
    document_id: str
    title: str
    doc_type: str
    ad_number: str | None
    source_url: str
    header: str
    text: str
    page: int | None
    page_label: str | None
    section: str | None
    score: float = 0.0
    ranks: dict[str, int] = field(default_factory=dict)  # rank in each retriever (1-based)

    @property
    def citation(self) -> str:
        """Human-readable reference, e.g. 'AD 2026-18-03, (c) Applicability, FR page 56578'."""
        if self.doc_type == "directive":
            name = f"AD {self.ad_number}" if self.ad_number else self.document_id
            page = f"FR page {self.page}" if self.page else None
        else:
            name = self.document_id
            page = f"page {self.page_label}" if self.page_label else None
        return ", ".join(p for p in (name, self.section, page) if p)


SELECT_HITS = """
    SELECT c.id, c.document_id, d.title, d.doc_type, d.ad_number, d.source_url,
           c.header, c.text, c.page, c.page_label, c.section
    FROM chunks c JOIN documents d ON d.id = c.document_id
    WHERE c.id = ANY(%s)
"""

# --------------------------------------------------------------------------- keyword search
STOPWORDS = set(
    """a an and are as at be by can do does for from has have how if in is it its of on or
    should that the their this to was what when where which who why will with you your""".split()
)
TOKEN = re.compile(r"[a-z0-9]+(?:[-./][a-z0-9]+)*")


def tokenize(text: str) -> list[str]:
    """Lowercase word tokens; compound identifiers are kept whole *and* split.

    "AD 2026-18-03 on A321-271NX" -> ad, 2026-18-03, 2026, 18, 03, a321-271nx, a321, 271nx
    so that both the exact identifier and its parts can match.
    """
    tokens = []
    for match in TOKEN.finditer(text.lower()):
        token = match.group()
        if token in STOPWORDS:
            continue
        tokens.append(token)
        if any(sep in token for sep in "-./"):
            tokens.extend(part for part in re.split(r"[-./]", token) if part)
    return tokens


class KeywordIndex:
    """In-memory BM25 over all chunks (header + text). Built in ~1 s for ~5,000 chunks."""

    def __init__(self, chunk_ids: list[int], texts: list[str]):
        import bm25s

        self.chunk_ids = np.array(chunk_ids)
        self.bm25 = bm25s.BM25()  # default parameters k1=1.5, b=0.75
        self.bm25.index([tokenize(t) for t in texts], show_progress=False)

    def search(self, query: str, n: int) -> list[tuple[int, float]]:
        scores = self.bm25.get_scores(tokenize(query))
        top = np.argsort(-scores)[:n]
        return [(int(self.chunk_ids[i]), float(scores[i])) for i in top if scores[i] > 0]


_KEYWORD_CACHE: dict[int, KeywordIndex] = {}


def keyword_index(conn: psycopg.Connection) -> KeywordIndex:
    """Build the BM25 index once per process; the chunk count is the cache key, so a
    re-index (different number of chunks) triggers a rebuild."""
    n = conn.execute("SELECT count(*) FROM chunks").fetchone()[0]
    if n not in _KEYWORD_CACHE:
        rows = conn.execute("SELECT id, header || ' ' || text FROM chunks ORDER BY id").fetchall()
        _KEYWORD_CACHE.clear()
        _KEYWORD_CACHE[n] = KeywordIndex([r[0] for r in rows], [r[1] for r in rows])
    return _KEYWORD_CACHE[n]


# --------------------------------------------------------------------------- fusion & rerank
def rrf(rankings: dict[str, list[int]], k: int = 60) -> list[tuple[int, float]]:
    """Reciprocal Rank Fusion: score(chunk) = sum over rankings of 1 / (k + rank).

    Uses ranks only, not raw scores, so a cosine similarity (0..1) and a BM25 score (0..30)
    can be combined without calibration. k=60 is the value from the original paper.
    """
    scores: dict[int, float] = {}
    for ranking in rankings.values():
        for rank, chunk_id in enumerate(ranking, 1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda item: -item[1])


@lru_cache(maxsize=2)
def _cross_encoder(name: str):
    from sentence_transformers import CrossEncoder

    return CrossEncoder(name, device="cpu", max_length=512)


def rerank(query: str, hits: list[Hit], model: str) -> list[Hit]:
    """Score each (question, passage) pair jointly and sort by that score."""
    if not hits:
        return hits
    scores = _cross_encoder(model).predict(
        [(query, f"{h.header}\n{h.text}") for h in hits], batch_size=16
    )
    for hit, score in zip(hits, scores, strict=True):
        hit.score = float(score)
    return sorted(hits, key=lambda h: -h.score)


AD_NUMBER = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")


def mentioned_ads(conn: psycopg.Connection, query: str) -> list[str]:
    """AD numbers written in the question that exist in the corpus."""
    numbers = AD_NUMBER.findall(query)
    if not numbers:
        return []
    rows = conn.execute(
        "SELECT ad_number FROM documents WHERE ad_number = ANY(%s)", (numbers,)
    ).fetchall()
    return [r[0] for r in rows]


# --------------------------------------------------------------------------- retrieval
def _dense_ids(conn, query: str, cfg: PipelineConfig, n: int) -> list[tuple[int, float]]:
    vector = embed_query(query, cfg.embedding)
    return conn.execute(
        "SELECT id, 1 - (embedding <=> %(v)s) FROM chunks ORDER BY embedding <=> %(v)s LIMIT %(n)s",
        {"v": vector, "n": n},
    ).fetchall()


def _load_hits(conn, scored: list[tuple[int, float]]) -> list[Hit]:
    rows = {r[0]: r for r in conn.execute(SELECT_HITS, ([cid for cid, _ in scored],))}
    return [Hit(*rows[cid], score=score) for cid, score in scored if cid in rows]


@dataclass
class Retrieval:
    hits: list[Hit]
    timings_ms: dict[str, float]


def retrieve(
    conn: psycopg.Connection, query: str, cfg: PipelineConfig, k: int | None = None
) -> Retrieval:
    """Return the top-k chunks for `query` according to `cfg.retrieval`."""
    rc = cfg.retrieval
    k = k or rc.top_k
    timings: dict[str, float] = {}
    rankings: dict[str, list[tuple[int, float]]] = {}

    if rc.mode in ("dense", "hybrid"):
        t = time.perf_counter()
        rankings["dense"] = _dense_ids(conn, query, cfg, rc.candidates)
        timings["dense"] = (time.perf_counter() - t) * 1000
    if rc.mode in ("bm25", "hybrid"):
        t = time.perf_counter()
        rankings["bm25"] = keyword_index(conn).search(query, rc.candidates)
        timings["bm25"] = (time.perf_counter() - t) * 1000

    ids = {name: [cid for cid, _ in r] for name, r in rankings.items()}
    if rc.mode != "hybrid":
        fused = rankings[rc.mode]
    else:
        fused = rrf(ids, rc.rrf_k)

    pool = rc.rerank_top_n if rc.rerank else k
    candidates = fused[:pool]
    # Metadata match: chunks of a directive named in the question always reach the reranker.
    named = mentioned_ads(conn, query) if rc.ad_number_slots else []
    if named:
        in_pool = {cid for cid, _ in candidates}
        rows = conn.execute(
            "SELECT c.id FROM chunks c JOIN documents d ON d.id = c.document_id "
            "WHERE d.ad_number = ANY(%s) ORDER BY c.id",
            (named,),
        ).fetchall()
        candidates += [(r[0], 0.0) for r in rows if r[0] not in in_pool]
    hits = _load_hits(conn, candidates)
    for hit in hits:
        for name, ranking in rankings.items():
            ids = [cid for cid, _ in ranking]
            if hit.chunk_id in ids:
                hit.ranks[name] = ids.index(hit.chunk_id) + 1

    if rc.rerank:
        t = time.perf_counter()
        hits = rerank(query, hits, rc.reranker_model)
        timings["rerank"] = (time.perf_counter() - t) * 1000
    if named:
        # Reserve slots for the named directive(s), fill the rest with the best other chunks.
        own = [h for h in hits if h.ad_number in named][: rc.ad_number_slots]
        others = [h for h in hits if h not in own][: k - len(own)]
        hits = sorted(own + others, key=lambda h: -h.score)
    return Retrieval(hits[:k], timings)


def dense_search(
    conn: psycopg.Connection, query: str, cfg: PipelineConfig, k: int | None = None
) -> list[Hit]:
    """Dense-only search, kept for the explorer page and comparisons."""
    return _load_hits(conn, _dense_ids(conn, query, cfg, k or cfg.retrieval.top_k))
