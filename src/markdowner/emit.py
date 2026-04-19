from __future__ import annotations

from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from markdowner.ingest import IngestResult
from markdowner.transcribe import TranscriptionResult

TEMPLATES_DIR = Path(__file__).parent / "templates"


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=False,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render(ingest: IngestResult, transcript: TranscriptionResult) -> str:
    env = _env()
    template = env.get_template("note.md.j2")
    return template.render(
        title=ingest.title,
        source=ingest.source_url,
        uploader=ingest.uploader,
        upload_date=ingest.upload_date,
        duration_sec=ingest.duration_sec,
        language=transcript.language,
        model=transcript.model,
        created=date.today().isoformat(),
        segments=transcript.segments,
    )
