import json
from typing import List, Optional

from mcp.server.fastmcp import FastMCP

from . import ffmpeg_ops
from .asr import transcribe_audio
from .image import generate_image, edit_image
from .pipeline import auto_subtitle
from .subtitle import make_srt
from .tts import synthesize_speech
from .video import understand_video
from .voice_clone import preview_voice, create_voice, list_system_voices

mcp = FastMCP("stepfun-mcp-server")


# --------------------------------------------------------------------------
# Voice (TTS / voice clone / voice list)
# --------------------------------------------------------------------------
@mcp.tool()
def stepfun_tts(
    text: str,
    output_path: str = "speech.mp3",
    voice: str = "cixingnansheng",
    instruction: Optional[str] = None,
    model: str = "stepaudio-2.5-tts",
    response_format: str = "mp3",
    speed: Optional[float] = None,
    volume: Optional[float] = None,
    sample_rate: Optional[int] = None,
    text_normalization: Optional[str] = None,
) -> str:
    """
    Synthesize speech (TTS, 配音) from text using StepFun. Long text is auto-split
    and concatenated seamlessly via ffmpeg.

    Args:
        text: Text to synthesize into speech.
        output_path: Target audio output file path.
        voice: Voice ID (default: cixingnansheng). Use stepfun_list_voices to browse.
        instruction: Optional emotion/tone/speed instruction (stepaudio-2.5-tts only).
        model: TTS model (stepaudio-2.5-tts / step-tts-2 / step-tts-mini).
        response_format: Output audio format (mp3, wav, flac, opus, pcm).
        speed: Optional speed 0.5~2.0.
        volume: Optional volume 0.1~2.0.
        sample_rate: Optional sample rate (8000/16000/22050/24000/48000).
        text_normalization: Optional "standard" or "enhanced".
    """
    out_file = synthesize_speech(
        text=text,
        output_path=output_path,
        voice=voice,
        instruction=instruction,
        model=model,
        response_format=response_format,
        speed=speed,
        volume=volume,
        sample_rate=sample_rate,
        text_normalization=text_normalization,
    )
    return f"Successfully generated speech audio at: {out_file}"


@mcp.tool()
def stepfun_list_voices(model: str = "step-tts-2") -> str:
    """
    List official StepFun system voices (voice IDs + descriptions).

    Args:
        model: Voice list model (currently only "step-tts-2").
    """
    res = list_system_voices(model=model)
    return json.dumps(res, ensure_ascii=False, indent=2)


@mcp.tool()
def stepfun_clone_preview(
    file_path: str,
    ref_text: str,
    sample_text: str,
    output_path: str = "preview.wav",
    instruction: Optional[str] = None,
    model: str = "stepaudio-2.5-tts",
) -> str:
    """
    Preview a cloned voice from a 5-10s reference audio without creating a permanent voice_id.

    Args:
        file_path: Path to reference audio file (5~10 seconds, mp3/wav).
        ref_text: Exact text spoken in the reference audio.
        sample_text: Text to synthesize for the preview (<50 characters).
        output_path: Target preview audio output path.
        instruction: Optional tone/speed instruction.
        model: TTS model.
    """
    out_file = preview_voice(
        file_path=file_path,
        ref_text=ref_text,
        sample_text=sample_text,
        output_path=output_path,
        instruction=instruction,
        model=model,
    )
    return f"Successfully generated voice preview at: {out_file}"


@mcp.tool()
def stepfun_clone_voice(
    file_path: str,
    ref_text: str,
    model: str = "stepaudio-2.5-tts",
) -> str:
    """
    Create a permanent cloned voice ID from a 5-10s reference audio file.

    Args:
        file_path: Path to reference audio file (5~10 seconds, mp3/wav).
        ref_text: Exact text spoken in the reference audio.
        model: TTS model.
    """
    res = create_voice(file_path=file_path, ref_text=ref_text, model=model)
    return f"Successfully created cloned voice:\n{json.dumps(res, ensure_ascii=False, indent=2)}"


