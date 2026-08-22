#!/usr/bin/env python3
"""extract_last_frame.py — pull the true final frame of a clip as a PNG.

Stage-9 chaining tool (Director order d-112): scene N+1's `start_image` is the LAST
frame of scene N's approved clip, so cuts land on pixel-continuous state. This script
is the reusable extractor — no per-scene ad-hoc ffmpeg.

Wraps system ffmpeg/ffprobe (no Pillow — same policy as storyboard_qc.py).

Usage:
  python scripts/extract_last_frame.py <clip.mp4> [-o out.png]

Default output: alongside the clip as `<clip_stem>_lastframe.png`.
Prints the output path on success — pipe it straight into media_upload.

Mechanics: seeks to 0.5s before end-of-file (`-sseof -0.5`) and keeps only the last
decoded frame (`-update 1`), which yields the genuine final frame rather than the
nearest keyframe. Falls back to decoding the whole tail if the container's seek fails.
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


def extract(clip: Path, out: Path, from_end: float = 0.0) -> bool:
    # [SEAM d-213] from_end > 0: grab the single frame at (duration - from_end) — the
    # overlap-generation start frame (sharp, mid-motion) instead of the final frame
    # (which is the most motion-blurred and most compressed frame of the clip).
    if from_end > 0:
        try:
            dur = float(probe(clip)["format"]["duration"])
        except Exception as e:
            print(f"[ERROR] ffprobe failed: {e}", file=sys.stderr)
            return False
        t = max(0.0, dur - from_end)
        r = subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(clip),
             "-frames:v", "1", "-q:v", "1", str(out)],
            capture_output=True, text=True,
        )
        return r.returncode == 0 and out.exists() and out.stat().st_size > 0
    # Primary: seek from end, write only the last frame.
    r = subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-sseof", "-0.5", "-i", str(clip),
         "-vsync", "0", "-update", "1", "-frames:v", "9999", "-q:v", "1", str(out)],
        capture_output=True, text=True,
    )
    if r.returncode == 0 and out.exists() and out.stat().st_size > 0:
        return True
    # Fallback: decode the tail via a duration-anchored seek.
    try:
        dur = float(probe(clip)["format"]["duration"])
    except Exception as e:
        print(f"[ERROR] ffprobe failed: {e}", file=sys.stderr)
        return False
    r = subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-ss", str(max(0.0, dur - 1.0)), "-i", str(clip),
         "-vsync", "0", "-update", "1", "-q:v", "1", str(out)],
        capture_output=True, text=True,
    )
    return r.returncode == 0 and out.exists() and out.stat().st_size > 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip", help="Video file to take the final frame from")
    ap.add_argument("-o", "--output", help="Output PNG path (default: <clip_stem>_lastframe.png beside the clip)")
    ap.add_argument("--from-end", type=float, default=0.0,
                    help="[SEAM d-213] Extract the frame this many seconds BEFORE the end instead of the final frame (overlap-generation start frame; e.g. 3.5)")
    args = ap.parse_args()

    clip = Path(args.clip)
    if not clip.exists():
        print(f"[ERROR] not found: {clip}", file=sys.stderr)
        return 1
    if args.from_end > 0:
        default_name = f"{clip.stem}_overlapstart_{args.from_end:g}s.png"
    else:
        default_name = f"{clip.stem}_lastframe.png"
    out = Path(args.output) if args.output else clip.with_name(default_name)
    out.parent.mkdir(parents=True, exist_ok=True)

    if not extract(clip, out, from_end=args.from_end):
        print(f"[ERROR] could not extract a final frame from {clip}", file=sys.stderr)
        return 1

    info = probe(clip)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    print(f"[OK] last frame -> {out}  (source: {clip.name}, {info['format']['duration']}s, {v['width']}x{v['height']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
