"""Command-line interface: `aerodoc <command>`."""

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
def version() -> None:
    """Print the AeroDoc version."""
    from aerodoc import __version__

    typer.echo(__version__)


if __name__ == "__main__":
    app()
