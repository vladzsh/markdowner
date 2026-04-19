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
    language: str
    model: str


def transcribe(audio_path: Path, model_path: Path) -> TranscriptionResult:
    """whisper-cli subprocess → parsed segments."""
    raise NotImplementedError