# --------------------------------------------------------------------------
# Speech-to-text / subtitles
# --------------------------------------------------------------------------
@mcp.tool()
def stepfun_transcribe(
    file_path: str,
    model: str = "stepaudio-2.5-asr",
    hotwords: Optional[List[str]] = None,
) -> str:
    """
    Transcribe an audio or video file into text (语音转文字 / ASR). Video inputs are
    automatically converted to audio first.

    Args:
        file_path: Local audio (mp3/wav/ogg/flac/m4a) or video file path.
        model: ASR model (stepaudio-2.5-asr or step-asr).
        hotwords: Optional list of hot words to bias recognition.
    """
    text = transcribe_audio(file_path=file_path, model=model, hotwords=hotwords)
    return text


@mcp.tool()
def stepfun_make_srt(
    text: str,
    output_path: str,
    duration: Optional[float] = None,
    max_chars: int = 28,
) -> str:
    """
    Turn plain text into an SRT subtitle file (加字幕前的字幕文件生成).

    Args:
        text: The subtitle text (e.g. transcription result).
        output_path: Target .srt file path.
        duration: Optional media duration in seconds to spread segments evenly; omit
            for a rough default per-segment length.
        max_chars: Max characters per subtitle line.
    """
    out = make_srt(text=text, output_path=output_path, duration=duration, max_chars=max_chars)
    return f"Successfully wrote subtitle file at: {out}"


@mcp.tool()
def stepfun_auto_subtitle(
    video_path: str,
    output_path: str,
    model: str = "stepaudio-2.5-asr",
    font_name: str = "Microsoft YaHei",
    font_size: int = 24,
) -> str:
    """
    One-shot auto caption: transcribe a video's speech, generate timed SRT, and burn
    it into the video (一键自动加字幕).

    Args:
        video_path: Input video file path.
        output_path: Output video file path with burned-in subtitles.
        model: ASR model.
        font_name: Subtitle font family name.
        font_size: Subtitle font size.
    """
    res = auto_subtitle(
        video_path=video_path,
        output_path=output_path,
        model=model,
        font_name=font_name,
        font_size=font_size,
    )
    return f"Subtitle burned to: {res['output_path']}\nTranscript: {res['text']}"


# --------------------------------------------------------------------------
# Image generation / edit
# --------------------------------------------------------------------------
@mcp.tool()
def stepfun_image_generate(
    prompt: str,
    output_path: str = "generated.png",
    model: str = "step-image-edit-2",
    size: Optional[str] = None,
    cfg_scale: float = 1.0,
    steps: int = 8,
    text_mode: bool = False,
) -> str:
    """
    Generate an image from a text prompt using StepFun image models (文生图).

    Args:
        prompt: Image generation prompt (<=512 characters).
        output_path: Target image output path.
        model: Model name (step-image-edit-2 / step-2x-large).
        size: Optional dimensions (e.g. 1024x1024, 768x1360, 1360x768).
        cfg_scale: Guidance scale (default 1.0).
        steps: Generation steps (default 8).
        text_mode: Set True if the image contains rendered text.
    """
    out_file = generate_image(
        prompt=prompt,
        output_path=output_path,
        model=model,
        size=size,
        cfg_scale=cfg_scale,
        steps=steps,
        text_mode=text_mode,
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
    text_mode: bool = False,
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
        text_mode=text_mode,
    )
    return f"Successfully edited image at: {out_file}"


@mcp.tool()
def stepfun_video_understand(
    video_input: str,
    prompt: str = "请概括这个视频的主要内容",
    model: str = "step-3.7-flash",
) -> str:
    """
    Understand and analyze video content from a URL or local file path (视频理解).

    Args:
        video_input: Video URL (http/https) or local file path (MP4 <=128MB, <=5 min).
        prompt: Prompt/question about the video.
        model: Video understanding model (step-3.7-flash / step-1o-turbo-vision).
    """
    ans = understand_video(video_input=video_input, prompt=prompt, model=model)
    return f"Video Analysis Result:\n{ans}"


# --------------------------------------------------------------------------
# Local media editing (ffmpeg) — subtitle burn / mixcut / roughcut / convert
# --------------------------------------------------------------------------
@mcp.tool()
def media_info(file_path: str) -> dict:
    """
    Read media metadata (duration, resolution, codec, streams) via ffprobe.

    Args:
        file_path: Local media file path.
    """
    return ffmpeg_ops.media_info(file_path)


