import os
import base64
import urllib.request
from typing import Optional
from .client import StepFunClient
from .config import StepFunConfig

def save_image_result(res: dict, output_path: str) -> str:
    """
    Extract b64_json or url from response and save to output_path.
    """
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
        
    data_list = res.get("data", [])
    if not data_list:
        raise RuntimeError(f"No image data returned from StepFun API. Response: {res}")
        
    first_item = data_list[0]
    
    if "b64_json" in first_item:
        img_bytes = base64.b64decode(first_item["b64_json"])
        with open(output_path, "wb") as f:
            f.write(img_bytes)
    elif "url" in first_item:
        url = first_item["url"]
        with urllib.request.urlopen(url) as resp:
            with open(output_path, "wb") as f:
                f.write(resp.read())
    else:
        raise RuntimeError(f"Unknown image format in response: {first_item}")
        
    return os.path.abspath(output_path)

def generate_image(
    prompt: str,
    output_path: str = "generated.png",
    model: str = "step-image-edit-2",
    size: Optional[str] = None,
    cfg_scale: float = 1.0,
    steps: int = 8,
    text_mode: bool = False,
    response_format: str = "b64_json",
    config: Optional[StepFunConfig] = None
) -> str:
    """
    Generate an image from a text prompt.
    """
    if len(prompt) > 512:
        prompt = prompt[:512]
        
    client = StepFunClient(config)
    
    payload = {
        "model": model,
        "prompt": prompt,
        "response_format": response_format,
        "cfg_scale": cfg_scale,
        "steps": steps,
        "text_mode": text_mode
    }
    if size:
        payload["size"] = size
        
    res = client.post_json("/images/generations", payload)
    return save_image_result(res, output_path)

def edit_image(
    image_path: str,
    prompt: str,
    output_path: str = "edited.png",
    model: str = "step-image-edit-2",
    size: Optional[str] = None,
    cfg_scale: float = 1.0,
    steps: int = 8,
    text_mode: bool = False,
    response_format: str = "b64_json",
    config: Optional[StepFunConfig] = None
) -> str:
    """
    Edit an existing image using a text prompt.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Input image not found: {image_path}")
        
    if len(prompt) > 512:
        prompt = prompt[:512]
        
    client = StepFunClient(config)
    
    fields = {
        "model": model,
        "prompt": prompt,
        "response_format": response_format,
        "cfg_scale": str(cfg_scale),
        "steps": str(steps),
        "text_mode": "true" if text_mode else "false"
    }
    if size:
        fields["size"] = size
        
    filename = os.path.basename(image_path)
    ext = os.path.splitext(filename)[1].lower()
    content_type = "image/png" if ext == ".png" else "image/jpeg"
    
    with open(image_path, "rb") as f:
        img_bytes = f.read()
        
    files = {"image": (filename, img_bytes, content_type)}
    
    res = client.post_multipart("/images/edits", fields, files)
    return save_image_result(res, output_path)
