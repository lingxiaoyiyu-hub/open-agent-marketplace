import sys
import json
import argparse
from . import ffmpeg_ops
from .asr import transcribe_audio
from .image import generate_image, edit_image
from .pipeline import auto_subtitle
from .subtitle import make_srt
from .tts import synthesize_speech
from .video import understand_video
from .voice_clone import preview_voice, create_voice, list_system_voices


def _add_common(p, *names):
    return p


def main():
    parser = argparse.ArgumentParser(
        prog="media-studio",
        description="Media Studio Audio/Image/Video/Media CLI Tool",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # 1. TTS
    tts = subparsers.add_parser("tts", help="Synthesize text to speech (TTS)")
    tts.add_argument("--input", "-i", required=True, help="Input text (auto-chunks if long)")
    tts.add_argument("--output", "-o", default="speech.mp3", help="Output audio path")
    tts.add_argument("--voice", "-v", default="cixingnansheng", help="Voice ID")
    tts.add_argument("--instruction", help="Tone/speed instruction (stepaudio-2.5-tts only)")
    tts.add_argument("--model", default="stepaudio-2.5-tts", help="TTS model")
    tts.add_argument("--format", default="mp3", help="Audio format (mp3/wav/flac/opus/pcm)")
    tts.add_argument("--speed", type=float, help="Speed 0.5~2.0")
    tts.add_argument("--volume", type=float, help="Volume 0.1~2.0")
    tts.add_argument("--sample-rate", type=int, help="Sample rate (8000..48000)")
    tts.add_argument("--text-normalization", help="standard | enhanced")

    # 2. Voices
    voices = subparsers.add_parser("voices", help="List official system voices")
    voices.add_argument("--model", default="step-tts-2", help="Voice list model")

    # 3. Clone preview / voice
    cp = subparsers.add_parser("clone-preview", help="Preview cloned voice (no permanent id)")
    cp.add_argument("--audio", "-a", required=True, help="Reference audio (5-10s mp3/wav)")
    cp.add_argument("--ref-text", "-r", required=True, help="Text spoken in reference audio")
    cp.add_argument("--sample-text", "-s", required=True, help="Sample text (<50 chars)")
    cp.add_argument("--output", "-o", default="preview.wav", help="Output wav path")
    cp.add_argument("--instruction", help="Tone/speed instruction")
    cp.add_argument("--model", default="stepaudio-2.5-tts", help="TTS model")

    cv = subparsers.add_parser("clone-voice", help="Create permanent cloned voice id")
    cv.add_argument("--audio", "-a", required=True, help="Reference audio (5-10s mp3/wav)")
    cv.add_argument("--ref-text", "-r", required=True, help="Text spoken in reference audio")
    cv.add_argument("--model", default="stepaudio-2.5-tts", help="TTS model")

    # 4. ASR
    asr = subparsers.add_parser("asr", help="Transcribe audio/video to text (ASR)")
    asr.add_argument("--input", "-i", required=True, help="Audio or video file path")
    asr.add_argument("--model", default="stepaudio-2.5-asr", help="ASR model")
    asr.add_argument("--hotwords", nargs="*", help="Optional hot words")

    # 5. SRT
    srt = subparsers.add_parser("srt", help="Turn text into an SRT subtitle file")
    srt.add_argument("--text", "-t", required=True, help="Subtitle text")
    srt.add_argument("--output", "-o", required=True, help="Output .srt path")
    srt.add_argument("--duration", type=float, help="Media duration to spread segments")
    srt.add_argument("--max-chars", type=int, default=28, help="Max chars per line")

    # 6. Auto subtitle
    auto_sub = subparsers.add_parser("auto-subtitle", help="Transcribe + SRT + burn (one-shot)")
    auto_sub.add_argument("--video", "-v", required=True, help="Input video path")
    auto_sub.add_argument("--output", "-o", required=True, help="Output video path")
    auto_sub.add_argument("--model", default="stepaudio-2.5-asr", help="ASR model")
    auto_sub.add_argument("--font-name", default="Microsoft YaHei", help="Subtitle font")
    auto_sub.add_argument("--font-size", type=int, default=24, help="Subtitle font size")

    # 7. Media (ffmpeg) tools
    mi = subparsers.add_parser("media-info", help="Probe media metadata")
    mi.add_argument("--input", "-i", required=True, help="Media file path")

    addsub = subparsers.add_parser("add-subtitle", help="Burn SRT into a video")
    addsub.add_argument("--video", "-v", required=True, help="Input video path")
    addsub.add_argument("--srt", "-s", required=True, help="Input .srt path")
    addsub.add_argument("--output", "-o", required=True, help="Output video path")
    addsub.add_argument("--font-name", default="Microsoft YaHei", help="Font family")
    addsub.add_argument("--font-size", type=int, default=24, help="Font size")
    addsub.add_argument("--primary-color", default="&H00FFFFFF", help="ASS colour")
    addsub.add_argument("--outline-color", default="&H00000000", help="ASS outline colour")
    addsub.add_argument("--outline", type=int, default=1, help="Outline width")

    mc = subparsers.add_parser("mixcut", help="Random mashup of multiple videos")
    mc.add_argument("--inputs", "-i", nargs="+", required=True, help="Input video files")
    mc.add_argument("--output", "-o", required=True, help="Output video path")
    mc.add_argument("--duration", "-d", type=float, required=True, help="Target duration (s)")
    mc.add_argument("--segment", type=float, default=4.0, help="Per-clip length (s)")
    mc.add_argument("--transition", action="store_true", help="Enable crossfade")
    mc.add_argument("--transition-duration", type=float, default=0.5)
    mc.add_argument("--width", type=int, default=1280)
    mc.add_argument("--height", type=int, default=720)
    mc.add_argument("--fps", type=int, default=30)
    mc.add_argument("--voiceover", help="Voiceover audio path")
    mc.add_argument("--bgm", help="Background music path")
    mc.add_argument("--bgm-volume", type=float, default=0.25)
    mc.add_argument("--subtitle", help="Optional .srt path to burn")

    rc = subparsers.add_parser("roughcut", help="Remove long silences (rough cut)")
    rc.add_argument("--input", "-i", required=True, help="Input video path")
    rc.add_argument("--output", "-o", required=True, help="Output video path")
    rc.add_argument("--threshold", default="-35dB", help="Silence threshold (dB)")
    rc.add_argument("--min-silence", type=float, default=0.4, help="Min silence (s)")

    conv = subparsers.add_parser("convert", help="Transcode / convert video")
    conv.add_argument("--input", "-i", required=True, help="Input media path")
    conv.add_argument("--output", "-o", required=True, help="Output media path")
    conv.add_argument("--vcodec", default="libx264")
    conv.add_argument("--crf", type=int, default=23)
    conv.add_argument("--preset", default="medium")
    conv.add_argument("--acodec", default="aac")
    conv.add_argument("--audio-bitrate", default="128k")
    conv.add_argument("--scale", help="e.g. 1280:720")
    conv.add_argument("--fps", type=float)

    merge = subparsers.add_parser("merge", help="Concatenate media files")
    merge.add_argument("--inputs", "-i", nargs="+", required=True, help="Input files")
    merge.add_argument("--output", "-o", required=True, help="Output path")
    merge.add_argument("--reencode", action="store_true", help="Re-encode instead of copy")

    trim = subparsers.add_parser("trim", help="Cut a segment out of media")
    trim.add_argument("--input", "-i", required=True)
    trim.add_argument("--output", "-o", required=True)
    trim.add_argument("--start", type=float, default=0.0)
    trim.add_argument("--end", type=float)
    trim.add_argument("--duration", type=float)
    trim.add_argument("--reencode", action="store_true")

    ea = subparsers.add_parser("extract-audio", help="Extract audio from video")
    ea.add_argument("--input", "-i", required=True)
    ea.add_argument("--output", "-o", required=True)
    ea.add_argument("--codec", default="libmp3lame")
    ea.add_argument("--bitrate", default="192k")

    ef = subparsers.add_parser("extract-frames", help="Extract frames from video")
    ef.add_argument("--input", "-i", required=True)
    ef.add_argument("--output-dir", "-o", required=True)
    ef.add_argument("--fps", type=float)
    ef.add_argument("--at-time", type=float)
    ef.add_argument("--pattern", default="frame_%04d.jpg")
    ef.add_argument("--quality", type=int, default=2)

    ma = subparsers.add_parser("mux-audio", help="Mux a new audio track onto a video")
    ma.add_argument("--video", "-v", required=True)
    ma.add_argument("--audio", "-a", required=True)
    ma.add_argument("--output", "-o", required=True)
    ma.add_argument("--no-video-copy", action="store_true", help="Re-encode video instead of copy")

    # 8. Image generation / edit
    img = subparsers.add_parser("image", help="Generate image from prompt")
    img.add_argument("--prompt", "-p", required=True)
    img.add_argument("--output", "-o", default="generated.png")
    img.add_argument("--model", default="step-image-edit-2")
    img.add_argument("--size", help="e.g. 1024x1024")
    img.add_argument("--cfg-scale", type=float, default=1.0)
    img.add_argument("--steps", type=int, default=8)
    img.add_argument("--text-mode", action="store_true")

    ie = subparsers.add_parser("image-edit", help="Edit an existing image")
    ie.add_argument("--image", "-i", required=True)
    ie.add_argument("--prompt", "-p", required=True)
    ie.add_argument("--output", "-o", default="edited.png")
    ie.add_argument("--model", default="step-image-edit-2")
    ie.add_argument("--size")
    ie.add_argument("--cfg-scale", type=float, default=1.0)
    ie.add_argument("--steps", type=int, default=8)
    ie.add_argument("--text-mode", action="store_true")

    # 9. Video understand
    vid = subparsers.add_parser("video", help="Understand/analyze video content")
    vid.add_argument("--video", "-v", required=True, help="Video URL or local path")
    vid.add_argument("--prompt", "-p", default="请概括这个视频的主要内容")
    vid.add_argument("--model", default="step-3.7-flash")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        c = args.command
        if c == "tts":
            print("Synthesizing speech...")
            out = synthesize_speech(
                text=args.input, output_path=args.output, voice=args.voice,
                instruction=args.instruction, model=args.model,
                response_format=args.format, speed=args.speed, volume=args.volume,
                sample_rate=args.sample_rate, text_normalization=args.text_normalization,
            )
            print(f"Success! Saved to {out}")

        elif c == "voices":
            print(json.dumps(list_system_voices(model=args.model), ensure_ascii=False, indent=2))

        elif c == "clone-preview":
            out = preview_voice(file_path=args.audio, ref_text=args.ref_text,
                                sample_text=args.sample_text, output_path=args.output,
                                instruction=args.instruction, model=args.model)
            print(f"Success! Preview saved to {out}")

        elif c == "clone-voice":
            res = create_voice(file_path=args.audio, ref_text=args.ref_text, model=args.model)
            print("Success! Result:")
            print(json.dumps(res, ensure_ascii=False, indent=2))

        elif c == "asr":
            print(transcribe_audio(file_path=args.input, model=args.model, hotwords=args.hotwords))

        elif c == "srt":
            out = make_srt(text=args.text, output_path=args.output,
                           duration=args.duration, max_chars=args.max_chars)
            print(f"Success! Saved to {out}")

        elif c == "auto-subtitle":
            res = auto_subtitle(video_path=args.video, output_path=args.output,
                                model=args.model, font_name=args.font_name,
                                font_size=args.font_size)
            print(f"Subtitle burned to: {res['output_path']}")
            print(f"Transcript: {res['text']}")

        elif c == "media-info":
            print(json.dumps(ffmpeg_ops.media_info(args.input), ensure_ascii=False, indent=2))

        elif c == "add-subtitle":
            out = ffmpeg_ops.add_subtitle(
                video_path=args.video, srt_path=args.srt, output_path=args.output,
                font_name=args.font_name, font_size=args.font_size,
                primary_color=args.primary_color, outline_color=args.outline_color,
                outline=args.outline,
            )
            print(f"Success! Saved to {out}")

        elif c == "mixcut":
            out = ffmpeg_ops.mixcut(
                inputs=args.inputs, output_path=args.output, duration=args.duration,
                segment=args.segment, transition=args.transition,
                transition_duration=args.transition_duration, width=args.width,
                height=args.height, fps=args.fps, voiceover=args.voiceover,
                bgm=args.bgm, bgm_volume=args.bgm_volume, subtitle=args.subtitle,
            )
            print(f"Success! Mashup saved to {out}")

        elif c == "roughcut":
            out = ffmpeg_ops.roughcut(input_path=args.input, output_path=args.output,
                                      threshold=args.threshold, min_silence=args.min_silence)
            print(f"Success! Saved to {out}")

        elif c == "convert":
            out = ffmpeg_ops.convert_video(
                input_path=args.input, output_path=args.output, vcodec=args.vcodec,
                crf=args.crf, preset=args.preset, acodec=args.acodec,
                audio_bitrate=args.audio_bitrate, scale=args.scale, fps=args.fps,
            )
            print(f"Success! Saved to {out}")

        elif c == "merge":
            out = ffmpeg_ops.merge_media(inputs=args.inputs, output_path=args.output,
                                         reencode=args.reencode)
            print(f"Success! Saved to {out}")

        elif c == "trim":
            out = ffmpeg_ops.trim_media(input_path=args.input, output_path=args.output,
                                        start=args.start, end=args.end,
                                        duration=args.duration, reencode=args.reencode)
            print(f"Success! Saved to {out}")

        elif c == "extract-audio":
            out = ffmpeg_ops.extract_audio(input_path=args.input, output_path=args.output,
                                           codec=args.codec, bitrate=args.bitrate)
            print(f"Success! Saved to {out}")

        elif c == "extract-frames":
            out = ffmpeg_ops.extract_frames(input_path=args.input, output_dir=args.output_dir,
                                            fps=args.fps, at_time=args.at_time,
                                            pattern=args.pattern, quality=args.quality)
            print(f"Success! Frames saved to {out}")

        elif c == "mux-audio":
            out = ffmpeg_ops.mux_audio(video_path=args.video, audio_path=args.audio,
                                       output_path=args.output,
                                       video_copy=not args.no_video_copy)
            print(f"Success! Saved to {out}")

        elif c == "image":
            out = generate_image(prompt=args.prompt, output_path=args.output, model=args.model,
                                 size=args.size, cfg_scale=args.cfg_scale, steps=args.steps,
                                 text_mode=args.text_mode)
            print(f"Success! Image saved to {out}")

        elif c == "image-edit":
            out = edit_image(image_path=args.image, prompt=args.prompt, output_path=args.output,
                             model=args.model, size=args.size, cfg_scale=args.cfg_scale,
                             steps=args.steps, text_mode=args.text_mode)
            print(f"Success! Edited image saved to {out}")

        elif c == "video":
            ans = understand_video(video_input=args.video, prompt=args.prompt, model=args.model)
            print("\nVideo Understanding Analysis Result:")
            print(ans)

    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
