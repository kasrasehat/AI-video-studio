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


def load_seam_policy() -> dict:
    """[SEAM d-210] Kill-switch flags from config/seam_policy.yaml.

    Every seam-fix code path in this script is guarded `if SEAM.get(<flag>):`.
    A missing file or missing key reads as False = exact pre-change behavior,
    so deleting the config (or flipping a flag) is a complete kill-switch.
    """
    p = Path(__file__).resolve().parent.parent / "config" / "seam_policy.yaml"
    if not p.exists():
        return {}
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        return data.get("flags", {}) or {}
    except Exception as e:  # a broken policy file must never kill a render
        print(f"[WARN] seam_policy.yaml unreadable ({e}) - seam fixes disabled this run")
        return {}


SEAM = load_seam_policy()

# [SEAM d-216] 3 frames at 24fps — the minimum audio fade that kills a splice click.
AFADE_PAIR_S = 3.0 / 24.0

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
    """clip_ref (e.g. S07_C01) -> absolute path of the APPROVED clip file.

    output_path may be repo-root-relative ('projects/<slug>/...') or project-relative.
    If several approved entries share a clip_id, the last one whose file exists wins.
    """
    out: dict[str, Path] = {}
    for entry in manifest.get("clips", []):
        if entry.get("status") != "approved":
            continue
        ref = entry.get("clip_id") or entry.get("clip_ref")
        rel = entry.get("output_path") or entry.get("file_path") or entry.get("local_path")
        if not ref or not rel:
            continue
        rp = Path(rel)
        if rp.is_absolute():
            p = rp
        elif rel.replace("\\", "/").startswith("projects/"):
            p = lib.ROOT / rp
        else:
            p = project / rp
        if p.exists() or ref not in out:
            out[ref] = p
    return out


def normalize_clip(src: Path, dst: Path, width: int, height: int, fps: int, trim_in: float | None,
                   trim_out: float | None, dry: bool,
                   afade_head_s: float = 0.0, afade_tail_s: float = 0.0) -> None:
    """Mezzanine: scale-to-fit + pad (never distort), constant fps, 48k stereo audio, near-lossless.

    [SEAM d-214] flag color_pipeline: Seedance MP4s are UNTAGGED (color_range/space/
    transfer/primaries=unknown -> decoder-dependent exposure pops at joins). With the
    flag on, the scale filter converts explicitly and the encode TAGS bt709/tv so every
    downstream join reads identical color. Flag off = the exact pre-change command.
    [SEAM d-216] flag audio_crossfade: afade_head_s/afade_tail_s put a 3-frame audio
    fade at hard-cut boundary edges so no join is ever a hard splice.
    """
    if SEAM.get("color_pipeline"):
        vf = (
            f"scale={width}:{height}:force_original_aspect_ratio=decrease:"
            f"in_range=tv:out_range=tv:in_color_matrix=bt709:out_color_matrix=bt709,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}"
        )
    else:
        vf = (
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}"
        )
    cmd = [FFMPEG, "-y", "-i", src]
    if trim_in:
        cmd += ["-ss", f"{trim_in}"]
    if trim_out:
        cmd += ["-to", f"{trim_out}"]
    cmd += ["-vf", vf]
    if SEAM.get("audio_crossfade") and (afade_head_s > 0 or afade_tail_s > 0):
        af_parts = []
        if afade_head_s > 0:
            af_parts.append(f"afade=t=in:st=0:d={afade_head_s:.4f}")
        if afade_tail_s > 0:
            dur = probe_duration(src) if not dry else 10.0
            eff_end = (trim_out if trim_out else dur) - (trim_in or 0.0)
            af_parts.append(f"afade=t=out:st={max(eff_end - afade_tail_s, 0):.4f}:d={afade_tail_s:.4f}")
        cmd += ["-af", ",".join(af_parts)]
    cmd += ["-c:v", "libx264", "-crf", "12", "-preset", "fast", "-pix_fmt", "yuv420p"]
    if SEAM.get("color_pipeline"):
        cmd += ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                "-color_range", "tv"]
    cmd += ["-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", dst.with_suffix(".mkv")]
    run(cmd, dry)


