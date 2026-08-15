"""High-level composite pipelines that chain multiple capabilities together."""

import os
import tempfile
from typing import Optional

from .asr import transcribe_audio
from .ffmpeg_ops import _exists, add_subtitle, probe_duration
from .subtitle import make_srt


def auto_subtitle(
    video_path: str,
    output_path: str,
    model: str = "stepaudio-2.5-asr",
    font_name: str = "Microsoft YaHei",
    font_size: int = 24,
    primary_color: str = "&H00FFFFFF",
    outline_color: str = "&H00000000",
) -> dict:
    """One-shot "auto caption" pipeline.

    1. Transcribe the video's audio via StepFun ASR.
    2. Turn the text into an SRT timed to the video duration.
    3. Burn the SRT into the video.

    Returns a dict with the output path and the transcribed text."""
    _exists(video_path)
    text = transcribe_audio(video_path, model=model)
    if not text:
        raise RuntimeError("Transcription returned empty text; nothing to caption.")

    fd, tmp_srt = tempfile.mkstemp(suffix=".srt")
    os.close(fd)
    try:
        duration = probe_duration(video_path)
        make_srt(text, tmp_srt, duration=duration)
        out = add_subtitle(
            video_path,
            tmp_srt,
            output_path,
            font_name=font_name,
            font_size=font_size,
            primary_color=primary_color,
            outline_color=outline_color,
        )
    finally:
        if os.path.exists(tmp_srt):
            os.remove(tmp_srt)

    return {"output_path": out, "text": text}
