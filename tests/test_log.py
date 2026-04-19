import pytest

from markdowner import log


@pytest.fixture(autouse=True)
def reset_quiet():
    log.set_quiet(False)
    yield
    log.set_quiet(False)


def test_stage_quiet_mode_still_yields_ctx():
    log.set_quiet(True)
    with log.stage("anything") as s:
        s.detail = "whatever"
    assert s.detail == "whatever"


def test_stage_captures_detail_without_error(capsys):
    with log.stage("doing thing") as s:
        s.detail = "42 items"
    err = capsys.readouterr().err
    assert "doing thing" in err
    assert "42 items" in err
    assert "✓" in err


def test_stage_marks_failure(capsys):
    with pytest.raises(ValueError):
        with log.stage("risky"):
            raise ValueError("boom")
    err = capsys.readouterr().err
    assert "risky" in err
    assert "✗" in err
