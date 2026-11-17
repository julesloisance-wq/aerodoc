"""Static HTML snapshot of the index, to look at the data without a database client."""

from __future__ import annotations

import html
from pathlib import Path

import psycopg

from aerodoc.pipeline_config import PipelineConfig
from aerodoc.search import retrieve

STYLE = """
:root { --bg:#fff; --fg:#1d1d1f; --muted:#6e6e73; --card:#f5f5f7; --accent:#0b63ce;
        --border:#d2d2d7; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#141416; --fg:#f2f2f2; --muted:#a1a1a6; --card:#1f1f23; --accent:#5aa2ff;
          --border:#3a3a3f; } }
body { background:var(--bg); color:var(--fg); font:15px/1.5 system-ui, sans-serif;
       max-width: 960px; margin: 0 auto; padding: 24px 16px; }
h1 { font-size: 26px; } h2 { margin-top: 40px; border-bottom: 1px solid var(--border); }
table { border-collapse: collapse; width: 100%; font-size: 14px; }
td, th { border-bottom: 1px solid var(--border); padding: 6px 8px; text-align: left;
         vertical-align: top; }
.card { background: var(--card); border-radius: 10px; padding: 12px 14px; margin: 10px 0; }
.meta { color: var(--muted); font-size: 13px; }
.score { color: var(--accent); font-weight: 600; }
details summary { cursor: pointer; }
.scroll { overflow-x: auto; }
"""


def _e(value) -> str:
    return html.escape("" if value is None else str(value))


def build_explorer(
    conn: psycopg.Connection, cfg: PipelineConfig, questions: list[str], sample_doc: str
) -> str:
    stats = conn.execute(
        """SELECT d.doc_type, count(DISTINCT d.id), count(c.id),
                  round(avg(array_length(regexp_split_to_array(c.text, '\\s+'), 1)))
           FROM documents d LEFT JOIN chunks c ON c.document_id = d.id
           GROUP BY d.doc_type ORDER BY d.doc_type"""
    ).fetchall()
    families = conn.execute(
        """SELECT f, count(*) FROM documents, unnest(families) f GROUP BY f ORDER BY f"""
    ).fetchall()
    docs = conn.execute(
        """SELECT d.id, d.ad_number, d.publication_date, d.families, d.title,
                  d.source_url, count(c.id)
           FROM documents d LEFT JOIN chunks c ON c.document_id = d.id
           GROUP BY d.id ORDER BY d.publication_date DESC NULLS LAST LIMIT 30"""
    ).fetchall()
    sample = conn.execute(
        """SELECT chunk_index, page, section, header, text FROM chunks
           WHERE document_id = %s ORDER BY chunk_index""",
        (sample_doc,),
    ).fetchall()

    out = [
        f"<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
        f"<meta name='viewport' content='width=device-width, initial-scale=1'>"
        f"<title>AeroDoc Explorer</title><style>{STYLE}</style></head><body>"
    ]
    out.append(
        "<h1>AeroDoc Explorer</h1><p class='meta'>Snapshot of the PostgreSQL index. "
        f"Embedding model: {_e(cfg.embedding.model)}, chunks of "
        f"~{cfg.chunking.max_words} words with {cfg.chunking.overlap_words} words "
        "of overlap.</p>"
    )

    out.append(
        "<h2>1. Corpus</h2><div class='scroll'><table><tr><th>Type</th>"
        "<th>Documents</th><th>Chunks</th><th>Avg words / chunk</th></tr>"
    )
    out += [
        f"<tr><td>{_e(t)}</td><td>{n}</td><td>{c}</td><td>{w}</td></tr>" for t, n, c, w in stats
    ]
    out.append(
        "</table></div><p>Directives per aircraft family: "
        + ", ".join(f"<b>{_e(f)}</b> {n}" for f, n in families)
        + "</p>"
    )

    out.append(
        "<h2>2. Most recent directives (table <code>documents</code>)</h2>"
        "<div class='scroll'><table><tr><th>AD</th><th>Published</th>"
        "<th>Aircraft</th><th>Chunks</th></tr>"
    )
    for doc_id, ad, date, fam, _title, url, n in docs:
        out.append(
            f"<tr><td><a href='{_e(url)}'>{_e(ad or doc_id)}</a></td><td>{_e(date)}"
            f"</td><td>{_e(', '.join(fam))}</td><td>{n}</td></tr>"
        )
    out.append("</table></div>")

    out.append(
        f"<h2>3. One directive cut into chunks ({_e(sample_doc)})</h2>"
        "<p class='meta'>The header (grey) is embedded together with the text, so "
        "every chunk knows which AD, aircraft and section it belongs to.</p>"
    )
    for idx, page, section, header, text in sample:
        out.append(
            f"<details class='card'><summary><b>Chunk {idx}</b> · page {_e(page)} · "
            f"{_e(section)}</summary><p class='meta'>{_e(header)}</p>"
            f"<p>{_e(text)}</p></details>"
        )

    out.append("<h2>4. Retrieval (hybrid + reranker): top 5 chunks per question</h2>")
    for question in questions:
        out.append(f"<h3>“{_e(question)}”</h3>")
        for rank, hit in enumerate(retrieve(conn, question, cfg, 5).hits, 1):
            found_by = ", ".join(f"{name} #{r}" for name, r in hit.ranks.items())
            out.append(
                f"<div class='card'><span class='score'>#{rank} · score "
                f"{hit.score:.3f}</span> <span class='meta'>{_e(hit.citation)} · "
                f"found by {_e(found_by)}</span>"
                f"<p>{_e(hit.text[:450])}…</p></div>"
            )
    out.append("</body></html>")
    return "\n".join(out)


def write_explorer(conn, cfg, questions, sample_doc, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_explorer(conn, cfg, questions, sample_doc), encoding="utf-8")
    return path