@mcp.tool()
def media_add_subtitle(
    video_path: str,
    srt_path: str,
    output_path: str,
    font_name: str = "Microsoft YaHei",
    font_size: int = 24,
    primary_color: str = "&H00FFFFFF",
    outline_color: str = "&H00000000",
    outline: int = 1,
    alignment: Optional[int] = None,
) -> str:
    """
    Burn an SRT subtitle file into a video (给视频加字幕).

    Args:
        video_path: Input video path.
        srt_path: Input .srt subtitle path.
        output_path: Output video path.
        font_name: Font family name (e.g. "Microsoft YaHei", "SimHei").
        font_size: Font size in px.
        primary_color: ASS colour hex (default white &H00FFFFFF).
        outline_color: ASS outline colour hex (default black &H00000000).
        outline: Outline width.
        alignment: Optional ASS alignment number (1-9).
    """
    out = ffmpeg_ops.add_subtitle(
        video_path=video_path,
        srt_path=srt_path,
        output_path=output_path,
        font_name=font_name,
        font_size=font_size,
        primary_color=primary_color,
        outline_color=outline_color,
        outline=outline,
        alignment=alignment,
    )
    return f"Successfully burned subtitle into: {out}"


@mcp.tool()
def media_mixcut(
    inputs: List[str],
    output_path: str,
    duration: float,
    segment: float = 4.0,
    transition: bool = False,
    transition_duration: float = 0.5,
    width: int = 1280,
    height: int = 720,
    fps: int = 30,
    voiceover: Optional[str] = None,
    bgm: Optional[str] = None,
    bgm_volume: float = 0.25,
    subtitle: Optional[str] = None,
) -> str:
    """
    Randomly trim & concatenate multiple video clips into one target-length video
    (视频混剪). Optionally add crossfade transitions, a voiceover, background music
    and a burned-in subtitle track.

    Args:
        inputs: List of input video file paths.
        output_path: Output video path.
        duration: Target total duration in seconds.
        segment: Per-clip segment length in seconds (default 4.0).
        transition: Enable crossfade transitions between clips.
        transition_duration: Transition length in seconds.
        width: Output width.
        height: Output height.
        fps: Output frame rate.
        voiceover: Optional voiceover audio path (replaces source audio).
        bgm: Optional background music path.
        bgm_volume: Background music volume (0~1, default 0.25).
        subtitle: Optional .srt path to burn in.
    """
    out = ffmpeg_ops.mixcut(
        inputs=inputs,
        output_path=output_path,
        duration=duration,
        segment=segment,
        transition=transition,
        transition_duration=transition_duration,
        width=width,
        height=height,
        fps=fps,
        voiceover=voiceover,
        bgm=bgm,
        bgm_volume=bgm_volume,
        subtitle=subtitle,
    )
    return f"Successfully created mashup video at: {out}"


@mcp.tool()
def media_roughcut(
    input_path: str,
    output_path: str,
    threshold: str = "-35dB",
    min_silence: float = 0.4,
) -> str:
    """
    Remove long silences from a talking-head video (视频粗剪 - 去停顿).

    Args:
        input_path: Input video path.
        output_path: Output video path.
        threshold: Silence threshold in dB (default -35dB).
        min_silence: Minimum silence duration in seconds to remove (default 0.4).
    """
    out = ffmpeg_ops.roughcut(
        input_path=input_path,
        output_path=output_path,
        threshold=threshold,
        min_silence=min_silence,
    )
    return f"Successfully rough-cut video at: {out}"


@mcp.tool()
def media_convert(
    input_path: str,
    output_path: str,
    vcodec: str = "libx264",
    crf: int = 23,
    preset: str = "medium",
    acodec: str = "aac",
    audio_bitrate: str = "128k",
    scale: Optional[str] = None,
    fps: Optional[float] = None,
) -> str:
    """
    Transcode / convert a video (转码/转格式/调尺寸/调帧率).

    Args:
        input_path: Input media path.
        output_path: Output media path.
        vcodec: Video codec (default libx264).
        crf: Quality (lower = better, default 23).
        preset: Encoder preset (default medium).
        acodec: Audio codec (default aac).
        audio_bitrate: Audio bitrate (default 128k).
        scale: Optional target size (e.g. "1280:720").
        fps: Optional frame rate.
    """
    out = ffmpeg_ops.convert_video(
        input_path=input_path,
        output_path=output_path,
        vcodec=vcodec,
        crf=crf,
        preset=preset,
        acodec=acodec,
        audio_bitrate=audio_bitrate,
        scale=scale,
        fps=fps,
    )
    return f"Successfully converted to: {out}"


