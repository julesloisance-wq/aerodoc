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
def version() -> None:
    """Print the AeroDoc version."""
    from aerodoc import __version__

    typer.echo(__version__)


if __name__ == "__main__":
    app()
