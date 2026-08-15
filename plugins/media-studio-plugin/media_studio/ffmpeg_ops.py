"""Local media editing built on ffmpeg / ffprobe.

This module replaces the closed-source ``nxImage.exe``/``ffmpeg`` pipeline that the
"逆象" desktop app relied on: subtitle burning, mashup (mixcut), rough cut,
transcoding, merging, audio extraction, frame extraction and media probing.

Everything here shells out to the open-source ffmpeg/ffprobe binaries. The
binaries are resolved from the ``FFMPEG_PATH`` / ``FFPROBE_PATH`` environment
variables, falling back to ``ffmpeg`` / ``ffprobe`` on PATH.
"""

import json
import os
import random
import subprocess
import tempfile
from typing import List, Optional


def _ffmpeg() -> str:
    return os.environ.get("FFMPEG_PATH") or "ffmpeg"


def _ffprobe() -> str:
    if os.environ.get("FFPROBE_PATH"):
        return os.environ["FFPROBE_PATH"]
    ff = _ffmpeg()
    if ff != "ffmpeg":
        return ff.replace("ffmpeg", "ffprobe")
    return "ffprobe"


def _run(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if check and res.returncode != 0:
        raise RuntimeError(
            "Command failed (%s): %s\n%s"
            % (res.returncode, " ".join(cmd), res.stderr[-2000:])
        )
    return res


def _exists(path: str) -> str:
    if not path or not os.path.exists(path):
        raise FileNotFoundError(f"Path not found: {path}")
    return os.path.abspath(path)


def media_info(path: str) -> dict:
    """Return a JSON dict describing a media file (streams + format)."""
    _exists(path)
    res = _run(
        [
            _ffprobe(),
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            path,
        ]
    )
    return json.loads(res.stdout)


def probe_duration(path: str) -> float:
    """Return the media duration in seconds."""
    info = media_info(path)
    fmt_dur = (info.get("format") or {}).get("duration")
    if fmt_dur is not None:
        try:
            return float(fmt_dur)
        except (TypeError, ValueError):
            pass
    # Fallback: longest stream duration.
    best = 0.0
    for s in info.get("streams", []):
        d = s.get("duration")
        if d is not None:
            try:
                best = max(best, float(d))
            except (TypeError, ValueError):
                pass
    if best <= 0:
        raise RuntimeError(f"Could not determine duration for: {path}")
    return best


def _has_video(path: str) -> bool:
    info = media_info(path)
    return any(s.get("codec_type") == "video" for s in info.get("streams", []))


def _has_audio(path: str) -> bool:
    info = media_info(path)
    return any(s.get("codec_type") == "audio" for s in info.get("streams", []))


def convert_video(
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
    """Transcode / convert a video to another format, size or frame rate."""
    _exists(input_path)
    cmd = [_ffmpeg(), "-y", "-i", input_path]
    if scale:
        cmd += ["-vf", f"scale={scale}"]
    cmd += ["-c:v", vcodec, "-crf", str(crf), "-preset", preset,
            "-c:a", acodec, "-b:a", audio_bitrate]
    if fps:
        cmd += ["-r", str(fps)]
    cmd += [output_path]
    _run(cmd)
    return os.path.abspath(output_path)


def merge_media(inputs: List[str], output_path: str, reencode: bool = False) -> str:
    """Concatenate multiple media files into one (same codec by default)."""
    if not inputs:
        raise ValueError("At least one input file is required.")
    for p in inputs:
        _exists(p)
    list_path = None
    with tempfile.NamedTemporaryFile(
        "w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        list_path = f.name
        for p in inputs:
            escaped = os.path.abspath(p).replace("'", "'\\''")
            f.write(f"file '{escaped}'\n")
    try:
        cmd = [_ffmpeg(), "-y", "-f", "concat", "-safe", "0", "-i", list_path]
        if reencode:
            cmd += ["-c:v", "libx264", "-crf", "23", "-preset", "medium",
                    "-c:a", "aac"]
        else:
            cmd += ["-c", "copy"]
        cmd += [output_path]
        _run(cmd)
    finally:
        os.remove(list_path)
    return os.path.abspath(output_path)


def trim_media(
    input_path: str,
    output_path: str,
    start: float = 0.0,
    end: Optional[float] = None,
    duration: Optional[float] = None,
    reencode: bool = False,
) -> str:
    """Cut a segment out of a media file."""
    _exists(input_path)
    cmd = [_ffmpeg(), "-y"]
    if start:
        cmd += ["-ss", str(start)]
    if end is not None:
        cmd += ["-to", str(end)]
    elif duration is not None:
        cmd += ["-t", str(duration)]
    cmd += ["-i", input_path]
    if reencode:
        cmd += ["-c:v", "libx264", "-crf", "23", "-preset", "medium", "-c:a", "aac"]
    else:
        cmd += ["-c", "copy"]
    cmd += [output_path]
    _run(cmd)
    return os.path.abspath(output_path)


def extract_audio(
    input_path: str,
    output_path: str,
    codec: str = "libmp3lame",
    bitrate: str = "192k",
) -> str:
    """Extract the audio track into a standalone audio file."""
    _exists(input_path)
    cmd = [_ffmpeg(), "-y", "-i", input_path, "-vn", "-acodec", codec,
           "-b:a", bitrate, output_path]
    _run(cmd)
    return os.path.abspath(output_path)


def extract_frames(
    input_path: str,
    output_dir: str,
    fps: Optional[float] = None,
    at_time: Optional[float] = None,
    pattern: str = "frame_%04d.jpg",
    quality: int = 2,
) -> str:
    """Extract frames from a video: one frame at a time, or every ``fps``."""
    _exists(input_path)
    os.makedirs(output_dir, exist_ok=True)
    cmd = [_ffmpeg(), "-y", "-i", input_path]
    if at_time is not None:
        cmd += ["-ss", str(at_time), "-frames:v", "1", "-q:v", str(quality)]
    elif fps:
        cmd += ["-vf", f"fps={fps}", "-q:v", str(quality)]
    else:
        cmd += ["-frames:v", "1", "-q:v", str(quality)]
    cmd += [os.path.join(output_dir, pattern)]
    _run(cmd)
    return os.path.abspath(output_dir)


def _safe_srt_path(srt: str):
    """Copy an SRT to a temp file with an ASCII-safe name and return both the
    real temp path and an ffmpeg-escaped path. Avoids the classic Windows
    ``subtitles=`` path-escaping pitfalls (spaces, colons, CJK characters)."""
    tmp = tempfile.NamedTemporaryFile("w", suffix=".srt", delete=False, encoding="utf-8")
    with open(srt, "r", encoding="utf-8") as src:
        tmp.write(src.read())
    tmp.close()
    escaped = tmp.name.replace("\\", "/").replace(":", "\\:")
    return tmp.name, escaped


def add_subtitle(
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
    """Burn an SRT subtitle file into a video."""
    _exists(video_path)
    _exists(srt_path)
    tmp_srt, escaped = _safe_srt_path(srt_path)
    style = (
        f"FontName={font_name},FontSize={font_size},"
        f"PrimaryColour={primary_color},OutlineColour={outline_color},Outline={outline},"
        f"WrapStyle=0"
    )
    if alignment is not None:
        style += f",Alignment={alignment}"
    try:
        vf = f"subtitles='{escaped}':force_style='{style}'"
        cmd = [_ffmpeg(), "-y", "-i", video_path, "-vf", vf,
               "-c:a", "copy",
               "-c:v", "libx264", "-crf", "18", "-preset", "medium",
               output_path]
        _run(cmd)
    finally:
        if os.path.exists(tmp_srt):
            os.remove(tmp_srt)
    return os.path.abspath(output_path)


def roughcut(
    input_path: str,
    output_path: str,
    threshold: str = "-35dB",
    min_silence: float = 0.4,
) -> str:
    """Remove long silences from a talking-head video (rough cut).

    This handles pauses/blank audio; removing filler words (口癖) requires the
    caller to first transcribe, locate filler segments, then call ``trim_media``
    or ``merge_media`` on the kept segments.
    """
    _exists(input_path)
    af = f"silenceremove=stop_periods=-1:stop_duration={min_silence}:stop_threshold={threshold}"
    cmd = [_ffmpeg(), "-y", "-i", input_path, "-af", af,
           "-c:v", "copy", "-c:a", "aac", output_path]
    _run(cmd)
    return os.path.abspath(output_path)


def mux_audio(
    video_path: str,
    audio_path: str,
    output_path: str,
    video_copy: bool = True,
) -> str:
    """Mux a (new) audio track onto a video, replacing its original audio."""
    _exists(video_path)
    _exists(audio_path)
    cmd = [_ffmpeg(), "-y", "-i", video_path, "-i", audio_path,
           "-map", "0:v:0", "-map", "1:a:0",
           "-c:a", "aac", "-b:a", "192k", "-shortest"]
    if video_copy:
        cmd += ["-c:v", "copy"]
    cmd += [output_path]
    _run(cmd)
    return os.path.abspath(output_path)


def mixcut(
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
    """Randomly trim & concatenate multiple video clips into one target-length
    video. Optionally add transitions, a voiceover, background music and a
    burned-in subtitle track."""
    if not inputs:
        raise ValueError("At least one input video is required.")
    for p in inputs:
        _exists(p)
        if not _has_video(p):
            raise ValueError(f"Input has no video stream: {p}")

    if not voiceover:
        for p in inputs:
            if not _has_audio(p):
                raise ValueError(
                    f"Input has no audio stream: {p}. "
                    "Provide a voiceover audio file, or use inputs with audio."
                )

    src_durs = [probe_duration(p) for p in inputs]
    # Build random segments (round-robin over inputs).
    segs: List[tuple] = []  # (input_index, start, length)
    total = 0.0
    i = 0
    guard = 0
    while total < duration and guard < 2000:
        idx = i % len(inputs)
        src = src_durs[idx]
        seg_len = min(segment, src - 0.5)
        if seg_len < 0.5:
            i += 1
            guard += 1
            continue
        start = random.uniform(0.0, max(0.0, src - seg_len))
        segs.append((idx, start, seg_len))
        total += seg_len
        i += 1
        guard += 1
    if not segs:
        raise RuntimeError("Could not build any segments from the given inputs.")

    n = len(segs)
    video_labels = []
    audio_labels = []

    fc_parts: List[str] = []
    for k, (idx, start, seg_len) in enumerate(segs):
        fc_parts.append(
            f"[{idx}:v]trim=start={start:.3f}:duration={seg_len:.3f},"
            f"setpts=PTS-STARTPTS,"
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}[v{k}]"
        )
        video_labels.append(f"[v{k}]")
        fc_parts.append(
            f"[{idx}:a]atrim=start={start:.3f}:duration={seg_len:.3f},"
            f"asetpts=PTS-STARTPTS[a{k}]"
        )
        audio_labels.append(f"[a{k}]")

    # Video chain.
    if transition and n >= 2:
        # xfade chain with correctly accumulating offsets.
        prev = f"[v0]"
        fc_parts.append(
            f"[v0][v1]xfade=transition=fade:duration={transition_duration}:"
            f"offset={segs[0][2] - transition_duration:.3f}[x0]"
        )
        prev = "[x0]"
        for k in range(2, n):
            offset = sum(s[2] for s in segs[:k]) - k * transition_duration
            fc_parts.append(
                f"{prev}[v{k}]xfade=transition=fade:duration={transition_duration}:"
                f"offset={offset:.3f}[x{k-1}]"
            )
            prev = f"[x{k-1}]"
        video_out_label = prev
    else:
        fc_parts.append(
            f"{''.join(video_labels)}concat=n={n}:v=1:a=0[vc]"
        )
        video_out_label = "[vc]"

    # Audio chain: voiceover replaces source audio, otherwise concat sources.
    if voiceover:
        _exists(voiceover)
        vi = len(inputs)
        fc_parts.append(f"[{vi}:a]atrim=0:{total:.3f},asetpts=PTS-STARTPTS[aout]")
    else:
        fc_parts.append(f"{''.join(audio_labels)}concat=n={n}:v=0:a=1[aout]")

    # Optional BGM mixing.
    if bgm:
        _exists(bgm)
        bi = len(inputs) + (1 if voiceover else 0)
        fc_parts.append(
            f"[{bi}:a]atrim=0:{total:.3f},asetpts=PTS-STARTPTS,"
            f"volume={bgm_volume}[bg];"
            f"[aout][bg]amix=inputs=2:duration=first:dropout_transition=0[afinal]"
        )
        audio_out_label = "[afinal]"
    else:
        audio_out_label = "[aout]"

    # Optional subtitle burn.
    if subtitle:
        _exists(subtitle)
        tmp_srt, escaped = _safe_srt_path(subtitle)
        fc_parts.append(f"{video_out_label}subtitles='{escaped}'[vfinal]")
        video_final = "[vfinal]"
    else:
        tmp_srt = None
        video_final = video_out_label

    filter_complex = ";".join(fc_parts)
    cmd = [_ffmpeg(), "-y"]
    for p in inputs:
        cmd += ["-i", p]
    if voiceover:
        cmd += ["-i", voiceover]
    if bgm:
        cmd += ["-i", bgm]
    cmd += ["-filter_complex", filter_complex,
            "-map", video_final, "-map", audio_out_label,
            "-t", f"{total:.3f}",
            "-c:v", "libx264", "-crf", "18", "-preset", "medium",
            "-c:a", "aac", "-b:a", "192k",
            output_path]
    try:
        _run(cmd)
    finally:
        if tmp_srt and os.path.exists(tmp_srt):
            os.remove(tmp_srt)
    return os.path.abspath(output_path)
