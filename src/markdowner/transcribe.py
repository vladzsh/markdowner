from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Segment:
    start: float
    end: float
    text: str


@dataclass(frozen=True)
class TranscriptionResult:
    segments: list[Segment]
    language: str | None
    model: str


def _parse_ts(ts: str) -> float:
    """'00:01:23,456' → 83.456 seconds."""
    h, m, rest = ts.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def parse_whisper_json(data: dict) -> TranscriptionResult:
    segments = [
        Segment(
            start=_parse_ts(seg["timestamps"]["from"]),
            end=_parse_ts(seg["timestamps"]["to"]),
            text=seg["text"].strip(),
        )
        for seg in data.get("transcription", [])
    ]
    lang = (data.get("result") or {}).get("language")
    model = (data.get("model") or {}).get("type") or "whisper"
    return TranscriptionResult(segments=segments, language=lang, model=model)


def transcribe(wav_path: Path, model_path: Path) -> TranscriptionResult:
    """Run whisper-cli with JSON output, parse segments + language."""
    subprocess.run(
        [
            "whisper-cli",
            "-m", str(model_path),
            "-f", str(wav_path),
            "-oj",
        ],
        check=True,
        capture_output=True,
    )
    json_path = wav_path.with_suffix(wav_path.suffix + ".json")
    data = json.loads(json_path.read_text(encoding="utf-8"))
    result = parse_whisper_json(data)
    # stamp the file-based model name so frontmatter shows `ggml-large-v3-turbo` etc.
    return TranscriptionResult(
        segments=result.segments,
        language=result.language,
        model=model_path.stem,
    )
