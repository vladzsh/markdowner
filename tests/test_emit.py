from datetime import date
from pathlib import Path

from markdowner.emit import NoteFrontmatter, build_frontmatter, emit
from markdowner.ingest import IngestResult
from markdowner.transcribe import Segment, TranscriptionResult


def test_build_frontmatter_url_source() -> None:
    ingest = IngestResult(
        audio_path=Path("/tmp/x.m4a"),
        source_url="https://youtube.com/watch?v=abc",
        title="Sample",
        duration_sec=123.5,
    )
    transcript = TranscriptionResult(segments=[], language="uk", model="large-v3-turbo")

    fm = build_frontmatter(ingest, transcript)

    assert fm.source == "https://youtube.com/watch?v=abc"
    assert fm.type == "url"
    assert fm.duration_sec == 123.5
    assert fm.model == "large-v3-turbo"
    assert fm.title == "Sample"
    assert fm.created == date.today()


def test_build_frontmatter_local_file() -> None:
    ingest = IngestResult(
        audio_path=Path("/tmp/rec.m4a"),
        source_url=None,
        title=None,
        duration_sec=None,
    )
    transcript = TranscriptionResult(segments=[], language="uk", model="large-v3-turbo")

    fm = build_frontmatter(ingest, transcript)

    assert fm.source is None
    assert fm.type == "audio"
    assert fm.duration_sec is None


def test_emit_writes_markdown(tmp_path: Path) -> None:
    ingest = IngestResult(
        audio_path=tmp_path / "rec.m4a",
        source_url="https://example.com/x",
        title="Hello World",
        duration_sec=42.0,
    )
    transcript = TranscriptionResult(
        segments=[Segment(0.0, 1.0, "Привіт"), Segment(1.0, 2.0, "світ")],
        language="uk",
        model="large-v3-turbo",
    )

    out = emit(ingest, transcript, tmp_path)

    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert content.startswith("---\n")
    assert "source: https://example.com/x" in content
    assert "model: large-v3-turbo" in content
    assert "Привіт" in content
    assert "світ" in content
