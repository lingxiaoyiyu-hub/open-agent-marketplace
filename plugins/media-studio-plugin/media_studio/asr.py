"""Speech-to-text (ASR) via the Studio transcription API.

Endpoint: ``POST {base_url}/audio/transcriptions`` (multipart/form-data).
The response is JSON ``{"text": "..."}``. Video inputs are transparently
converted to audio (via ffmpeg) before transcription.
"""

import json
import os
import tempfile
from typing import List, Optional

from .client import StudioClient
from .config import StudioConfig
from .ffmpeg_ops import _exists, _has_video, extract_audio

_AUDIO_MIME = {
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
    ".oga": "audio/ogg",
    ".flac": "audio/flac",
    ".m4a": "audio/mp4",
    ".aac": "audio/aac",
    ".pcm": "audio/pcm",
}


def _guess_mime(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return _AUDIO_MIME.get(ext, "application/octet-stream")


def transcribe_audio(
    file_path: str,
    model: str = "stepaudio-2.5-asr",
    hotwords: Optional[List[str]] = None,
    config: Optional[StudioConfig] = None,
) -> str:
    """Transcribe an audio or video file into text.

    Args:
        file_path: Local audio (mp3/wav/ogg/flac/m4a) or video file path.
        model: ASR model (``stepaudio-2.5-asr`` or ``step-asr``).
        hotwords: Optional list of hot words to bias recognition.
    Returns:
        The transcribed text string.
    """
    _exists(file_path)
    client = StudioClient(config)

    audio_path = file_path
    tmp = None
    try:
        if _has_video(file_path):
            fd, tmp = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            audio_path = extract_audio(file_path, tmp, codec="pcm_s16le")

        with open(audio_path, "rb") as f:
            file_bytes = f.read()

        fields = {"model": model, "response_format": "json"}
        if hotwords:
            fields["hotwords"] = json.dumps(hotwords, ensure_ascii=False)
        files = {"file": (os.path.basename(audio_path), file_bytes, _guess_mime(audio_path))}

        res = client.post_multipart("/audio/transcriptions", fields, files)
        if isinstance(res, dict):
            return (res.get("text") or "").strip()
        return str(res).strip()
    finally:
        if tmp and os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass
