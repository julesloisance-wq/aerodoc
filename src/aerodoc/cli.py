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
    """Show the passages closest to a question (no LLM involved)."""
    from aerodoc.pipeline_config import load_config
    from aerodoc.search import dense_search

    with db.connect() as conn:
        hits = dense_search(conn, question, load_config(config), k)
    for rank, hit in enumerate(hits, 1):
        text = hit.text if full else hit.text[:300] + "..."
        typer.echo(f"\n#{rank}  score {hit.score:.3f}  [{hit.citation}]\n    {text}")


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
def version() -> None:
    """Print the AeroDoc version."""
    from aerodoc import __version__

    typer.echo(__version__)


if __name__ == "__main__":
    app()
