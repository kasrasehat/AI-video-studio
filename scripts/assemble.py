"""assemble.py — build the film from approved clips per edit_decisions.json (stage 10).

Usage:
  python scripts/assemble.py <slug> [--preset master] [--skip-audio] [--dry-run]

Reads:
  projects/<slug>/artifacts/edit_decisions.json   (the cut — schema edit_decisions)
  projects/<slug>/artifacts/generation_manifest.json  (clip_ref -> approved clip file)
  config/delivery_presets.yaml                    (per-preset encode settings)

Writes:
  projects/<slug>/renders/_work/                  (normalized mezzanine clips, mix stems)
  projects/<slug>/renders/<out_path per deliverable>
  projects/<slug>/artifacts/render_report.json    (archive-before-edit; final_qc.verdict
                                                   stays "fix" until the watch-through QC
                                                   passes and the EP updates it)

Pipeline per preset:
  1. Resolve timeline clip_refs to approved clip files (generation_manifest is authority).
  2. Normalize every clip to the preset's resolution/fps (pad, never distort; d-145: 720p
     sources are scaled locally), audio to 48k stereo.
  3. Join with transitions: cut/match_cut = concat; xfade/dip_black/wipe/iris_out via the
     ffmpeg xfade filter (iris_out = circleclose into black — the S17 ending).
  4. Mix audio: concatenated clip audio (dialogue — untouchable) + music beds (sidechain-
     ducked under clip audio when duck=true) + SFX one-shots; loudnorm to target_lufs.
  5. Captions: srt sidecar copied next to the output, or burned via subtitles filter.
  6. ffprobe-verify each output into render_report.json.

Vertical presets (aspect 9:16) render the 16:9 picture full-width over a blurred
fill of itself (no crop — framing was directed for 16:9).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import favs_lib as lib  # noqa: E402

FFMPEG = "ffmpeg"
FFPROBE = "ffprobe"

XFADE_MAP = {
    "xfade": "fade",
    "dip_black": "fadeblack",
    "wipe": "wipeleft",
    "iris_out": "circleclose",
}
DEFAULT_XFADE_S = 0.5


def run(cmd: list[str], dry: bool = False) -> None:
    print("  $", " ".join(str(c) for c in cmd[:8]) + (" ..." if len(cmd) > 8 else ""))
    if dry:
        return
    proc = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        tail = "\n".join((proc.stderr or "").splitlines()[-15:])
        raise RuntimeError(f"command failed ({proc.returncode}):\n{tail}")


def ffprobe_json(path: Path) -> dict:
    proc = subprocess.run(
        [FFPROBE, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        return {}
    return json.loads(proc.stdout or "{}")


def probe_duration(path: Path) -> float:
    info = ffprobe_json(path)
    return float(info.get("format", {}).get("duration", 0.0))


def resolve_clip_paths(project: Path, manifest: dict) -> dict[str, Path]:
    """clip_ref (e.g. S07_C01) -> absolute path of the APPROVED clip file."""
    out: dict[str, Path] = {}
    for entry in manifest.get("clips", []):
        if entry.get("status") != "approved":
            continue
        ref = entry.get("clip_id") or entry.get("clip_ref")
        rel = entry.get("file_path") or entry.get("local_path")
        if not ref or not rel:
            continue
        p = project / rel if not Path(rel).is_absolute() else Path(rel)
        out[ref] = p
    return out


def normalize_clip(src: Path, dst: Path, width: int, height: int, fps: int, trim_in: float | None,
                   trim_out: float | None, dry: bool) -> None:
    """Mezzanine: scale-to-fit + pad (never distort), constant fps, 48k stereo audio, near-lossless."""
    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}"
    )
    cmd = [FFMPEG, "-y", "-i", src]
    if trim_in:
        cmd += ["-ss", f"{trim_in}"]
    if trim_out:
        cmd += ["-to", f"{trim_out}"]
    cmd += ["-vf", vf, "-c:v", "libx264", "-crf", "12", "-preset", "fast", "-pix_fmt", "yuv420p",
            "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", dst.with_suffix(".mkv")]
    run(cmd, dry)


def join_timeline(mezz: list[dict], work: Path, fps: int, dry: bool) -> Path:
    """Join normalized clips honoring per-boundary transitions.

    mezz: [{path, duration, transition_out: {type, duration_s}}] in timeline order.
    Strategy: consecutive runs of hard cuts are concat'd (fast, exact); each non-cut
    boundary is an xfade between the accumulated left side and the next run.
    """
    def concat_run(paths: list[Path], out: Path) -> Path:
        if len(paths) == 1:
            return paths[0]
        lst = out.with_suffix(".txt")
        # ffmpeg concat demuxer wants forward slashes and quoted paths (Windows gotcha)
        lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in paths), encoding="utf-8", newline="\n")
        run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out], dry)
        return out

    # split into runs at non-cut boundaries
    runs: list[list[dict]] = [[]]
    fades: list[dict] = []
    for item in mezz:
        runs[-1].append(item)
        tr = item["transition_out"]
        if tr["type"] in XFADE_MAP and item is not mezz[-1]:
            fades.append(tr)
            runs.append([])
    # iris_out on the LAST clip fades into black after the film — handled post-join
    closing = mezz[-1]["transition_out"] if mezz[-1]["transition_out"]["type"] == "iris_out" else None

    left = concat_run([r["path"] for r in runs[0]], work / "run00.mkv")
    left_dur = sum(r["duration"] for r in runs[0])
    for i, (fade, seg) in enumerate(zip(fades, runs[1:]), start=1):
        right = concat_run([r["path"] for r in seg], work / f"run{i:02d}.mkv")
        right_dur = sum(r["duration"] for r in seg)
        d = float(fade.get("duration_s") or DEFAULT_XFADE_S)
        out = work / f"join{i:02d}.mkv"
        offset = max(left_dur - d, 0)
        fc = (
            f"[0:v]settb=AVTB[v0];[1:v]settb=AVTB[v1];"
            f"[v0][v1]xfade=transition={XFADE_MAP[fade['type']]}:duration={d}:offset={offset}[v];"
            f"[0:a][1:a]acrossfade=d={d}[a]"
        )
        run([FFMPEG, "-y", "-i", left, "-i", right, "-filter_complex", fc,
             "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "12", "-preset", "fast",
             "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", out], dry)
        left, left_dur = out, left_dur + right_dur - d

    if closing:
        d = float(closing.get("duration_s") or 1.0)
        hold = float(closing.get("hold_s") or 0.0)  # black tail after the close (audio button lives there)
        out = work / "closed.mkv"
        offset = max(left_dur - d, 0)
        # xfade inputs must share dimensions — generate the black tail at the cut's size
        info = ffprobe_json(left) if not dry else {}
        vs = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), {})
        w, h = vs.get("width", 1920), vs.get("height", 1080)
        fc = (
            f"color=c=black:s={w}x{h}:r={fps}:d={d + hold},settb=AVTB[blk];"
            f"[0:v]settb=AVTB[v0];"
            f"[v0][blk]xfade=transition=circleclose:duration={d}:offset={offset}[v];"
            f"[0:a]apad=pad_dur={hold}[a]"
        )
        run([FFMPEG, "-y", "-i", left, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
             "-c:v", "libx264", "-crf", "12", "-preset", "fast", "-pix_fmt", "yuv420p",
             "-c:a", "pcm_s16le", out], dry)
        left = out
    return left


def mix_audio(cut: Path, audio: dict, project: Path, work: Path, skip: bool, dry: bool) -> Path:
    """Overlay music beds (optionally sidechain-ducked under clip audio) and SFX; loudnorm."""
    target_lufs = audio.get("mix", {}).get("target_lufs", -14)
    music = [m for m in audio.get("music", []) if (project / m["path"]).exists() or dry] if not skip else []
    sfx = [s for s in audio.get("sfx", []) if (project / s["path"]).exists() or dry] if not skip else []
    skipped_m = [] if skip else [m["path"] for m in audio.get("music", []) if not ((project / m["path"]).exists() or dry)]
    if skipped_m:
        print(f"  [WARN] music files missing, skipped: {skipped_m}")

    out = work / "mixed.mkv"
    if not music and not sfx:
        run([FFMPEG, "-y", "-i", cut, "-c:v", "copy",
             "-af", f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11", "-c:a", "pcm_s16le", out], dry)
        return out

    cmd = [FFMPEG, "-y", "-i", cut]
    for m in music:
        cmd += ["-i", project / m["path"]]
    for s in sfx:
        cmd += ["-i", project / s["path"]]

    # The clip audio (dialogue) feeds the final mix AND keys each ducked music bed.
    parts, mix_inputs = [], []
    n_duckers = sum(1 for m in music if m.get("duck"))
    dlg_labels = [f"[dlg{i}]" for i in range(1 + n_duckers)]
    parts.append(f"[0:a]asplit={1 + n_duckers}" + "".join(dlg_labels))
    key_iter = iter(dlg_labels[1:])
    idx = 1
    for m in music:
        lbl = f"mus{idx}"
        delay = int(float(m["in_s"]) * 1000)
        parts.append(f"[{idx}:a]adelay={delay}|{delay},volume={m['gain_db']}dB[{lbl}pre]")
        if m.get("duck"):
            parts.append(f"[{lbl}pre]{next(key_iter)}"
                         f"sidechaincompress=threshold=0.05:ratio=8:attack=20:release=400[{lbl}]")
        else:
            parts.append(f"[{lbl}pre]anull[{lbl}]")
        mix_inputs.append(f"[{lbl}]")
        idx += 1
    for s in sfx:
        lbl = f"fx{idx}"
        delay = int(float(s["at_s"]) * 1000)
        parts.append(f"[{idx}:a]adelay={delay}|{delay},volume={s['gain_db']}dB[{lbl}]")
        mix_inputs.append(f"[{lbl}]")
        idx += 1
    parts.append(f"{dlg_labels[0]}{''.join(mix_inputs)}"
                 f"amix=inputs={1 + len(mix_inputs)}:duration=first:normalize=0,"
                 f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11[aout]")
    fc = ";".join(parts)
    cmd += ["-filter_complex", fc, "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "pcm_s16le", out]
    run(cmd, dry)
    return out


def render_deliverable(mixed: Path, preset: dict, out_path: Path, captions: dict,
                       srt_path: Path | None, dry: bool) -> None:
    w, h = preset["resolution"]
    fps = preset["fps"]
    vf_parts = []
    aspect_vertical = h > w
    if aspect_vertical:
        vf_parts.append(
            f"split[fg][bg];[bg]scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h},gblur=sigma=30[bgb];"
            f"[fg]scale={w}:-2[fgs];[bgb][fgs]overlay=(W-w)/2:(H-h)/2"
        )
    else:
        vf_parts.append(f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
                        f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2")
    if captions.get("mode") == "burn" and srt_path and (srt_path.exists() or dry):
        srt_escaped = str(srt_path).replace("\\", "/").replace(":", "\\:")
        vf_parts.append(f"subtitles='{srt_escaped}'")
    vf = ",".join(vf_parts)  # the vertical chain is one linear filtergraph (split..overlay), ',' continues it

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [FFMPEG, "-y", "-i", mixed]
    cmd += ["-filter_complex" if aspect_vertical else "-vf", vf]
    cmd += ["-r", str(fps), "-c:v", preset["video_codec"], "-crf", str(preset["crf"]),
            "-pix_fmt", preset["pixel_format"], "-c:a", preset["audio_codec"],
            "-b:a", preset["audio_bitrate"], "-movflags", "+faststart", out_path]
    run(cmd, dry)
    if captions.get("mode") == "srt" and srt_path and srt_path.exists():
        shutil.copy2(srt_path, out_path.with_suffix(".srt"))


def verify_output(path: Path, preset_id: str) -> dict:
    info = ffprobe_json(path)
    vs = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), {})
    a_ok = any(s.get("codec_type") == "audio" for s in info.get("streams", []))
    fps = 0.0
    if vs.get("avg_frame_rate") and vs["avg_frame_rate"] != "0/0":
        num, den = vs["avg_frame_rate"].split("/")
        fps = float(num) / float(den) if float(den) else 0.0
    return {
        "preset_id": preset_id,
        "path": str(path),
        "duration_s": float(info.get("format", {}).get("duration", 0) or 0),
        "resolution": f"{vs.get('width', 0)}x{vs.get('height', 0)}",
        "fps": round(fps, 3),
        "size_bytes": int(info.get("format", {}).get("size", 0) or 0),
        "ffprobe_ok": bool(vs) and a_ok and float(info.get("format", {}).get("duration", 0) or 0) > 0,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug")
    ap.add_argument("--preset", action="append", help="preset_id to render (repeatable); default: all in edit_decisions.deliverables")
    ap.add_argument("--skip-audio", action="store_true", help="skip music/SFX overlay (dialogue + loudnorm only)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    project = lib.ROOT / "projects" / args.slug
    ed = lib.read_json(project / "artifacts" / "edit_decisions.json")
    manifest = lib.read_json(project / "artifacts" / "generation_manifest.json")
    presets = yaml.safe_load((lib.ROOT / "config" / "delivery_presets.yaml").read_text(encoding="utf-8"))["presets"]

    errors = lib.validation_errors(ed, "edit_decisions")
    if errors:
        print("[ERROR] edit_decisions invalid:\n  " + "\n  ".join(errors))
        return 1

    clip_paths = resolve_clip_paths(project, manifest)
    work = project / "renders" / "_work"
    work.mkdir(parents=True, exist_ok=True)

    timeline = sorted(ed["timeline"], key=lambda t: t["order"])
    missing = [t["clip_ref"] for t in timeline if t["clip_ref"] not in clip_paths]
    if missing:
        print(f"[ERROR] timeline clip_refs not found as approved clips: {missing}")
        return 1

    wanted = args.preset or [d["preset_id"] for d in ed["deliverables"]]
    unknown = [p for p in wanted if p not in presets]
    if unknown:
        print(f"[ERROR] unknown presets {unknown}; known: {list(presets)}")
        return 1

    # Normalize + join ONCE at master quality (1920x1080@fps of first wanted preset)
    base_preset = presets[wanted[0]]
    bw, bh = (1920, 1080)
    fps = base_preset["fps"]
    print(f"[1/4] normalizing {len(timeline)} clips -> {bw}x{bh}@{fps}")
    mezz = []
    for t in timeline:
        src = clip_paths[t["clip_ref"]]
        dst = work / f"n_{t['order']:02d}_{t['clip_ref']}"
        normalize_clip(src, dst, bw, bh, fps, t.get("in_s"), t.get("out_s"), args.dry_run)
        mp = dst.with_suffix(".mkv")
        mezz.append({"path": mp, "duration": probe_duration(mp) if not args.dry_run else 10.0,
                     "transition_out": t["transition_out"]})

    print("[2/4] joining timeline with transitions")
    cut = join_timeline(mezz, work, fps, args.dry_run)

    print("[3/4] audio mix")
    mixed = mix_audio(cut, ed.get("audio", {}), project, work, args.skip_audio, args.dry_run)

    print("[4/4] rendering deliverables")
    srt = project / "renders" / "captions.srt"
    outputs = []
    for d in ed["deliverables"]:
        if d["preset_id"] not in wanted:
            continue
        out_path = project / d["out_path"]
        render_deliverable(mixed, presets[d["preset_id"]], out_path, ed.get("captions", {}),
                           srt if ed.get("captions", {}).get("mode") in ("burn", "srt") else None,
                           args.dry_run)
        if not args.dry_run:
            outputs.append(verify_output(out_path, d["preset_id"]))

    if args.dry_run:
        print("[DRY RUN] no render_report written")
        return 0

    report = {
        "version": "1.0",
        "project_id": args.slug,
        "outputs": outputs,
        "final_qc": {"verdict": "fix", "watch_through_findings": ["watch-through QC pending"]},
        "completed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    rr = project / "artifacts" / "render_report.json"
    if rr.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        shutil.copy2(rr, project / "history" / f"render_report_{stamp}.json")
    rr.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    errors = lib.validation_errors(report, "render_report")
    if errors:
        print("[ERROR] render_report invalid:\n  " + "\n  ".join(errors))
        return 1
    print(f"[OK] {len(outputs)} deliverable(s) rendered and verified; render_report written "
          f"(final_qc pending watch-through)")
    for o in outputs:
        print(f"  {o['preset_id']}: {o['resolution']} {o['duration_s']:.1f}s "
              f"{'OK' if o['ffprobe_ok'] else 'FFPROBE FAIL'} -> {o['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
