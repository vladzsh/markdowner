from __future__ import annotations

import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import typer

from markdowner import audio, cleaner, emit, ingest, transcribe

app = typer.Typer(
    help="URL / audio / video → structured .md for LLM Wiki",
    no_args_is_help=True,
    add_completion=False,
)

_DEFAULT_MODEL = Path(
    os.environ.get(
        "MARKDOWNER_WHISPER_MODEL",
        str(
            Path.home()
            / "Library/Application Support/github.com.thewh1teagle.vibe/ggml-large-v3-turbo.bin"
        ),
    )
)
_DEFAULT_LLM = os.environ.get("MARKDOWNER_LLM_MODEL", "gemini-2.5-flash-lite")


def resolve_out(path: Path | None, stem: str, cwd: Path | None = None) -> Path | None:
    """None → stdout; '.' → <cwd>/<stem>.md; existing dir → <dir>/<stem>.md; else → path verbatim."""
    if path is None:
        return None
    base = cwd or Path.cwd()
    if str(path) == ".":
        return base / f"{stem}.md"
    if path.exists() and path.is_dir():
        return path / f"{stem}.md"
    return path


@app.command()
def run(
    link: str = typer.Argument(..., help="URL or path to local audio/video file"),
    path: Path | None = typer.Argument(
        None,
        help="Output: omit for stdout; '.' → <slug>.md in cwd; file → write there; dir → <dir>/<slug>.md",
    ),
    clean: bool = typer.Option(False, "--clean", help="Run LLM cleanup (opt-in, needs `llm` CLI)"),
    model: Path = typer.Option(_DEFAULT_MODEL, "--model", help="Whisper model .bin"),
    llm_model: str = typer.Option(_DEFAULT_LLM, "--llm-model", help="Model for --clean via simonw/llm"),
) -> None:
    """Transcribe a URL or local media file into a markdown note."""
    with TemporaryDirectory(prefix="markdowner-") as tmp_str:
        tmp = Path(tmp_str)
        ingested = ingest.ingest(link, tmp)
        wav = audio.to_whisper_wav(ingested.audio_path, tmp / "whisper-input.wav")
        transcript = transcribe.transcribe(wav, model)
        if clean:
            transcript = cleaner.clean(transcript, model=llm_model)
        content = emit.render(ingested, transcript)

    out_path = resolve_out(path, ingested.suggested_stem)
    if out_path is None:
        sys.stdout.write(content)
    else:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        typer.echo(f"wrote {out_path}", err=True)


if __name__ == "__main__":
    app()
