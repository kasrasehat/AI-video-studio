#!/usr/bin/env python3
"""extract_last_seconds.py — trim the final N seconds of a clip to its own mp4.

Stage-9 chaining tool (Director order d-202, supersedes last-FRAME chaining d-112
for chained scenes): scene N+1's generation call attaches the LAST 3 SECONDS of
scene N's approved clip as a `video_references` entry, so the model inherits real
motion, lighting and state — not just a frozen frame. The start_image is the
scene's own promoted Soul-cinema keyframe (d-200/d-202).

Wraps system ffmpeg/ffprobe (no Pillow — same policy as extract_last_frame.py).
Re-encodes (h264/aac) for frame-accurate cuts — stream copy would snap to the
nearest keyframe and deliver the wrong duration.

Usage:
  python scripts/extract_last_seconds.py <clip.mp4> [-s 3.0] [-o out.mp4]

Default output: alongside the clip as `<clip_stem>_last3s.mp4`.
Prints the output path on success — pipe it straight into media_upload.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def probe(path: Path) -> dict:
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(path)],
        capture_output=True, text=True, check=True,
    )
    return json.loads(r.stdout)


def extract(clip: Path, out: Path, seconds: float) -> bool:
    try:
        dur = float(probe(clip)["format"]["duration"])
    except Exception as e:
        print(f"[ERROR] ffprobe failed: {e}", file=sys.stderr)
        return False
    start = max(0.0, dur - seconds)
    r = subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-ss", f"{start:.3f}", "-i", str(clip),
         "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", str(out)],
        capture_output=True, text=True,
    )
    return r.returncode == 0 and out.exists() and out.stat().st_size > 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip", help="Video file to take the final seconds from")
    ap.add_argument("-s", "--seconds", type=float, default=3.0, help="Tail length in seconds (default 3.0)")
    ap.add_argument("-o", "--output", help="Output mp4 path (default: <clip_stem>_last3s.mp4 beside the clip)")
    args = ap.parse_args()

    clip = Path(args.clip)
    if not clip.exists():
        print(f"[ERROR] not found: {clip}", file=sys.stderr)
        return 1
    label = f"last{args.seconds:g}s".replace(".", "p")
    out = Path(args.output) if args.output else clip.with_name(f"{clip.stem}_{label}.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)

    if not extract(clip, out, args.seconds):
        print(f"[ERROR] could not extract the final {args.seconds:g}s from {clip}", file=sys.stderr)
        return 1

    info = probe(out)
    print(f"[OK] last {args.seconds:g}s -> {out}  ({info['format']['duration']}s, from {clip.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
