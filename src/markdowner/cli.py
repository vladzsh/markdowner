from __future__ import annotations

import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import typer

from markdowner import audio, cleaner, emit, ingest, log, transcribe

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
    source: str = typer.Argument(
        ...,
        metavar="<link|file>",
        help="URL (any yt-dlp-supported site) or path to a local audio/video file",
    ),
    path: Path | None = typer.Argument(
        None,
        metavar="[path]",
        help="Output: omit for stdout; '.' → <slug>.md in cwd; file → write there; dir → <dir>/<slug>.md",
    ),
    clean: bool = typer.Option(False, "--clean", help="Run LLM cleanup (opt-in, needs `llm` CLI)"),
    model: Path = typer.Option(_DEFAULT_MODEL, "--model", help="Whisper model .bin"),
    llm_model: str = typer.Option(_DEFAULT_LLM, "--llm-model", help="Model for --clean via simonw/llm"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress progress output"),
) -> None:
    """Transcribe a URL or local media file into a markdown note."""
    log.set_quiet(quiet)

    with TemporaryDirectory(prefix="markdowner-") as tmp_str:
        tmp = Path(tmp_str)

        kind = "URL" if ingest.is_url(source) else "file"
        with log.stage(f"ingesting {kind} [bold]{source}[/bold]") as s:
            try:
                ingested = ingest.ingest(source, tmp)
            except FileNotFoundError as e:
                raise typer.BadParameter(f"local file does not exist: {e}") from e
            bits = []
            if ingested.title:
                bits.append(f'"{ingested.title}"')
            if ingested.duration_sec:
                bits.append(f"{ingested.duration_sec:.0f}s")
            if ingested.uploader:
                bits.append(f"by {ingested.uploader}")
            s.detail = ", ".join(bits) or None

        with log.stage("transcoding to 16kHz mono WAV") as s:
            wav = audio.to_whisper_wav(ingested.audio_path, tmp / "whisper-input.wav")
            s.detail = f"{wav.stat().st_size // 1024} KiB"

        with log.stage(f"transcribing with [bold]{model.stem}[/bold]") as s:
            transcript = transcribe.transcribe(wav, model)
            s.detail = f"{len(transcript.segments)} segments, lang={transcript.language}"

        if clean:
            with log.stage(f"cleaning with [bold]{llm_model}[/bold]"):
                transcript = cleaner.clean(transcript, model=llm_model)

        with log.stage("rendering markdown") as s:
            content = emit.render(ingested, transcript)
            s.detail = f"{len(content)} chars"

    out_path = resolve_out(path, ingested.suggested_stem)
    if out_path is None:
        sys.stdout.write(content)
    else:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        log.info(f"[green]wrote[/green] {out_path}")


if __name__ == "__main__":
    app()