def boundary_ssim(prev_mkv: Path, next_mkv: Path, work: Path, tag: str, dry: bool) -> float | None:
    """[SEAM d-215] SSIM between the outgoing clip's LAST frame and the incoming clip's
    frame 0. >= 0.99 means the chained conditioning frame survived as a duplicate —
    two identical frames across a cut read as a stutter."""
    if dry:
        return None
    a = work / f"ssim_{tag}_out.png"
    b = work / f"ssim_{tag}_in.png"
    r1 = subprocess.run([FFMPEG, "-y", "-v", "error", "-sseof", "-0.5", "-i", str(prev_mkv),
                         "-vsync", "0", "-update", "1", "-q:v", "1", str(a)],
                        capture_output=True, text=True)
    r2 = subprocess.run([FFMPEG, "-y", "-v", "error", "-i", str(next_mkv),
                         "-frames:v", "1", "-q:v", "1", str(b)],
                        capture_output=True, text=True)
    if r1.returncode != 0 or r2.returncode != 0 or not a.exists() or not b.exists():
        return None
    proc = subprocess.run([FFMPEG, "-i", str(a), "-i", str(b),
                           "-filter_complex", "[0][1]ssim", "-f", "null", "-"],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    import re
    m = re.search(r"All:([0-9.]+)", proc.stderr or "")
    return float(m.group(1)) if m else None


def drop_first_frame(mkv: Path, fps: int, dry: bool) -> Path:
    """[SEAM d-215] Drop the incoming clip's duplicated frame 0 (and its 1/fps of audio,
    keeping A/V sync). Writes <stem>_dedup.mkv beside the input and returns it."""
    out = mkv.with_name(mkv.stem + "_dedup.mkv")
    one = 1.0 / fps
    run([FFMPEG, "-y", "-i", mkv,
         "-vf", "select='gte(n\\,1)',setpts=PTS-STARTPTS",
         "-af", f"atrim=start={one:.6f},asetpts=PTS-STARTPTS",
         "-vsync", "0", "-c:v", "libx264", "-crf", "12", "-preset", "fast",
         "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", out], dry)
    return out


def apply_audio_bridges(cut: Path, bridges: list[dict], work: Path, dry: bool) -> Path:
    """[SEAM d-216] Sound bridges at treated boundaries — picture and sound never cut on
    the same frame. Sync-safe implementation (no timeline-length change):
      J-cut (audio_lead_s): the INCOMING clip's first `lead` seconds of audio are
        UNDERLAID beneath the outgoing tail at -6dB with a fade-in, ending at the cut —
        the next world's ambience arrives before its picture.
      L-cut (audio_tail_s): the OUTGOING clip's last `tail` seconds of audio are
        UNDERLAID beneath the incoming head at -6dB with a fade-out — the old world's
        room decays across the cut.
    Full track-replacement J/L cuts would require re-timing every downstream clip's
    audio; the additive-bridge form delivers the perceptual effect without desync risk.
    """
    cur = cut
    for i, br in enumerate(bridges):
        t = br["time"]
        parts, extra_inputs = [], []
        n = 1
        mix = ["[0:a]"]
        if br.get("lead_s") and br.get("incoming"):
            L = min(float(br["lead_s"]), 2.0)
            extra_inputs += ["-i", str(br["incoming"])]
            delay_ms = max(int((t - L) * 1000), 0)
            parts.append(f"[{n}:a]atrim=0:{L:.3f},afade=t=in:st=0:d={min(L, 0.25):.3f},"
                         f"volume=-6dB,adelay={delay_ms}|{delay_ms}[jb{i}]")
            mix.append(f"[jb{i}]")
            n += 1
        if br.get("tail_s") and br.get("outgoing"):
            T = min(float(br["tail_s"]), 2.0)
            src_dur = probe_duration(Path(br["outgoing"])) if not dry else 10.0
            extra_inputs += ["-i", str(br["outgoing"])]
            delay_ms = max(int(t * 1000), 0)
            parts.append(f"[{n}:a]atrim={max(src_dur - T, 0):.3f},asetpts=PTS-STARTPTS,"
                         f"afade=t=out:st=0:d={T:.3f},volume=-6dB,adelay={delay_ms}|{delay_ms}[lb{i}]")
            mix.append(f"[lb{i}]")
            n += 1
        if len(mix) == 1:
            continue
        parts.append("".join(mix) + f"amix=inputs={len(mix)}:duration=first:normalize=0[aout]")
        out = work / f"bridge{i:02d}.mkv"
        run([FFMPEG, "-y", "-i", cur, *extra_inputs, "-filter_complex", ";".join(parts),
             "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "pcm_s16le", out], dry)
        cur = out
    return cur


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
        premix = work / "premix.mkv"
        run([FFMPEG, "-y", "-i", cut, "-c", "copy", premix], dry)
        return loudnorm_two_pass(premix, out, target_lufs, dry)

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
        fades = ""
        if m.get("fade_in_s"):
            fades += f",afade=t=in:d={m['fade_in_s']}"
        if m.get("fade_out_s"):
            fdur = probe_duration(project / m["path"]) if not dry else 20.0
            st = max(fdur - float(m["fade_out_s"]), 0)
            fades += f",afade=t=out:st={st}:d={m['fade_out_s']}"
        parts.append(f"[{idx}:a]anull{fades},adelay={delay}|{delay},volume={m['gain_db']}dB[{lbl}pre]")
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
                 f"amix=inputs={1 + len(mix_inputs)}:duration=first:normalize=0[aout]")
    fc = ";".join(parts)
    premix = work / "premix.mkv"
    cmd += ["-filter_complex", fc, "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "pcm_s16le", premix]
    run(cmd, dry)
    return loudnorm_two_pass(premix, out, target_lufs, dry)


def loudnorm_two_pass(premix: Path, out: Path, target_lufs: float, dry: bool) -> Path:
    """Two-pass loudnorm in LINEAR mode: pure gain to target, dynamics untouched —
    single-pass loudnorm is adaptive and audibly lifts protected silences."""
    if dry:
        return premix
    proc = subprocess.run(
        [FFMPEG, "-i", str(premix), "-af",
         f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    tail = (proc.stderr or "")[proc.stderr.rfind("{"):]
    m = json.loads(tail[:tail.rfind("}") + 1])
    af = (f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11:linear=true:"
          f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}")
    run([FFMPEG, "-y", "-i", premix, "-c:v", "copy", "-af", af, "-c:a", "pcm_s16le", out], dry)
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
    # caption mode: the PRESET decides (master none / youtube srt / tiktok burn);
    # ed.captions supplies language/style, and its mode 'none' disables captions globally.
    preset_mode = preset.get("captions", "none")
    mode = "none" if captions.get("mode") == "none" else preset_mode
    if mode == "burn" and srt_path and (srt_path.exists() or dry):
        srt_escaped = str(srt_path).replace("\\", "/").replace(":", "\\:")
        # ASS units are relative to PlayResY=288: FontSize 8 ≈ 53px at 1920-tall output.
        # MarginV 48 ≈ 320px up from the bottom — inside the blurred pad, BELOW the 16:9 film band.
        style = "FontSize=8,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=1,Shadow=0,Alignment=2,MarginV=48"
        vf_parts.append(f"subtitles='{srt_escaped}':force_style='{style}'")
    vf = ",".join(vf_parts)  # the vertical chain is one linear filtergraph (split..overlay), ',' continues it

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [FFMPEG, "-y", "-i", mixed]
    cmd += ["-filter_complex" if aspect_vertical else "-vf", vf]
    cmd += ["-r", str(fps), "-c:v", preset["video_codec"], "-crf", str(preset["crf"]),
            "-pix_fmt", preset["pixel_format"], "-c:a", preset["audio_codec"],
            "-b:a", preset["audio_bitrate"], "-movflags", "+faststart"]
    # [SEAM d-214] tag deliverables bt709/tv + one container timebase (mp4/mov only).
    if SEAM.get("color_pipeline"):
        cmd += ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                "-color_range", "tv"]
        if out_path.suffix.lower() in (".mp4", ".mov", ".m4v"):
            cmd += ["-video_track_timescale", "24000"]
    cmd += [out_path]
    run(cmd, dry)
    if mode == "srt" and srt_path and srt_path.exists():
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
    hard = ("cut", "match_cut")
    mezz = []
    for i, t in enumerate(timeline):
        src = clip_paths[t["clip_ref"]]
        dst = work / f"n_{t['order']:02d}_{t['clip_ref']}"
        # [SEAM d-216] 3-frame audio fade pair at every HARD-cut boundary edge — no hard splices.
        head = AFADE_PAIR_S if (i > 0 and timeline[i - 1]["transition_out"]["type"] in hard) else 0.0
        tail = AFADE_PAIR_S if (i < len(timeline) - 1 and t["transition_out"]["type"] in hard) else 0.0
        normalize_clip(src, dst, bw, bh, fps, t.get("in_s"), t.get("out_s"), args.dry_run,
                       afade_head_s=head, afade_tail_s=tail)
        mp = dst.with_suffix(".mkv")
        mezz.append({"path": mp, "duration": probe_duration(mp) if not args.dry_run else 10.0,
                     "transition_out": t["transition_out"]})

    # [SEAM d-215] duplicate-conditioning-frame detection at chained boundaries.
    seam_boundaries = []
    if SEAM.get("dup_frame_trim"):
        chained_refs = {e.get("clip_id") for e in manifest.get("clips", [])
                        if e.get("status") == "approved"
                        and (e.get("start_frame") or e.get("chain_start_offset_s") is not None)}
        for i in range(len(mezz) - 1):
            nxt_ref = timeline[i + 1]["clip_ref"]
            if nxt_ref not in chained_refs:
                continue
            s = boundary_ssim(mezz[i]["path"], mezz[i + 1]["path"], work, f"b{i:02d}", args.dry_run)
            rec = {"boundary": f"{timeline[i]['clip_ref']}->{nxt_ref}", "frame0_ssim": s,
                   "dropped_dup_frame": False}
            if s is not None and s >= 0.99:
                new_path = drop_first_frame(mezz[i + 1]["path"], fps, args.dry_run)
                mezz[i + 1]["path"] = new_path
                mezz[i + 1]["duration"] = probe_duration(new_path) if not args.dry_run else 10.0
                rec["dropped_dup_frame"] = True
                print(f"  [SEAM d-215] duplicate frame at {rec['boundary']} (SSIM {s:.4f}) - frame 0 dropped")
            seam_boundaries.append(rec)

    print("[2/4] joining timeline with transitions")
    cut = join_timeline(mezz, work, fps, args.dry_run)

    # [SEAM d-216] J/L sound bridges at boundaries carrying an audio_treatment.
    total_fade_s = 0.0
    if SEAM.get("audio_crossfade"):
        bridges, t_cursor = [], 0.0
        for i, (t, m) in enumerate(zip(timeline, mezz)):
            t_cursor += m["duration"]
            tr = t["transition_out"]
            if tr["type"] in XFADE_MAP and i < len(timeline) - 1:
                t_cursor -= float(tr.get("duration_s") or DEFAULT_XFADE_S)
                total_fade_s += float(tr.get("duration_s") or DEFAULT_XFADE_S)
            at = t.get("audio_treatment")
            if at and i < len(timeline) - 1 and (at.get("audio_lead_s") or at.get("audio_tail_s")):
                bridges.append({"time": t_cursor, "lead_s": at.get("audio_lead_s"),
                                "incoming": mezz[i + 1]["path"], "tail_s": at.get("audio_tail_s"),
                                "outgoing": m["path"]})
        if bridges:
            print(f"  [SEAM d-216] applying {len(bridges)} sound bridge(s)")
            cut = apply_audio_bridges(cut, bridges, work, args.dry_run)
    else:
        total_fade_s = sum(float(t["transition_out"].get("duration_s") or DEFAULT_XFADE_S)
                           for i, t in enumerate(timeline[:-1])
                           if t["transition_out"]["type"] in XFADE_MAP)

    # [SEAM d-214] xfade timing law: every video crossfade SHORTENS the timeline by its
    # duration. Cue-sheet timecodes must be computed AFTER transitions are final.
    if total_fade_s > 0:
        final_dur = probe_duration(cut) if not args.dry_run else 0.0
        print(f"  [SEAM] crossfades shortened the timeline by {total_fade_s:.2f}s - "
              f"verify audio cue timecodes were authored against the POST-transition timeline")
        if not args.dry_run and final_dur > 0:
            for mcue in ed.get("audio", {}).get("music", []):
                if float(mcue.get("in_s", 0)) > final_dur:
                    print(f"  [WARN] music cue '{mcue.get('path')}' in_s={mcue.get('in_s')} is BEYOND "
                          f"the {final_dur:.1f}s timeline - cue sheet predates final transitions?")

    print("[3/4] audio mix")
    mixed = mix_audio(cut, ed.get("audio", {}), project, work, args.skip_audio, args.dry_run)

    print("[4/4] rendering deliverables")
    srt = project / "renders" / "captions.srt"
    outputs = []
    attempts_dir = project / "renders" / "attempts"
    render_attempts = {}
    for d in ed["deliverables"]:
        if d["preset_id"] not in wanted:
            continue
        out_path = project / d["out_path"]
        # Director order 2026-07-31: renders are versioned - never overwrite silently.
        # An existing output is moved to renders/attempts/<stem>_attemptNN<ext> first.
        n = 1
        if out_path.exists() and not args.dry_run:
            attempts_dir.mkdir(parents=True, exist_ok=True)
            existing = sorted(attempts_dir.glob(f"{out_path.stem}_attempt*{out_path.suffix}"))
            n = len(existing) + 1
            shutil.move(str(out_path), attempts_dir / f"{out_path.stem}_attempt{n:02d}{out_path.suffix}")
            n += 1
        render_attempts[d["preset_id"]] = n
        print(f"  {d['preset_id']}: attempt {n:02d}")
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
        "metadata": {"render_attempts": render_attempts,
                     "note": "prior attempts preserved in renders/attempts/ (Director order 2026-07-31)",
                     "seam": {"flags_active": {k: bool(v) for k, v in SEAM.items()},
                              "boundaries": seam_boundaries,
                              "xfade_timeline_shortening_s": round(total_fade_s, 3)}},
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
