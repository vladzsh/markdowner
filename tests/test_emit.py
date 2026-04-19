from datetime import date
from pathlib import Path

from markdowner.emit import render
from markdowner.ingest import IngestResult
from markdowner.transcribe import Segment, TranscriptionResult


def _make_ingest(**overrides) -> IngestResult:
    base = dict(
        audio_path=Path("/tmp/x.m4a"),
        source_url="https://youtube.com/watch?v=abc",
        title="Sample Title",
        uploader="Jane Doe",
        upload_date="20260415",
        duration_sec=123.5,
        suggested_stem="sample-title",
    )
    base.update(overrides)
    return IngestResult(**base)


def _make_transcript(**overrides) -> TranscriptionResult:
    base = dict(
        segments=[Segment(0.0, 1.0, "Привіт"), Segment(1.0, 2.0, "світ")],
        language="uk",
        model="ggml-large-v3-turbo",
    )
    base.update(overrides)
    return TranscriptionResult(**base)


def test_render_full_frontmatter() -> None:
    content = render(_make_ingest(), _make_transcript())

    assert content.startswith("---\n")
    assert 'title: "Sample Title"' in content
    assert "source: https://youtube.com/watch?v=abc" in content
    assert 'uploader: "Jane Doe"' in content
    assert "upload_date: 20260415" in content
    assert "duration_sec: 123.5" in content
    assert "language: uk" in content
    assert "model: ggml-large-v3-turbo" in content
    assert f"created: {date.today().isoformat()}" in content
    assert "# Sample Title" in content
    assert "Привіт" in content
    assert "світ" in content


def test_render_local_file_omits_url_fields() -> None:
    ingested = _make_ingest(
        source_url=None, uploader=None, upload_date=None, duration_sec=None, title="rec"
    )
    content = render(ingested, _make_transcript(language=None))

    assert "source:" not in content
    assert "uploader:" not in content
    assert "upload_date:" not in content
    assert "duration_sec:" not in content
    assert "language:" not in content
    assert "model: ggml-large-v3-turbo" in content


def test_render_escapes_quotes_in_title() -> None:
    content = render(_make_ingest(title='He said "hi"'), _make_transcript())
    assert 'title: "He said \\"hi\\""' in content
