---
name: storyboard-qc
description: "Mechanical, low-token QC procedure for stage-8 grid storyboard pages — panel-by-panel extraction via scripts/storyboard_qc.py, a defect taxonomy built from this production's real failures, and the exact Higgsfield MCP call shapes. Use when self-QCing a generated storyboard page, verifying a regen, or diagnosing why a page failed."
---

# Storyboard QC

Read this AFTER `skills/stages/08-storyboard-director.md` and `skills/tech/storyboard-design/SKILL.md`, as the concrete "how" behind their self-QC checklist. This skill exists because two things kept happening: (1) real defects slipped past self-QC into the Director's gate (d-051, d-058, d-062, d-068), and (2) agents were re-deriving crop pixel math by hand in ad-hoc Bash every scene — expensive and error-prone (a real transcript showed an artist typing `crop=672:380:0:380` from scratch, more than once, for the same page). `scripts/storyboard_qc.py` replaces the hand math; this skill replaces the improvised checklist.

## The procedure (binding — cheaper AND more accurate than reading the whole page repeatedly)

**Step 1 — split, once, no LLM tokens spent on arithmetic:**
```
.venv/Scripts/python scripts/storyboard_qc.py split-panels <page.png> --rows R --cols C --out-dir <scratch_dir>
```
Produces `panel_01.png … panel_NN.png` + `manifest.json` (exact pixel boxes used — never hand-compute crop coordinates again). Use your session's scratchpad directory for `<scratch_dir>`.

**Step 2 — per-panel pass:** `Read` each `panel_NN.png` individually (not the full page) and check it against the fixed list below. Small isolated crops read sharper and cheaper than the full 9-up grid, AND — the real payoff — after a regen you re-check only the ONE panel that changed, not the whole page again.

**Step 3 — integrity pass across panels** (this is where most real defects in this production hid — see taxonomy class D below):
```
.venv/Scripts/python scripts/storyboard_qc.py diff <panel_a.png> <panel_b.png> --out <scratch_dir>/diff.png
```
Produces ONE image: source A | source B | amplified difference, side by side. `Read` that one image. For any scene where the direction says two panels must share the identical camera setup (a "locked static" scene, or the first/last panel of a continuous move), diff them: differences should be confined to characters/light — if walls, columns, or background scale light up in the diff panel, the camera moved and that is a fail. This is the exact check that would have caught the camera-lock defect both S11 artists shipped on their first attempt (d-072) — do this BEFORE calling a page done, not after the Director catches it.

**Step 4 — fix or disclose:** ONE regeneration maximum (d-057). State the exact defect AND explicitly forbid the failure mode itself (not just "fix panel 9" — "panel 9 must use the IDENTICAL camera distance as panel 1; do not reveal any more of the body than panel 1 shows"). If the regen doesn't fix it, disclose — do not attempt a second silent regen (d-068: a regen aimed straight at a named defect still failed to fix it about half the time in this production; see taxonomy class H).

## Defect taxonomy (from this production's real decision log — read before generating, not just before checking)

| Class | What it looks like | Real examples | Catch it by |
|---|---|---|---|
| **A. Count/identity** | Wrong number of characters/objects in a panel (extra or missing) | d-051 dropped twin; d-058 4th cell added; d-062 twin hidden behind an effect; d-068 4-cells-instead-of-3, survived a regen | Per-panel count against the descriptor's fixed cast for the scene |
| **B. Axis/geometry** | Left-right positions swap across panels or vs. the direction's blocking | Early attempts on S07/S08/S09 | Compare frame-left/frame-right assignment panel-to-panel and against `scene_direction.blocking` |
| **C. State-law violation** | Goggles up when canon says down (or reverse), wrong wrist for an accessory, wet/dry mismatch, forbidden accessory | d-023-class nsfw phrasing; goggle-state slips at S06/S07; spurious wrist-watch d-based S07-B | Check every present character against `outfit_by_scene` / `default_outfit`, not memory |
| **D. Camera-continuity break** | A "locked static" or "one continuous move" scene where a panel secretly changes distance/angle | d-070 push-in pulled back mid-sequence; d-072 both S11 artists widened panel 9 to show legs, breaking the lock | `diff` the two panels that must match (Step 3) — do not eyeball it |
| **E. Panel-chrome/formatting** | Numbering style breaks (font/box style changes mid-page), gutters uneven | d-065 boxed-corner-number style dropped in panels 7–9 | Per-panel check includes "number label matches the style of panel 1" |
| **F. Prop continuity** | An object required by continuity_notes vanishes or teleports between panels | d-053 lemonade glass disappeared from a panel and had to be edited back in | Trace one named prop across all panels in the per-panel pass |
| **G. Content-filter false positive** | Innocent content flagged nsfw, almost always from body-descriptive phrasing on the child character | Origin d-017; recurred at S06 | Never use body-proportion language for Milo; cartoon-craft/energy language only |
| **H. Regen doesn't fix its own target** | A regeneration prompt correctly names the defect; the model ships the same defect anyway | d-068 (S09-B: targeted regen, defect persisted); d-062 (S07-A: partial fix only) | Always re-run Step 2/3 on the regenerated panel — never trust a regen was applied without re-checking it |

Classes A, C, E, F are catchable in Step 2 alone. Class D requires Step 3's diff. Class H is why Step 4 says disclose-don't-loop — assume roughly half of targeted regens will not land, and budget accordingly rather than chasing it.

## Higgsfield MCP call shapes (verified against real production logs — use these, don't improvise)

`generate_image` params (all storyboard pages use this shape):
```json
{
  "model": "gpt_image_2",
  "get_cost": true,
  "prompt": "<the full page prompt>",
  "aspect_ratio": "16:9",
  "quality": "high",
  "resolution": "2k",
  "medias": [{"role": "image", "value": "<media_id>"}, ...]
}
```
Preflight once with `get_cost: true` (no `medias` needed for the estimate), confirm the credits match the plan, then call again without `get_cost` and with `medias` populated to actually generate. `medias[].value` is always a media_id/job_id — never a URL or local path.

Poll `job_display` with the returned job id until `status: "completed"`. Typical wait: `until [ $SECONDS -ge 110 ]; do sleep 5; done` then poll once — polling in a tight loop wastes calls, one wait-then-check is standard for this model's latency.

**The exact stall cause, confirmed from a real transcript:** an unlimited `Read` of `lock_descriptors.json` (a large canonical artifact) triggered a 600-second stream stall. **Never `Read` a full artifact JSON.** Use a targeted slice instead:
```
.venv/Scripts/python -c "import json; d=json.load(open('projects/<slug>/artifacts/lock_descriptors.json', encoding='utf-8')); print(json.dumps(next(c for c in d['characters'] if c['char_id']=='CH01'), indent=1))"
```
Briefs should already inline the slices you need (per the stage-8 brief template) — reach for a manual slice only when the brief is missing something, and always slice, never full-Read.
