from pathlib import Path

import pytest

from markdowner.ingest import ingest_file, is_url, slugify


@pytest.mark.parametrize(
    "src,expected",
    [
        ("https://youtube.com/watch?v=abc", True),
        ("http://example.com/foo.mp3", True),
        ("./local/file.mp3", False),
        ("/abs/path.wav", False),
        ("ftp://example.com/x", False),
        ("just text", False),
    ],
)
def test_is_url(src: str, expected: bool) -> None:
    assert is_url(src) is expected


def test_slugify_basic() -> None:
    assert slugify("Hello World!") == "hello-world"
    assert slugify("  spaces  and   tabs\t") == "spaces-and-tabs"


def test_slugify_unicode_preserved() -> None:
    # Ukrainian letters should survive slugification
    assert slugify("Привіт Світ") == "привіт-світ"


def test_slugify_fallback_for_empty() -> None:
    assert slugify("!!!", fallback="x") == "x"
    assert slugify("", fallback="y") == "y"


def test_slugify_truncation() -> None:
    assert len(slugify("a" * 500)) <= 80


def test_ingest_file_passthrough(tmp_path: Path) -> None:
    f = tmp_path / "My Recording.m4a"
    f.write_bytes(b"")

    result = ingest_file(f)

    assert result.audio_path == f.resolve()
    assert result.source_url is None
    assert result.title == "My Recording"
    assert result.suggested_stem == "my-recording"
    assert result.duration_sec is None


def test_ingest_file_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        ingest_file(tmp_path / "nope.mp3")
