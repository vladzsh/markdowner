from pathlib import Path

from markdowner.cli import resolve_out


def test_resolve_out_none_is_stdout() -> None:
    assert resolve_out(None, "slug") is None


def test_resolve_out_dot_uses_cwd(tmp_path: Path) -> None:
    result = resolve_out(Path("."), "my-slug", cwd=tmp_path)
    assert result == tmp_path / "my-slug.md"


def test_resolve_out_existing_dir_appends_slug(tmp_path: Path) -> None:
    result = resolve_out(tmp_path, "note")
    assert result == tmp_path / "note.md"


def test_resolve_out_explicit_file_kept_verbatim(tmp_path: Path) -> None:
    target = tmp_path / "custom.md"
    result = resolve_out(target, "ignored")
    assert result == target


def test_resolve_out_nonexistent_path_treated_as_file(tmp_path: Path) -> None:
    target = tmp_path / "future" / "note.md"
    result = resolve_out(target, "ignored")
    assert result == target
