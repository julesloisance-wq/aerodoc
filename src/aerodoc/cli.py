"""Command-line interface: `aerodoc <command>`."""

from pathlib import Path

import typer

from aerodoc import db

app = typer.Typer(help="AeroDoc: cited answers over FAA maintenance documentation.")


@app.command()
def health() -> None:
    """Check that the database is reachable and pgvector is installed."""
    with db.connect() as conn:
        info = db.server_info(conn)
    typer.echo(f"PostgreSQL {info['postgres']} with pgvector {info['pgvector']}: OK")


@app.command()
def data(
    config: Path = typer.Option(Path("configs/corpus.yaml"), help="Corpus definition."),
    data_dir: Path = typer.Option(Path("data"), help="Where to store the corpus."),
) -> None:
    """Download the corpus (FAA directives and handbook) and write the manifest."""
    from aerodoc.corpus import build_corpus

    records = build_corpus(config, data_dir)
    try:
        with db.connect() as conn:
            n = db.upsert_documents(conn, records)
        typer.echo(f"Loaded {n} documents into the database (table `documents`).")
    except Exception as exc:  # the corpus on disk is still valid without the database
        typer.echo(f"Database not reachable, skipped loading ({exc}). Run `make db` first.")


@app.command()
def index(
    config: Path = typer.Option(Path("configs/default.yaml"), help="Pipeline config."),
    data_dir: Path = typer.Option(Path("data"), help="Corpus directory."),
) -> None:
    """Chunk the corpus, embed every chunk and store everything in PostgreSQL."""
    from aerodoc.index import build_index
    from aerodoc.pipeline_config import load_config

    with db.connect() as conn:
        n = build_index(conn, load_config(config), data_dir)
    typer.echo(f"Indexed {n} chunks.")


@app.command()
def search(
    question: str,
    k: int = typer.Option(5, "-k", help="Number of passages to show."),
    config: Path = typer.Option(Path("configs/default.yaml"), help="Pipeline config."),
    full: bool = typer.Option(False, help="Print whole passages."),
) -> None:
    """Show the passages retrieved for a question (no LLM involved)."""
    from aerodoc.pipeline_config import load_config
    from aerodoc.search import retrieve

    with db.connect() as conn:
        result = retrieve(conn, question, load_config(config), k)
    for rank, hit in enumerate(result.hits, 1):
        text = hit.text if full else hit.text[:300] + "..."
        origin = ", ".join(f"{name} #{r}" for name, r in hit.ranks.items()) or "-"
        typer.echo(
            f"\n#{rank}  score {hit.score:.3f}  [{hit.citation}]  (found by: {origin})\n    {text}"
        )
    timings = ", ".join(f"{name} {ms:.0f} ms" for name, ms in result.timings_ms.items())
    typer.echo(f"\nTimings: {timings}")


@app.command()
def probe(
    config: Path = typer.Option(Path("configs/default.yaml"), help="Base pipeline config."),
) -> None:
    """Compare retrieval variants on the 16-query probe set."""
    from aerodoc.pipeline_config import load_config
    from aerodoc.probe import run_probe

    with db.connect() as conn:
        results = run_probe(conn, load_config(config))
    for row in results:
        ranks = row.pop("ranks")
        typer.echo(row["variant"])
        for key, value in row.items():
            if key != "variant":
                typer.echo(f"    {key}: {value:.2f}")
        typer.echo(f"    rank of first relevant chunk: {ranks}")


@app.command()
def explore(
    out: Path = typer.Option(Path("data/explorer.html"), help="Output HTML file."),
    config: Path = typer.Option(Path("configs/default.yaml"), help="Pipeline config."),
) -> None:
    """Write a static HTML page showing the corpus, chunks and example searches."""
    from aerodoc.explorer import write_explorer
    from aerodoc.pipeline_config import load_config

    questions = [
        "landing gear inspection",
        "AD 2026-18-03",
        "How do you inspect a fire extinguisher?",
    ]
    with db.connect() as conn:
        path = write_explorer(conn, load_config(config), questions, "FR-2026-18052", out)
    typer.echo(f"Wrote {path}")


