#!/usr/bin/env python3
"""storyboard_qc.py — cheap, deterministic panel-level QC tooling for stage-8 grid storyboard pages.

Wraps system ffmpeg/ffprobe (no Pillow/PIL — keeps the repo venv dependency-free; ffmpeg is
already required by skills/tech/ffmpeg). Exists to stop storyboard-artist subagents from
hand-computing crop pixel math in ad-hoc Bash on every scene (expensive, error-prone, and the
coordinates are silently different from what the grid method actually laid out).

See skills/tech/storyboard-qc/SKILL.md for the QC procedure this tool supports — that skill
is the read-first entry point; this file is the mechanical backend for it.

Commands:
  split-panels  Crop a grid storyboard page into individual numbered panel PNGs + manifest.json
  diff          Build a single A|B|diff triptych image for camera-lock / continuity comparison
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def ffprobe_dims(path: Path) -> tuple[int, int]:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    w, h = out.stdout.strip().split(",")
    return int(w), int(h)


def cell_edges(total: int, n: int) -> list[int]:
    """Evenly split [0, total) into n integer boundaries — no rounding drift on later cells."""
    return [round(i * total / n) for i in range(n + 1)]


def cmd_split(args: argparse.Namespace) -> None:
    img = Path(args.image)
    if not img.exists():
        sys.exit(f"[ERROR] not found: {img}")
    rows, cols = args.rows, args.cols
    w, h = ffprobe_dims(img)
    xs = cell_edges(w, cols)
    ys = cell_edges(h, rows)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"source": str(img), "width": w, "height": h, "rows": rows, "cols": cols, "panels": []}
    n = 1
    for r in range(rows):
        for c in range(cols):
            x0, x1 = xs[c], xs[c + 1]
            y0, y1 = ys[r], ys[r + 1]
            pw, ph = x1 - x0, y1 - y0
            out_path = out_dir / f"{args.prefix}_{n:02d}.png"
            subprocess.run(
                ["ffmpeg", "-loglevel", "error", "-y", "-i", str(img),
                 "-vf", f"crop={pw}:{ph}:{x0}:{y0}", str(out_path)],
                check=True,
            )
            manifest["panels"].append({"panel": n, "path": str(out_path), "x": x0, "y": y0, "w": pw, "h": ph})
            n += 1
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"[OK] {rows}x{cols} = {rows * cols} panels -> {out_dir}")
    print(f"[OK] manifest -> {manifest_path}")
    print("Read each panel_NN.png individually for the per-panel QC pass (smaller image, sharper detail than the full page).")


def cmd_diff(args: argparse.Namespace) -> None:
    a, b = Path(args.image_a), Path(args.image_b)
    for p in (a, b):
        if not p.exists():
            sys.exit(f"[ERROR] not found: {p}")
    wa, ha = ffprobe_dims(a)
    wb, hb = ffprobe_dims(b)
    if (wa, ha) != (wb, hb):
        print(f"[WARN] size mismatch A={wa}x{ha} B={wb}x{hb} — scaling B to A before diffing")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    filt = (
        f"[0:v]split=2[a1][a2];"
        f"[1:v]scale={wa}:{ha},split=2[b1][b2];"
        f"[a1][b1]blend=all_mode=difference[d];"
        f"[d]eq=contrast={args.amplify}:brightness=0.15[damp];"
        f"[a2][b2][damp]hstack=inputs=3[out]"
    )
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-y", "-i", str(a), "-i", str(b),
         "-filter_complex", filt, "-map", "[out]", str(out)],
        check=True,
    )
    print(f"[OK] triptych (A | B | amplified-diff) -> {out}")
    print("Read this ONE image. Bright/colored regions in the RIGHT panel = pixels that differ between A and B.")
    print("Camera-lock check: differences should be confined to characters/light state — never to walls, columns, or background scale/position.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("split-panels", help="Crop a grid storyboard page into individual numbered panel PNGs + manifest.json")
    sp.add_argument("image")
    sp.add_argument("--rows", type=int, required=True)
    sp.add_argument("--cols", type=int, required=True)
    sp.add_argument("--out-dir", required=True)
    sp.add_argument("--prefix", default="panel")
    sp.set_defaults(func=cmd_split)

    dp = sub.add_parser("diff", help="Build a single A|B|diff triptych for camera-lock / continuity comparison between two panel crops")
    dp.add_argument("image_a")
    dp.add_argument("image_b")
    dp.add_argument("--out", required=True)
    dp.add_argument("--amplify", type=float, default=3.0, help="contrast multiplier on the diff channel (default 3.0)")
    dp.set_defaults(func=cmd_diff)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
