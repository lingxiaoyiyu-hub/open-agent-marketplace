import json
from typing import Optional
from mcp.server.fastmcp import FastMCP
from .tts import synthesize_speech
from .voice_clone import preview_voice, create_voice
from .image import generate_image, edit_image
from .video import understand_video

mcp = FastMCP("stepfun-mcp-server")

@mcp.tool()
def stepfun_tts(
    text: str,
    output_path: str = "speech.mp3",
    voice: str = "cixingnansheng",
    instruction: Optional[str] = None,
    model: str = "stepaudio-2.5-tts",
    response_format: str = "mp3"
) -> str:
    """
    Synthesize speech (TTS) from text using StepFun Step Plan API.
    Supports auto-segmentation & concatenation for long text (>1000 chars).
    
    Args:
        text: Text to synthesize into speech.
        output_path: Target audio output file path.
        voice: Voice ID (default: cixingnansheng).
        instruction: Optional emotion, tone or speed instruction (e.g. "语气温柔，语速偏慢").
        model: TTS model (stepaudio-2.5-tts / step-tts-2 / step-tts-mini).
        response_format: Output audio format (mp3, wav, flac, opus, pcm).
    """
    out_file = synthesize_speech(
        text=text,
        output_path=output_path,
        voice=voice,
        instruction=instruction,
        model=model,
        response_format=response_format
    )
    return f"Successfully generated speech audio at: {out_file}"

@mcp.tool()
def stepfun_clone_preview(
    file_path: str,
    ref_text: str,
    sample_text: str,
    output_path: str = "preview.wav",
    instruction: Optional[str] = None,
    model: str = "stepaudio-2.5-tts"
) -> str:
    """
    Preview cloned voice from reference audio (5-10s mp3/wav) without creating a permanent voice_id.
    
    Args:
        file_path: Path to reference audio file (5~10 seconds).
        ref_text: Exact text spoken in the reference audio.
        sample_text: Text to synthesize for voice preview (<50 characters).
        output_path: Target audio preview output file path.
        instruction: Optional tone or speed instruction.
        model: TTS model.
    """
    out_file = preview_voice(
        file_path=file_path,
        ref_text=ref_text,
        sample_text=sample_text,
        output_path=output_path,
        instruction=instruction,
        model=model
    )
    return f"Successfully generated voice preview at: {out_file}"

@mcp.tool()
def stepfun_clone_voice(
    file_path: str,
    ref_text: str,
    model: str = "stepaudio-2.5-tts"
) -> str:
    """
    Create a permanent cloned voice ID from reference audio file (5-10s mp3/wav).
    
    Args:
        file_path: Path to reference audio file (5~10 seconds).
        ref_text: Exact text spoken in the reference audio.
        model: TTS model.
    """
    res = create_voice(
        file_path=file_path,
        ref_text=ref_text,
        model=model
    )
    return f"Successfully created cloned voice:\n{json.dumps(res, ensure_ascii=False, indent=2)}"

@mcp.tool()
def stepfun_image_generate(
    prompt: str,
    output_path: str = "generated.png",
    model: str = "step-image-edit-2",
    size: Optional[str] = None,
    cfg_scale: float = 1.0,
    steps: int = 8,
    text_mode: bool = False
) -> str:
    """
    Generate an image from text prompt using StepFun image models.
    
    Args:
        prompt: Image generation prompt (<=512 characters).
        output_path: Target image output path.
        model: Model name (step-image-edit-2 / step-2x-large).
        size: Optional dimensions (e.g. 1024x1024, 768x1360, 1360x768).
        cfg_scale: Guidance scale (default 1.0).
        steps: Generation steps (default 8).
        text_mode: Set True if the image contains rendering text.
    """
    out_file = generate_image(
        prompt=prompt,
        output_path=output_path,
        model=model,
        size=size,
        cfg_scale=cfg_scale,
        steps=steps,
        text_mode=text_mode
    )
    return f"Successfully generated image at: {out_file}"

@mcp.tool()
def stepfun_image_edit(
    image_path: str,
    prompt: str,
    output_path: str = "edited.png",
    model: str = "step-image-edit-2",
    size: Optional[str] = None,
    cfg_scale: float = 1.0,
    steps: int = 8,
    text_mode: bool = False
) -> str:
    """
    Edit an existing image with a text prompt using StepFun image edit models.
    
    Args:
        image_path: Path to input image to edit.
        prompt: Text prompt describing edits to make.
        output_path: Target output image path.
        model: Model name (step-image-edit-2).
        size: Optional output size.
        cfg_scale: Guidance scale.
        steps: Generation steps.
        text_mode: Set True if editing images with text.
    """
    out_file = edit_image(
        image_path=image_path,
        prompt=prompt,
        output_path=output_path,
        model=model,
        size=size,
        cfg_scale=cfg_scale,
        steps=steps,
        text_mode=text_mode
    )
    return f"Successfully edited image at: {out_file}"

@mcp.tool()
def stepfun_video_understand(
    video_input: str,
    prompt: str = "请概括这个视频的主要内容",
    model: str = "step-3.7-flash"
) -> str:
    """
    Understand and analyze video content from a URL or local file path.
    
    Args:
        video_input: Video URL (http/https) or local file path (MP4 <=128MB, <=5 min).
        prompt: Prompt/question about the video.
        model: Video understanding model (step-3.7-flash / step-1o-turbo-vision).
    """
    ans = understand_video(
        video_input=video_input,
        prompt=prompt,
        model=model
    )
    return f"Video Analysis Result:\n{ans}"

def main():
    mcp.run()

if __name__ == "__main__":
    main()
