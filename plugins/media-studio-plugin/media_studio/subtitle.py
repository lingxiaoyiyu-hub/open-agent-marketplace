"""Generate SRT subtitle files from plain text."""

import os
import re
from typing import List, Optional


_SENTENCE_END = re.compile(r"(?<=[。！？!?；;\n])")
_CLAUSE_END = re.compile(r"(?<=[，,、])")


def split_text(text: str, max_chars: int = 28) -> List[str]:
    """Split text into subtitle-sized chunks.

    Prefers sentence boundaries, then falls back to clause boundaries, then
    hard-splits very long tokens."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    sentences = [s for s in _SENTENCE_END.split(text) if s.strip()]
    chunks: List[str] = []
    for sent in sentences:
        if len(sent) <= max_chars:
            chunks.append(sent.strip())
            continue
        pieces = [p for p in _CLAUSE_END.split(sent) if p.strip()]
        buf = ""
        for p in pieces:
            if len(buf) + len(p) <= max_chars:
                buf += p
            else:
                if buf:
                    chunks.append(buf.strip())
                    buf = ""
                # Hard split if a single clause still exceeds the limit.
                while len(p) > max_chars:
                    chunks.append(p[:max_chars])
                    p = p[max_chars:]
                buf = p
        if buf:
            chunks.append(buf.strip())

    return [c for c in chunks if c]


def _ts(seconds: float) -> str:
    seconds = max(0.0, seconds)
    ms = int(round(seconds * 1000))
    h, rem = divmod(ms, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def make_srt(
    text: str,
    output_path: str,
    duration: Optional[float] = None,
    max_chars: int = 28,
    min_segment: float = 0.8,
) -> str:
    """Write an SRT file for ``text``.

    If ``duration`` is given (e.g. the media duration), segments are spread
    evenly across it. Otherwise each segment gets a rough length estimate."""
    segments = split_text(text, max_chars)
    if not segments:
        raise ValueError("No text to turn into subtitles.")

    if duration:
        per = max(min_segment, duration / len(segments))
    else:
        per = max(min_segment, 1.0)

    lines: List[str] = []
    start = 0.0
    for i, seg in enumerate(segments, start=1):
        end = start + per
        lines.append(str(i))
        lines.append(f"{_ts(start)} --> {_ts(end)}")
        lines.append(seg)
        lines.append("")
        start = end

    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return os.path.abspath(output_path)
