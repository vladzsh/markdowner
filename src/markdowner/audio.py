from __future__ import annotations

import subprocess
from pathlib import Path


def to_whisper_wav(src: Path, dst: Path) -> Path:
    """Convert any audio/video file to 16 kHz mono PCM s16le — whisper-cli input format."""
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(src),
            "-ar", "16000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            str(dst),
        ],
        check=True,
        capture_output=True,
    )
    return dst
