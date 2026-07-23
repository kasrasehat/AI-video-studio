#!/usr/bin/env python3
"""combine_clip_versions.py — splice two attempts of the same clip together.

Stage-9 pattern: when the Director likes different parts of two regen attempts of the
same clip (e.g. attempt 1's opening, attempt 2's remainder), this cuts both at a chosen
point and joins them into one deliverable clip.

Two cut modes:
  --cut SECONDS         Exact cutpoint: clip_a supplies 0..SECONDS, clip_b supplies SECONDS..end.
  --window START END    Auto-match mode: search this time window in BOTH clips for the pair of
                         frames that look most alike (lowest pixel difference), and cut each clip
                         at its own best-matching frame. Use this when you know roughly where the
                         two attempts line up (e.g. "7 to 8 seconds") but want the seam landed on
                         the closest visual match inside that range rather than a fixed timestamp
                         (the two clips are separate generations and drift slightly in pacing, so
                         their most-similar frames are rarely at the exact same timestamp).

Either way, both trims are re-encoded (arbitrary-timestamp `-c copy` trims land on the nearest
keyframe, not the exact cut point, and can glitch) then concatenated with a fast stream copy.
ffmpeg/ffprobe must be on PATH (see skills/tech/ffmpeg, skills/tech/video-edit).

Usage:
  python scripts/combine_clip_versions.py <clip_a> <clip_b> <output> --cut SECONDS
  python scripts/combine_clip_versions.py <clip_a> <clip_b> <output> --window START END

Examples:
  # Exact cut: attempt 1 for 0-7s, attempt 2 for 7s-end
  python scripts/combine_clip_versions.py \\
    projects/micro-explorers/assets/clips/S02_C01.mp4 \\
    projects/micro-explorers/assets/clips/S02_C01_attempt2.mp4 \\
    projects/micro-explorers/assets/clips/S02_C01_combined.mp4 \\
    --cut 7

  # Auto-match: "7 to 8 seconds from V1, the rest from V2" - find the closest-matching
  # frame pair inside 7-8s and cut there instead of at a fixed timestamp
  python scripts/combine_clip_versions.py \\
    projects/micro-explorers/assets/clips/S02_C01.mp4 \\
    projects/micro-explorers/assets/clips/S02_C01_attempt2.mp4 \\
    projects/micro-explorers/assets/clips/S02_C01_combined.mp4 \\
    --window 7 8
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def probe_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(json.loads(r.stdout)["format"]["duration"])


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def extract_thumb_frames(clip: Path, start: float, end: float, sample_fps: float,
                          thumb_w: int, thumb_h: int) -> list[tuple[float, bytes]]:
    """Decode [start, end) of `clip` as small raw RGB frames for cheap comparison.

    Returns a list of (timestamp_seconds, raw_rgb24_bytes), sampled at sample_fps.
    """
    frame_size = thumb_w * thumb_h * 3
    cmd = [
        "ffmpeg", "-v", "error", "-i", str(clip), "-ss", str(start), "-to", str(end),
        "-vf", f"fps={sample_fps},scale={thumb_w}:{thumb_h}:flags=fast_bilinear",
        "-pix_fmt", "rgb24", "-f", "rawvideo", "-",
    ]
    print("+", " ".join(cmd))
    proc = subprocess.run(cmd, capture_output=True, check=True)
    raw = proc.stdout
    n_frames = len(raw) // frame_size
    frames = []
    for i in range(n_frames):
        chunk = raw[i * frame_size:(i + 1) * frame_size]
        ts = start + i / sample_fps
        frames.append((ts, chunk))
    return frames


def frame_diff(a: bytes, b: bytes) -> float:
    """Mean absolute per-byte difference between two equal-length raw RGB buffers."""
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


def find_best_match(clip_a: Path, clip_b: Path, start: float, end: float,
                     sample_fps: float, thumb_w: int, thumb_h: int) -> tuple[float, float, float]:
    """Search [start, end) in both clips for the closest-matching frame pair.

    Returns (ta, tb, score) - the timestamps in clip_a and clip_b whose frames are most
    alike, and their mean-absolute-difference score (lower = more similar, 0 = identical).
    """
    frames_a = extract_thumb_frames(clip_a, start, end, sample_fps, thumb_w, thumb_h)
    frames_b = extract_thumb_frames(clip_b, start, end, sample_fps, thumb_w, thumb_h)
    if not frames_a or not frames_b:
        raise RuntimeError(f"No frames extracted in window [{start}, {end}) - "
                            f"check the window falls inside both clips' durations")

    best = (frames_a[0][0], frames_b[0][0], float("inf"))
    for ta, fa in frames_a:
        for tb, fb in frames_b:
            score = frame_diff(fa, fb)
            if score < best[2]:
                best = (ta, tb, score)
    return best


def splice(clip_a: Path, clip_b: Path, ta: float, tb: float, out: Path, crf: int,
           audio_crossfade: float) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        seg_a = tmp / "seg_a.mp4"
        seg_b = tmp / "seg_b.mp4"
        list_txt = tmp / "list.txt"

        run([
            "ffmpeg", "-y", "-i", str(clip_a), "-to", str(ta),
            "-c:v", "libx264", "-crf", str(crf), "-preset", "medium",
            "-c:a", "aac", "-b:a", "192k",
            str(seg_a),
        ])
        run([
            "ffmpeg", "-y", "-ss", str(tb), "-i", str(clip_b),
            "-c:v", "libx264", "-crf", str(crf), "-preset", "medium",
            "-c:a", "aac", "-b:a", "192k",
            str(seg_b),
        ])

        if audio_crossfade > 0:
            run([
                "ffmpeg", "-y", "-i", str(seg_a), "-i", str(seg_b),
                "-filter_complex",
                f"[0:v][1:v]concat=n=2:v=1:a=0[v];"
                f"[0:a][1:a]acrossfade=d={audio_crossfade}[a]",
                "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-crf", str(crf), "-preset", "medium",
                "-c:a", "aac", "-b:a", "192k",
                str(out),
            ])
        else:
            list_txt.write_text(f"file '{seg_a.as_posix()}'\nfile '{seg_b.as_posix()}'\n", encoding="utf-8")
            run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_txt), "-c", "copy", str(out)])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip_a", help="Source for the FIRST segment (0..cut)")
    ap.add_argument("clip_b", help="Source for the SECOND segment (cut..end)")
    ap.add_argument("output", help="Path for the combined output clip")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--cut", type=float, metavar="SECONDS",
                       help="Exact cutpoint: clip_a 0..SECONDS, clip_b SECONDS..end")
    mode.add_argument("--window", nargs=2, type=float, metavar=("START", "END"),
                       help="Search this window in both clips for the best-matching frame pair, "
                            "and cut each clip at its own match point instead of a fixed timestamp")
    ap.add_argument("--sample-fps", type=float, default=10.0,
                     help="Frames/sec to sample when searching --window (default 10)")
    ap.add_argument("--thumb-size", default="64x36", metavar="WxH",
                     help="Downscale size used for frame comparison, small=fast (default 64x36)")
    ap.add_argument("--crf", type=int, default=18, help="Re-encode quality for the two trims (default 18)")
    ap.add_argument("--audio-crossfade", type=float, default=0.0,
                     help="Seconds of audio crossfade at the cut (default 0 = hard cut)")
    args = ap.parse_args()

    clip_a, clip_b, out = Path(args.clip_a), Path(args.clip_b), Path(args.output)
    for p in (clip_a, clip_b):
        if not p.exists():
            print(f"[ERROR] not found: {p}", file=sys.stderr)
            return 1

    dur_a = probe_duration(clip_a)
    dur_b = probe_duration(clip_b)
    out.parent.mkdir(parents=True, exist_ok=True)

    if args.cut is not None:
        if not (0 < args.cut < dur_a):
            print(f"[ERROR] --cut ({args.cut}) must be within clip_a's duration (0, {dur_a:.2f})", file=sys.stderr)
            return 1
        if args.cut >= dur_b:
            print(f"[ERROR] --cut ({args.cut}) must be less than clip_b's duration ({dur_b:.2f})", file=sys.stderr)
            return 1
        ta = tb = args.cut
        print(f"[fixed cut] clip_a 0-{ta}s + clip_b {tb}s-end")
    else:
        start, end = args.window
        if not (0 <= start < end):
            print(f"[ERROR] --window start ({start}) must be < end ({end})", file=sys.stderr)
            return 1
        if end > dur_a or end > dur_b:
            print(f"[ERROR] --window end ({end}) exceeds a clip's duration "
                  f"(clip_a={dur_a:.2f}, clip_b={dur_b:.2f})", file=sys.stderr)
            return 1
        thumb_w, thumb_h = (int(x) for x in args.thumb_size.lower().split("x"))
        ta, tb, score = find_best_match(clip_a, clip_b, start, end, args.sample_fps, thumb_w, thumb_h)
        print(f"[best match in {start}-{end}s] clip_a @ {ta:.3f}s <-> clip_b @ {tb:.3f}s "
              f"(mean abs diff {score:.2f}/255, lower=more similar)")

    splice(clip_a, clip_b, ta, tb, out, args.crf, args.audio_crossfade)

    final_dur = probe_duration(out)
    print(f"[OK] combined -> {out}  (segment A: 0-{ta:.3f}s from {clip_a.name}; "
          f"segment B: {tb:.3f}s-end from {clip_b.name}; total output {final_dur:.2f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
