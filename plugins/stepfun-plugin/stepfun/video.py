import os
from typing import Optional, Dict, Any
from .client import StepFunClient
from .config import StepFunConfig

def upload_video_file(file_path: str, client: StepFunClient) -> str:
    """
    Upload a local video file to StepFun files API.
    Returns file_id.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Video file not found: {file_path}")
        
    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()
    content_type = "video/mp4" if ext == ".mp4" else "application/octet-stream"
    
    with open(file_path, "rb") as f:
        file_bytes = f.read()
        
    fields = {"purpose": "storage"}
    files = {"file": (filename, file_bytes, content_type)}
    
    res = client.post_multipart("/files", fields, files)
    file_id = res.get("id")
    if not file_id:
        raise RuntimeError(f"Failed to upload video file. Response: {res}")
    return file_id

def understand_video(
    video_input: str,
    prompt: str = "请概括这个视频的主要内容",
    model: str = "step-3.7-flash",
    config: Optional[StepFunConfig] = None
) -> str:
    """
    Understand and analyze video content from a URL or local file path.
    """
    client = StepFunClient(config)
    
    if video_input.startswith("http://") or video_input.startswith("https://"):
        video_target = video_input
    else:
        # Upload local file
        video_target = upload_video_file(video_input, client)
        
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "video_url", "video_url": {"url": video_target}}
                ]
            }
        ]
    }
    
    res = client.post_json("/chat/completions", payload)
    
    choices = res.get("choices", [])
    if not choices:
        raise RuntimeError(f"Video understanding returned no choices. Response: {res}")
        
    return choices[0].get("message", {}).get("content", "")
