from __future__ import annotations

import subprocess

from markdowner.transcribe import Segment, TranscriptionResult

PROMPT = """Clean up the following transcript by removing filler words (um, uh, like, \
you know, "ну", "типу", "короче"), repeated words, false starts, and stammering. \
Keep the meaning and information intact.

IMPORTANT:
- Do NOT translate. Keep the original language exactly.
- Do NOT add comments, explanations, headers, or markdown.
- Return ONLY the cleaned transcript text.
- Stay as close to the original wording as possible.

Transcript:
"""


def _chunks(text: str, size: int = 15000) -> list[str]:
    """Split at sentence boundaries; keep each chunk ≤ size."""
    if len(text) <= size:
        return [text]
    parts: list[str] = []
    buf: list[str] = []
    cur = 0
    for sentence in text.split(". "):
        added = len(sentence) + 2
        if cur + added > size and buf:
            parts.append(". ".join(buf))
            buf = [sentence]
            cur = added
        else:
            buf.append(sentence)
            cur += added
    if buf:
        parts.append(". ".join(buf))
    return parts


def _call_llm(body: str, model: str, timeout: int) -> str:
    result = subprocess.run(
        ["llm", "-m", model, PROMPT + body],
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.stdout.strip()


def clean(
    transcript: TranscriptionResult,
    model: str = "gemini-2.5-flash-lite",
    timeout_per_chunk: int = 180,
) -> TranscriptionResult:
    """LLM noise-remover via `llm` CLI. Degrades to raw chunk on failure."""
    full_text = " ".join(seg.text for seg in transcript.segments).strip()
    if not full_text:
        return transcript

    cleaned_parts: list[str] = []
    for chunk in _chunks(full_text):
        try:
            cleaned_parts.append(_call_llm(chunk, model, timeout_per_chunk))
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            cleaned_parts.append(chunk)

    cleaned_text = "\n\n".join(cleaned_parts)
    single = Segment(
        start=transcript.segments[0].start,
        end=transcript.segments[-1].end,
        text=cleaned_text,
    )
    return TranscriptionResult(
        segments=[single],
        language=transcript.language,
        model=f"{transcript.model}+clean:{model}",
    )
