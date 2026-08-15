import os
import base64
from typing import Optional, Dict, Any
from .client import StepFunClient
from .config import StepFunConfig

def upload_voice_file(file_path: str, client: StepFunClient) -> str:
    """
    Upload a 5~10 second audio file to StepFun files API with purpose=storage.
    Returns the file_id.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Reference audio file not found: {file_path}")
        
    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()
    
    content_type = "audio/mpeg" if ext in [".mp3"] else "audio/wav"
    
    with open(file_path, "rb") as f:
        file_bytes = f.read()
        
    fields = {"purpose": "storage"}
    files = {"file": (filename, file_bytes, content_type)}
    
    res = client.post_multipart("/files", fields, files)
    file_id = res.get("id")
    if not file_id:
        raise RuntimeError(f"Failed to upload voice file. Response: {res}")
    return file_id

def preview_voice(
    file_path: str,
    ref_text: str,
    sample_text: str,
    output_path: str = "preview.wav",
    instruction: Optional[str] = None,
    model: str = "stepaudio-2.5-tts",
    config: Optional[StepFunConfig] = None
) -> str:
    """
    Preview cloned voice without creating a permanent voice ID.
    Decodes the returned base64 wav audio into output_path.
    """
    client = StepFunClient(config)
    file_id = upload_voice_file(file_path, client)
    
    payload = {
        "file_id": file_id,
        "model": model,
        "text": ref_text,
        "sample_text": sample_text,
    }
    if instruction:
        payload["instruction"] = instruction
        
    res = client.post_json("/audio/voices/preview", payload)
    
    sample_audio_b64 = res.get("sample_audio")
    if not sample_audio_b64:
        raise RuntimeError(f"Voice preview failed, missing sample_audio in response: {res}")
        
    audio_bytes = base64.b64decode(sample_audio_b64)
    
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
        
    with open(output_path, "wb") as f:
        f.write(audio_bytes)
        
    return os.path.abspath(output_path)

def create_voice(
    file_path: str,
    ref_text: str,
    model: str = "stepaudio-2.5-tts",
    config: Optional[StepFunConfig] = None
) -> Dict[str, Any]:
    """
    Create a permanent cloned voice.
    Returns response dict containing voice_id / id.
    """
    client = StepFunClient(config)
    file_id = upload_voice_file(file_path, client)
    
    payload = {
        "file_id": file_id,
        "model": model,
        "text": ref_text
    }
    
    res = client.post_json("/audio/voices", payload)
    return res


def list_system_voices(
    model: str = "step-tts-2",
    config: Optional[StepFunConfig] = None
) -> Dict[str, Any]:
    """List official StepFun system voices.

    Returns the raw response containing ``voices`` (a list of voice ID strings)
    and ``voices-details`` (a dict keyed by voice ID with name/description)."""
    client = StepFunClient(config)
    return client.get_json("/audio/system_voices", {"model": model})
