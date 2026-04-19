from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class IngestResult:
    audio_path: Path
    source_url: str | None
    title: str | None
    uploader: str | None
    upload_date: str | None
    duration_sec: float | None
    suggested_stem: str


def is_url(source: str) -> bool:
    parsed = urlparse(source)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def slugify(text: str, fallback: str = "transcript", max_len: int = 80) -> str:
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip().lower()
    text = re.sub(r"[-\s]+", "-", text)
    return text[:max_len].strip("-") or fallback


def ingest_file(file_path: Path) -> IngestResult:
    file_path = file_path.expanduser().resolve()
    if not file_path.exists():
        raise FileNotFoundError(file_path)
    return IngestResult(
        audio_path=file_path,
        source_url=None,
        title=file_path.stem,
        uploader=None,
        upload_date=None,
        duration_sec=None,
        suggested_stem=slugify(file_path.stem),
    )


def ingest_url(url: str, workdir: Path) -> IngestResult:
    import yt_dlp  # deferred import — keeps `--help` fast

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(workdir / "%(id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "nopart": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        audio_path = Path(ydl.prepare_filename(info))

    title = info.get("title")
    return IngestResult(
        audio_path=audio_path,
        source_url=info.get("webpage_url") or url,
        title=title,
        uploader=info.get("uploader"),
        upload_date=info.get("upload_date"),
        duration_sec=info.get("duration"),
        suggested_stem=slugify(title or info.get("id") or "transcript"),
    )


def ingest(source: str, workdir: Path) -> IngestResult:
    """Dispatch URL → yt-dlp, otherwise treat as local file path."""
    if is_url(source):
        return ingest_url(source, workdir)
    return ingest_file(Path(source))