@mcp.tool()
def media_merge(inputs: List[str], output_path: str, reencode: bool = False) -> str:
    """
    Concatenate multiple media files into one (合并媒体).

    Args:
        inputs: List of media file paths (same codec/params recommended).
        output_path: Output media path.
        reencode: Set True to re-encode instead of stream copy.
    """
    out = ffmpeg_ops.merge_media(inputs=inputs, output_path=output_path, reencode=reencode)
    return f"Successfully merged into: {out}"


@mcp.tool()
def media_trim(
    input_path: str,
    output_path: str,
    start: float = 0.0,
    end: Optional[float] = None,
    duration: Optional[float] = None,
    reencode: bool = False,
) -> str:
    """
    Cut a segment out of a media file (裁剪媒体).

    Args:
        input_path: Input media path.
        output_path: Output media path.
        start: Start time in seconds.
        end: End time in seconds (alternative to duration).
        duration: Segment length in seconds (alternative to end).
        reencode: Set True to re-encode instead of stream copy.
    """
    out = ffmpeg_ops.trim_media(
        input_path=input_path,
        output_path=output_path,
        start=start,
        end=end,
        duration=duration,
        reencode=reencode,
    )
    return f"Successfully trimmed to: {out}"


@mcp.tool()
def media_extract_audio(
    input_path: str,
    output_path: str,
    codec: str = "libmp3lame",
    bitrate: str = "192k",
) -> str:
    """
    Extract the audio track from a video into a standalone audio file (提取音频).

    Args:
        input_path: Input video/media path.
        output_path: Output audio path (e.g. out.mp3 / out.wav).
        codec: Audio codec (default libmp3lame for mp3; use pcm_s16le for wav).
        bitrate: Audio bitrate (default 192k).
    """
    out = ffmpeg_ops.extract_audio(
        input_path=input_path, output_path=output_path, codec=codec, bitrate=bitrate
    )
    return f"Successfully extracted audio to: {out}"


@mcp.tool()
def media_extract_frames(
    input_path: str,
    output_dir: str,
    fps: Optional[float] = None,
    at_time: Optional[float] = None,
    pattern: str = "frame_%04d.jpg",
    quality: int = 2,
) -> str:
    """
    Extract frames from a video (提取画面/截图).

    Args:
        input_path: Input video path.
        output_dir: Directory to write frames into.
        fps: Frames per second to sample (e.g. 1 = one frame every second).
        at_time: Alternatively grab a single frame at a specific time (seconds).
        pattern: Output filename pattern (default frame_%04d.jpg).
        quality: JPEG quality 1-31 (lower = better, default 2).
    """
    out = ffmpeg_ops.extract_frames(
        input_path=input_path,
        output_dir=output_dir,
        fps=fps,
        at_time=at_time,
        pattern=pattern,
        quality=quality,
    )
    return f"Successfully extracted frames to: {out}"


@mcp.tool()
def media_mux_audio(
    video_path: str,
    audio_path: str,
    output_path: str,
    video_copy: bool = True,
) -> str:
    """
    Mux a (new) audio track onto a video, replacing its original audio (配音合成到视频).

    Args:
        video_path: Input video path.
        audio_path: Input audio path (e.g. a TTS voiceover).
        output_path: Output video path.
        video_copy: Keep original video stream without re-encoding (default True).
    """
    out = ffmpeg_ops.mux_audio(
        video_path=video_path,
        audio_path=audio_path,
        output_path=output_path,
        video_copy=video_copy,
    )
    return f"Successfully muxed audio into: {out}"


def main():
    mcp.run()


if __name__ == "__main__":
    main()
