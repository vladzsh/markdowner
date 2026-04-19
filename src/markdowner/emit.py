from dataclasses import dataclass
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from markdowner.ingest import IngestResult
from markdowner.transcribe import TranscriptionResult

TEMPLATES_DIR = Path(__file__).parent / "templates"


@dataclass(frozen=True)
class NoteFrontmatter:
    source: str | None
    type: str
    duration_sec: float | None
    model: str
    created: date
    title: str | None


def build_frontmatter(
    ingest: IngestResult, transcript: TranscriptionResult
) -> NoteFrontmatter:
    return NoteFrontmatter(
        source=ingest.source_url,
        type="audio" if ingest.source_url is None else "url",
        duration_sec=ingest.duration_sec,
        model=transcript.model,
        created=date.today(),
        title=ingest.title,
    )


def emit(
    ingest: IngestResult,
    transcript: TranscriptionResult,
    output_dir: Path,
) -> Path:
    """Render Jinja template → .md file, return path."""
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(),
        keep_trailing_newline=True,
    )
    template = env.get_template("note.md.j2")
    frontmatter = build_frontmatter(ingest, transcript)
    rendered = template.render(fm=frontmatter, segments=transcript.segments)

    stem = (ingest.title or ingest.audio_path.stem).replace("/", "-")
    out_path = output_dir / f"{stem}.md"
    out_path.write_text(rendered, encoding="utf-8")
    return out_path