@app.command()
def ask(
    question: str,
    config: Path = typer.Option(Path("configs/default.yaml"), help="Pipeline config."),
    show_passages: bool = typer.Option(False, help="Also print the retrieved passages."),
) -> None:
    """Answer a question from the documents, with citations (or abstain)."""
    from aerodoc.answer import answer_question, render_answer
    from aerodoc.pipeline_config import load_config

    with db.connect() as conn:
        ans = answer_question(conn, question, load_config(config))
    typer.echo(render_answer(ans))
    if show_passages:
        for i, hit in enumerate(ans.passages, 1):
            typer.echo(f"\n[{i}] {hit.citation}\n{hit.text}")


@app.command(name="eval")
def evaluate(
    config: Path = typer.Option(Path("configs/default.yaml"), help="Pipeline config."),
    questions: Path = typer.Option(
        Path("eval/questions/dev.jsonl"), help="Question file (dev, test or smoke)."
    ),
    system: str = typer.Option("rag", help="rag, or closed_book (LLM without documents)."),
) -> None:
    """Run the quality test and save the results in eval/results/."""
    from aerodoc.evaluate import run_eval
    from aerodoc.pipeline_config import load_config

    if questions.name == "test.jsonl":
        typer.echo("Running on the TEST set: use it once, for the final measurement only.")
    with db.connect() as conn:
        result = run_eval(conn, load_config(config), str(config), questions, system)
    typer.echo(f"\n{system} on {questions} ({result['summary']['questions']} questions)")
    typer.echo(format_summary(result["summary"]))
    for row in result["rows"]:
        ok = row.get("correct", row.get("correct_abstention"))
        if not ok:
            typer.echo(f"\n  FAILED {row['id']} ({row['type']}): {row['question']}")
            typer.echo(f"    answer: {row['answer'][:300]}")
            if row.get("missing_facts"):
                typer.echo(f"    missing: {row['missing_facts']}")
    typer.echo(f"\nDetails: {result['path']}")


def format_summary(s: dict) -> str:
    def fmt(metric: dict | None) -> str:
        if not metric:
            return "n/a"
        low, high = metric["ci95"]
        return f"{metric['rate']:.0%} ({metric['k']}/{metric['n']}, 95% CI {low:.0%}-{high:.0%})"

    lines = [
        f"  Right passage retrieved (top 5)   {fmt(s['retrieval_hit@5'])}",
        f"  Correct answers                   {fmt(s['answer_correct'])}",
    ]
    lines += [f"      {k:<26}  {fmt(v)}" for k, v in s["answer_correct_by_type"].items()]
    lines += [
        f"  Correct abstentions               {fmt(s['correct_abstention'])}",
        f"  Made-up answers (unanswerable)    {fmt(s['hallucination_on_unanswerable'])}",
        f"  Wrong abstentions                 {fmt(s['false_abstention'])}",
        "  Citation precision                "
        + (f"{s['citation_precision']:.0%}" if s["citation_precision"] is not None else "n/a"),
        f"  Latency median / max              {s['median_latency_s']:.1f} s / "
        f"{s['max_latency_s']:.1f} s",
        f"  Tokens per question (mean)        {s['mean_tokens']:.0f}",
    ]
    return "\n".join(lines)


@app.command()
def bootstrap(
    config: Path = typer.Option(Path("configs/default.yaml"), help="Pipeline config."),
) -> None:
    """Build the corpus and the index if the database is empty (first start in Docker)."""
    from aerodoc.corpus import build_corpus
    from aerodoc.index import build_index
    from aerodoc.pipeline_config import load_config

    with db.connect() as conn:
        exists = conn.execute("SELECT to_regclass('chunks') IS NOT NULL").fetchone()[0]
        n = conn.execute("SELECT count(*) FROM chunks").fetchone()[0] if exists else 0
        if n:
            typer.echo(f"Index already built ({n} chunks): nothing to do.")
            return
        typer.echo("First start: downloading the corpus and building the index (~10 min).")
        build_corpus(Path("configs/corpus.yaml"), Path("data"))
        n = build_index(conn, load_config(config), Path("data"))
    typer.echo(f"Indexed {n} chunks.")


@app.command()
def version() -> None:
    """Print the AeroDoc version."""
    from aerodoc import __version__

    typer.echo(__version__)


if __name__ == "__main__":
    app()
