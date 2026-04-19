from markdowner.transcribe import TranscriptionResult


def clean(transcript: TranscriptionResult) -> TranscriptionResult:
    """LLM noise-remover: філлери, повтори, 'ну/типу'. MVP — noop."""
    return transcript
