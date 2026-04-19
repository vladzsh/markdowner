from pathlib import Path

import typer

app = typer.Typer(help="URL / audio / video → structured .md for LLM Wiki")


@app.command()
def run(
    source: str = typer.Argument(..., help="URL або шлях до локального файлу"),
    output_dir: Path = typer.Option(Path.cwd(), "--out", "-o", help="Куди писати .md"),
    clean: bool = typer.Option(False, "--clean", help="LLM cleanup (opt-in)"),
) -> None:
    """Pipeline: ingest → transcribe → clean (optional) → emit."""
    raise NotImplementedError("Pipeline skeleton — див. TODO у src/markdowner/")


if __name__ == "__main__":
    app()
