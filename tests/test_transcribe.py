from markdowner.transcribe import _parse_ts, parse_whisper_json


def test_parse_ts_basic() -> None:
    assert _parse_ts("00:00:00,000") == 0.0
    assert _parse_ts("00:00:01,500") == 1.5
    assert _parse_ts("00:01:23,456") == 83.456
    assert _parse_ts("01:02:03,000") == 3723.0


def test_parse_whisper_json_happy_path() -> None:
    data = {
        "result": {"language": "uk"},
        "model": {"type": "large-v3-turbo"},
        "transcription": [
            {
                "timestamps": {"from": "00:00:00,000", "to": "00:00:02,500"},
                "text": " Привіт ",
            },
            {
                "timestamps": {"from": "00:00:02,500", "to": "00:00:05,000"},
                "text": "світ",
            },
        ],
    }
    result = parse_whisper_json(data)

    assert result.language == "uk"
    assert result.model == "large-v3-turbo"
    assert len(result.segments) == 2
    assert result.segments[0].start == 0.0
    assert result.segments[0].end == 2.5
    assert result.segments[0].text == "Привіт"  # stripped
    assert result.segments[1].text == "світ"


def test_parse_whisper_json_empty_transcription() -> None:
    result = parse_whisper_json({"result": {"language": "en"}, "transcription": []})
    assert result.segments == []
    assert result.language == "en"


def test_parse_whisper_json_missing_fields_fallback() -> None:
    result = parse_whisper_json({"transcription": []})
    assert result.language is None
    assert result.model == "whisper"
