from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class IngestResult:
    audio_path: Path
    source_url: str | None
    title: str | None
    duration_sec: float | None


def ingest(source: str) -> IngestResult:
    """URL → yt-dlp; local file → passthrough."""
    raise NotImplementedError
