"""
Media Studio SDK & Tool Suite
"""

from .config import StudioConfig
from .client import StudioClient
from .tts import synthesize_speech
from .voice_clone import preview_voice, create_voice, list_system_voices
from .image import generate_image, edit_image
from .video import understand_video
from .asr import transcribe_audio
from .subtitle import make_srt
from .pipeline import auto_subtitle

__version__ = "1.2.0"
__all__ = [
    "StudioConfig",
    "StudioClient",
    "synthesize_speech",
    "preview_voice",
    "create_voice",
    "list_system_voices",
    "generate_image",
    "edit_image",
    "understand_video",
    "transcribe_audio",
    "make_srt",
    "auto_subtitle",
]
