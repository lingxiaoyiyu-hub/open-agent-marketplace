import os
import re
import tempfile
import subprocess
from typing import List, Optional
from .client import StudioClient
from .config import StudioConfig

CHUNK_LIMIT = 900  # Character limit per chunk for TTS API (max 1000 per doc)

def split_text_into_chunks(text: str, max_chars: int = CHUNK_LIMIT) -> List[str]:
    text = text.strip()
    if len(text) <= max_chars:
        return [text]
        
    # Split primary by sentence enders: 。！？；\n
    sentence_delimiters = r'(?<=[。！？；\n])'
    sentences = re.split(sentence_delimiters, text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if not sentence:
            continue
        if len(current_chunk) + len(sentence) <= max_chars:
            current_chunk += sentence
        else:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            # If a single sentence exceeds max_chars, split by commas
            if len(sentence) > max_chars:
                comma_sentences = re.split(r'(?<=[，,])', sentence)
                sub_chunk = ""
                for s in comma_sentences:
                    if len(sub_chunk) + len(s) <= max_chars:
                        sub_chunk += s
                    else:
                        if sub_chunk:
                            chunks.append(sub_chunk)
                        sub_chunk = s
                if sub_chunk:
                    current_chunk = sub_chunk
            else:
                current_chunk = sentence
                
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

def merge_audio_files(input_files: List[str], output_file: str):
    if len(input_files) == 1:
        # Just copy/rename
        with open(input_files[0], "rb") as f_in, open(output_file, "wb") as f_out:
            f_out.write(f_in.read())
        return

    # Use ffmpeg concat list
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as list_file:
        list_file_path = list_file.name
        for file_path in input_files:
            # Escape single quotes for ffmpeg
            escaped_path = file_path.replace("\\", "/").replace("'", "'\\''")
            list_file.write(f"file '{escaped_path}'\n")

    try:
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file_path,
            "-c", "copy",
            "-y",
            output_file
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            # Fallback to re-encoding if direct copy fails
            cmd_reencode = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", list_file_path,
                "-y",
                output_file
            ]
            res_re = subprocess.run(cmd_reencode, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res_re.returncode != 0:
                raise RuntimeError(f"FFmpeg audio merge failed: {res_re.stderr}")
    finally:
        if os.path.exists(list_file_path):
            try:
                os.remove(list_file_path)
            except Exception:
                pass

def _build_payload(
    text: str,
    model: str,
    voice: str,
    response_format: str,
    instruction: Optional[str],
    speed: Optional[float],
    volume: Optional[float],
    sample_rate: Optional[int],
    text_normalization: Optional[str],
) -> dict:
    payload = {
        "model": model,
        "input": text,
        "voice": voice,
        "response_format": response_format,
    }
    if instruction and model == "stepaudio-2.5-tts":
        payload["instruction"] = instruction
    if speed is not None:
        payload["speed"] = speed
    if volume is not None:
        payload["volume"] = volume
    if sample_rate is not None:
        payload["sample_rate"] = sample_rate
    if text_normalization is not None:
        payload["text_normalization"] = text_normalization
    return payload


def synthesize_speech(
    text: str,
    output_path: str = "output.mp3",
    voice: str = "cixingnansheng",
    instruction: Optional[str] = None,
    model: str = "stepaudio-2.5-tts",
    response_format: str = "mp3",
    speed: Optional[float] = None,
    volume: Optional[float] = None,
    sample_rate: Optional[int] = None,
    text_normalization: Optional[str] = None,
    config: Optional[StudioConfig] = None
) -> str:
    """
    Synthesize speech from text. Automatically splits long text into chunks and merges audio.

    Extra synthesis controls (speed, volume, sample_rate, text_normalization) map
    directly to the Studio TTS API. ``instruction`` is only honored by the
    ``stepaudio-2.5-tts`` model.
    """
    client = StudioClient(config)
    chunks = split_text_into_chunks(text)

    if len(chunks) == 1:
        payload = _build_payload(
            chunks[0], model, voice, response_format, instruction,
            speed, volume, sample_rate, text_normalization,
        )
        audio_bytes = client.post_json("/audio/speech", payload, raw_response=True)

        # Ensure target directory exists
        out_dir = os.path.dirname(os.path.abspath(output_path))
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        return os.path.abspath(output_path)

    # Multi-chunk processing
    temp_files = []
    try:
        for idx, chunk in enumerate(chunks):
            payload = _build_payload(
                chunk, model, voice, response_format, instruction,
                speed, volume, sample_rate, text_normalization,
            )
            audio_bytes = client.post_json("/audio/speech", payload, raw_response=True)

            tmp_fd, tmp_path = tempfile.mkstemp(suffix=f"_{idx}.{response_format}")
            os.close(tmp_fd)
            with open(tmp_path, "wb") as f:
                f.write(audio_bytes)
            temp_files.append(tmp_path)

        out_dir = os.path.dirname(os.path.abspath(output_path))
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        merge_audio_files(temp_files, output_path)
        return os.path.abspath(output_path)
    finally:
        for tmp_p in temp_files:
            if os.path.exists(tmp_p):
                try:
                    os.remove(tmp_p)
                except Exception:
                    pass
