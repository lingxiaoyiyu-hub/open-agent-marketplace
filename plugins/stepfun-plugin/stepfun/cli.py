import sys
import json
import argparse
from .tts import synthesize_speech
from .voice_clone import preview_voice, create_voice
from .image import generate_image, edit_image
from .video import understand_video

def main():
    parser = argparse.ArgumentParser(prog="stepfun", description="StepFun (阶跃星辰) Audio/Image/Video CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # 1. TTS
    tts_parser = subparsers.add_parser("tts", help="Synthesize text to speech (TTS)")
    tts_parser.add_argument("--input", "-i", required=True, help="Input text to synthesize (auto-chunks if long)")
    tts_parser.add_argument("--output", "-o", default="speech.mp3", help="Output audio file path (default: speech.mp3)")
    tts_parser.add_argument("--voice", "-v", default="cixingnansheng", help="Voice ID (default: cixingnansheng)")
    tts_parser.add_argument("--instruction", help="Global tone/speed instruction (stepaudio-2.5-tts only)")
    tts_parser.add_argument("--model", default="stepaudio-2.5-tts", help="TTS Model (default: stepaudio-2.5-tts)")
    tts_parser.add_argument("--format", default="mp3", help="Audio response format (mp3, wav, flac, opus, pcm)")

    # 2. Clone Preview
    clone_prev_parser = subparsers.add_parser("clone-preview", help="Preview cloned voice (does not register voice_id)")
    clone_prev_parser.add_argument("--audio", "-a", required=True, help="Path to reference audio file (5-10s mp3/wav)")
    clone_prev_parser.add_argument("--ref-text", "-r", required=True, help="Text spoken in reference audio")
    clone_prev_parser.add_argument("--sample-text", "-s", required=True, help="Sample text for synthesis preview (<50 chars)")
    clone_prev_parser.add_argument("--output", "-o", default="preview.wav", help="Output wav path (default: preview.wav)")
    clone_prev_parser.add_argument("--instruction", help="Global tone/speed instruction")
    clone_prev_parser.add_argument("--model", default="stepaudio-2.5-tts", help="TTS Model")

    # 3. Clone Voice (Create permanent)
    clone_voice_parser = subparsers.add_parser("clone-voice", help="Create permanent cloned voice ID")
    clone_voice_parser.add_argument("--audio", "-a", required=True, help="Path to reference audio file (5-10s mp3/wav)")
    clone_voice_parser.add_argument("--ref-text", "-r", required=True, help="Text spoken in reference audio")
    clone_voice_parser.add_argument("--model", default="stepaudio-2.5-tts", help="TTS Model")

    # 4. Image Generation
    img_gen_parser = subparsers.add_parser("image", help="Generate image from prompt (Text-to-Image)")
    img_gen_parser.add_argument("--prompt", "-p", required=True, help="Prompt text (max 512 chars)")
    img_gen_parser.add_argument("--output", "-o", default="generated.png", help="Output image file path (default: generated.png)")
    img_gen_parser.add_argument("--model", default="step-image-edit-2", help="Model (default: step-image-edit-2)")
    img_gen_parser.add_argument("--size", help="Image size (e.g. 1024x1024, 768x1360, 1360x768)")
    img_gen_parser.add_argument("--cfg-scale", type=float, default=1.0, help="CFG scale (default: 1.0)")
    img_gen_parser.add_argument("--steps", type=int, default=8, help="Generation steps (default: 8)")
    img_gen_parser.add_argument("--text-mode", action="store_true", help="Enable text mode for images with text")

    # 5. Image Edit
    img_edit_parser = subparsers.add_parser("image-edit", help="Edit an existing image with prompt")
    img_edit_parser.add_argument("--image", "-i", required=True, help="Input image file path")
    img_edit_parser.add_argument("--prompt", "-p", required=True, help="Editing prompt text")
    img_edit_parser.add_argument("--output", "-o", default="edited.png", help="Output image file path (default: edited.png)")
    img_edit_parser.add_argument("--model", default="step-image-edit-2", help="Model (default: step-image-edit-2)")
    img_edit_parser.add_argument("--size", help="Image size (e.g. 1024x1024)")
    img_edit_parser.add_argument("--cfg-scale", type=float, default=1.0, help="CFG scale (default: 1.0)")
    img_edit_parser.add_argument("--steps", type=int, default=8, help="Generation steps (default: 8)")
    img_edit_parser.add_argument("--text-mode", action="store_true", help="Enable text mode")

    # 6. Video Understand
    video_parser = subparsers.add_parser("video", help="Understand and analyze video content")
    video_parser.add_argument("--video", "-v", required=True, help="Video URL or local file path")
    video_parser.add_argument("--prompt", "-p", default="请概括这个视频的主要内容", help="Analysis prompt")
    video_parser.add_argument("--model", default="step-3.7-flash", help="Video understanding model")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "tts":
            print(f"Synthesizing speech...")
            out_file = synthesize_speech(
                text=args.input,
                output_path=args.output,
                voice=args.voice,
                instruction=args.instruction,
                model=args.model,
                response_format=args.format
            )
            print(f"Success! Saved to {out_file}")

        elif args.command == "clone-preview":
            print(f"Generating voice preview...")
            out_file = preview_voice(
                file_path=args.audio,
                ref_text=args.ref_text,
                sample_text=args.sample_text,
                output_path=args.output,
                instruction=args.instruction,
                model=args.model
            )
            print(f"Success! Preview saved to {out_file}")

        elif args.command == "clone-voice":
            print(f"Creating cloned voice...")
            res = create_voice(
                file_path=args.audio,
                ref_text=args.ref_text,
                model=args.model
            )
            print(f"Success! Result:")
            print(json.dumps(res, ensure_ascii=False, indent=2))

        elif args.command == "image":
            print(f"Generating image...")
            out_file = generate_image(
                prompt=args.prompt,
                output_path=args.output,
                model=args.model,
                size=args.size,
                cfg_scale=args.cfg_scale,
                steps=args.steps,
                text_mode=args.text_mode
            )
            print(f"Success! Image saved to {out_file}")

        elif args.command == "image-edit":
            print(f"Editing image...")
            out_file = edit_image(
                image_path=args.image,
                prompt=args.prompt,
                output_path=args.output,
                model=args.model,
                size=args.size,
                cfg_scale=args.cfg_scale,
                steps=args.steps,
                text_mode=args.text_mode
            )
            print(f"Success! Edited image saved to {out_file}")

        elif args.command == "video":
            print(f"Analyzing video content...")
            ans = understand_video(
                video_input=args.video,
                prompt=args.prompt,
                model=args.model
            )
            print("\nVideo Understanding Analysis Result:")
            print(ans)

    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
