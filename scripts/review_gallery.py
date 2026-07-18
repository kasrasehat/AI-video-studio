"""review_gallery.py — build a static HTML compare gallery for Director variant picks.

Usage:
  python scripts/review_gallery.py <slug> [--source asset_manifest|storyboard_set] [--open]

Reads projects/<slug>/artifacts/<source>.json and writes projects/<slug>/gallery/<source>.html —
a self-contained page (relative file paths, no external requests) showing each element's
variants side by side: images inline, audio as <audio> players, provenance and cost per variant.
Locked elements are badged; the Director picks by telling the agent, not by clicking.
"""
from __future__ import annotations

import argparse
import html
import sys
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import favs_lib as lib  # noqa: E402

AUDIO_EXT = {".mp3", ".wav", ".m4a", ".ogg"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

CSS = """
body{font-family:system-ui,sans-serif;margin:0;padding:24px;background:#1b1626;color:#FFF3DC}
h1{font-size:20px;margin:0 0 4px} .sub{color:#c9b8d8;font-size:13px;margin-bottom:24px}
.element{background:#241d33;border-radius:12px;padding:16px;margin-bottom:24px}
.element h2{font-size:16px;margin:0 0 2px} .eid{color:#F27BA0;font-family:monospace;font-size:12px}
.locked{display:inline-block;background:#2f7d4f;color:#fff;border-radius:6px;padding:1px 8px;font-size:11px;margin-left:8px}
.pending{display:inline-block;background:#8a6d1f;color:#fff;border-radius:6px;padding:1px 8px;font-size:11px;margin-left:8px}
.variants{display:flex;gap:16px;flex-wrap:wrap;margin-top:12px}
.variant{background:#2e2542;border-radius:10px;padding:12px;flex:1;min-width:280px;max-width:520px}
.variant.selected{outline:3px solid #F5A623}
.variant h3{font-size:13px;margin:0 0 8px;color:#FFD97A}
.views{display:flex;gap:8px;flex-wrap:wrap}
.views figure{margin:0;text-align:center}
.views img{max-width:150px;max-height:200px;border-radius:6px;display:block}
.views figcaption{font-size:11px;color:#c9b8d8;margin-top:2px}
audio{width:100%;margin:4px 0}
.meta{font-size:11px;color:#c9b8d8;margin-top:8px;line-height:1.5}
.prompt{font-size:11px;color:#a893c2;margin-top:6px;max-height:72px;overflow:auto;background:#1b1626;border-radius:6px;padding:6px}
.missing{color:#e06c75;font-size:12px}
"""


def render_variant(v: dict, selected: bool, project_dir: Path) -> str:
    parts = [f'<div class="variant{" selected" if selected else ""}">']
    title = html.escape(v.get("variant_id", "?")) + (" — SELECTED" if selected else "")
    parts.append(f"<h3>{title}</h3>")
    parts.append('<div class="views">')
    for f in v.get("files", []):
        rel = f.get("path", "")
        # gallery/ lives one level below the project root
        src = html.escape("../" + rel)
        ext = Path(rel).suffix.lower()
        exists = (project_dir / rel).exists()
        label = html.escape(f.get("view", "") or Path(rel).name)
        if not exists:
            parts.append(f'<figure><div class="missing">missing:<br>{html.escape(rel)}</div></figure>')
        elif ext in AUDIO_EXT:
            parts.append(f'<figure style="width:100%"><audio controls src="{src}"></audio><figcaption>{label}</figcaption></figure>')
        elif ext in IMAGE_EXT:
            parts.append(f'<figure><a href="{src}"><img src="{src}" alt="{label}"></a><figcaption>{label}</figcaption></figure>')
        else:
            parts.append(f'<figure><a href="{src}">{html.escape(Path(rel).name)}</a><figcaption>{label}</figcaption></figure>')
    parts.append("</div>")
    gen = v.get("generator", {})
    meta = f"model: {html.escape(str(gen.get('model', '?')))} · seed: {html.escape(str(v.get('seed', gen.get('seed', '—'))))} · cost: {v.get('cost_usd', 0)}"
    parts.append(f'<div class="meta">{meta}</div>')
    if gen.get("prompt"):
        parts.append(f'<div class="prompt">{html.escape(gen["prompt"])}</div>')
    parts.append("</div>")
    return "".join(parts)


def render_asset_manifest(manifest: dict, project_dir: Path) -> str:
    out = []
    for el in manifest.get("elements", []):
        badge = '<span class="locked">LOCKED</span>' if el.get("locked") else '<span class="pending">pick pending</span>'
        out.append('<div class="element">')
        out.append(f"<h2>{html.escape(el.get('element_id', '?'))} {badge}</h2>")
        out.append(f'<div class="eid">{html.escape(el.get("element_type", ""))} · from {html.escape(el.get("source_descriptor_ref", ""))}</div>')
        out.append('<div class="variants">')
        for v in el.get("variants", []):
            out.append(render_variant(v, v.get("variant_id") == el.get("selected_variant_id"), project_dir))
        out.append("</div></div>")
    return "".join(out)


def render_storyboard_set(sb: dict, project_dir: Path) -> str:
    out = []
    for scene in sb.get("scenes", []):
        out.append('<div class="element">')
        out.append(f"<h2>{html.escape(scene.get('scene_id', '?'))}</h2>")
        out.append('<div class="variants">')
        for v in scene.get("variants", []):
            files = [{"path": fr.get("image_path", ""), "view": f"shot {fr.get('shot_no')} · {fr.get('frame_id')}"}
                     for fr in v.get("frames", [])]
            pseudo = {"variant_id": f"Board {v.get('variant_id')}: {v.get('approach_note', '')}",
                      "files": files, "generator": {}, "cost_usd": sum(fr.get("cost_usd", 0) for fr in v.get("frames", []))}
            out.append(render_variant(pseudo, False, project_dir))
        out.append("</div></div>")
    return "".join(out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug")
    parser.add_argument("--source", choices=["asset_manifest", "storyboard_set"], default="asset_manifest")
    parser.add_argument("--open", action="store_true", help="open the gallery in the default browser")
    args = parser.parse_args(argv)

    project_dir = lib.project_dir(args.slug)
    artifact_path = project_dir / "artifacts" / f"{args.source}.json"
    if not artifact_path.exists():
        print(f"[ERROR] {artifact_path} not found")
        return 1
    data = lib.read_json(artifact_path)

    body = render_asset_manifest(data, project_dir) if args.source == "asset_manifest" else render_storyboard_set(data, project_dir)
    page = (f"<!doctype html><meta charset='utf-8'><title>{args.slug} — {args.source}</title>"
            f"<style>{CSS}</style><h1>{html.escape(args.slug)} — {args.source.replace('_', ' ')}</h1>"
            f"<div class='sub'>Compare variants; tell the agent your picks (e.g. \"CH01_sheet: V2\"). "
            f"Generated by review_gallery.py — refresh after regeneration.</div>{body}")

    out_path = project_dir / "gallery" / f"{args.source}.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page, encoding="utf-8")
    print(f"[OK] gallery written: {out_path}")
    if args.open:
        webbrowser.open(out_path.as_uri())
    return 0


if __name__ == "__main__":
    sys.exit(main())
