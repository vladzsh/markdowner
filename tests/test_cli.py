from pathlib import Path

from typer.testing import CliRunner

from markdowner.cli import app, resolve_out

runner = CliRunner()


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


def test_cli_help_shows_link_or_file_metavar() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "<link|file>" in result.stdout
    assert "[path]" in result.stdout


def test_cli_missing_file_gives_clean_error(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist.mp3"
    result = runner.invoke(app, [str(missing)])
    assert result.exit_code != 0
    combined = (result.stdout or "") + (result.stderr or "")
    assert "local file does not exist" in combined or "does-not-exist" in combined
