# Integration Director — stage 10

Assembly, sound & delivery: turn the approved clips into the finished film. Full version (M7, 2026-07-31) — supersedes the stub. Sound is DESIGNED before it is generated (Director order: this stage moves product value more than any other — absolute caution).

## IO contract (from pipeline.yaml)
- Consumes: `generation_manifest`, `clip_qc_report`, `scene_direction`, `scene_list`, `brief`.
- Produces: `artifacts/edit_decisions.json`, `artifacts/audio_direction.json`, `artifacts/render_report.json`.
- QA loop: `qc-critic` watch-through of the assembled cut, max 2 rounds, report-only (d-114 — fixes are Director-ordered).
- Gate: the Director approves (1) the edit + audio direction ON PAPER, (2) each generated audio cue, (3) the final cut. Resume unit: deliverable preset.

## Standing rulings that bind this stage
- **d-114:** every paid call (music cue, SFX cue, upscale, anything) is individually Director-gated; prompts/plans saved BEFORE generation. QC reports, the Director decides.
- **d-145:** S01/S04 (720p) are scaled locally by `assemble.py` — no provider upscale unless the final result disappoints and the Director orders it.
- **d-146:** deliverables = master + youtube_16x9 + tiktok_9x16 (all from `config/delivery_presets.yaml`).
- **d-147:** Higgsfield-first was checked and Higgsfield has no music/SFX/assembly service → **d-150:** ElevenLabs is the audio backend (key in gitignored `.env`; verify PAID tier + commercial license via `GET /v1/user/subscription` BEFORE the first paid cue — at key time the account read tier=free).
- Archive-before-edit, schema validation, decision logging — as everywhere.

## Phase 1 — Edit decisions (free, on paper)

Author `edit_decisions.json`:
1. **Timeline:** the approved clips in scene order (clip_ref = manifest clip_id; `scripts/assemble.py` resolves files via the manifest — approved entries only). Trims (`in_s`/`out_s`) only where a clip's tail fights the next cut.
2. **Transitions from the direction, never uniform:** each boundary's `transition_out` comes from the scene's `transition_out_hint` / the direction's cut logic, with `source` naming it. Types: `cut` (default), `match_cut` (S13→S14 glitter comet), `xfade`, `dip_black`, `wipe`, `iris_out` (S17's ending: circle-close into black on the dog's extreme close-up).
2b. **HINT-TARGET VERIFICATION (BINDING — d-158):** a `transition_out_hint` is bound to the neighbor it was AUTHORED against, not to whatever scene sits next today. Before mapping any hint to a boundary, confirm the current next scene is the one the hint describes (read the hint's content — it usually names or implies its target: "slam" = the reveal, "into golden light" = the heart hall). Mid-production insertions (letter-suffixed scene ids are the tell) shift neighbors WITHOUT updating hints. A hint written for a later scene is VOID at the new boundary: author that boundary from the actual motion at the cut instead — continuous action defaults to a plain `cut`; never let a stylized transition (dip/wipe/xfade) ride across an inserted scene's seam. This is the bug the Director caught on S05→S05A in the first assembled cut.
3. **Captions block** per brief language (srt sidecar for youtube preset, burn for vertical — per preset config). Caption text comes from the scenes' dialogue lines verbatim, timed against the assembled cut.
4. **Deliverables list** per d-146.
→ Present to the Director together with Phase 2. Nothing renders yet.

## Phase 2 — Audio direction (free, on paper — the Sound Direction design)

Author `audio_direction.json` (schema `audio_direction`) — sound is directed like scenes:
1. **Score architecture first:** theme(s) with dramatic meaning + instrumentation + tempo/key; the emotional arc mapped scene-span by scene-span; **protected silences** carried over from scene_direction rhythm (a silence the direction protected stays protected in the score); continuity notes so adjacent cues share tempo/key families and never clash at cuts.
2. **Cue sheets with timecodes:** every music cue (`MC..`) and SFX cue (`FX..`) gets timeline in/out points derived from the Phase-1 cut. Every SFX cue cites its `source_line` from `scene_direction.sound_direction` — **nothing invented**. Complete generation prompts saved per cue, instrumental by default.
3. **Mix plan:** the dialogue law (Seedance-baked clip audio is untouchable; music sidechain-ducks under it; SFX placed to picture), target −14 LUFS, ducking params.
4. **Main-theme audition plan:** ~2 genuinely distinct style schools (variant discipline), short cheap cues, prompts saved.
→ **Director gate on paper** (both artifacts). Zero spend to this point.

## Phase 3 — Audio generation (paid, per-cue gates)

1. **Tier check first** (see d-150 caveat) — free tier lacks the commercial license; halt and report if not resolved.
2. **Audition:** generate the ~2 main-theme variants (`skills/tech/music` — ElevenLabs Music API, `music_length_ms` exact) → Director listens, picks → `selected_variant_id`. The winner's style language anchors EVERY other cue prompt (consistency-guard for sound).
3. **Cues:** generate music cues then SFX (`skills/tech/sound-effects`), each: cost stated → Director go → generate → cue-level QC (duration fits its slot, tail clears dialogue entrances, style matches the anchor) → **Director listens and approves** → status `approved`, file to `assets/audio/`, cost recorded. A rejected cue regenerates only on Director order with a fix directive.

## Phase 4 — Assembly, QC, render (assemble.py)

1. `python scripts/assemble.py <slug>` — normalize (d-145 local scaling happens here) → join with transitions → mix (ducked beds, one-shot SFX, loudnorm) → render per preset → ffprobe-verify into `render_report.json`. Use `--skip-audio` for a free early cut preview if the Director wants to see the edit before cues exist; `--preset master` to iterate on one preset.
2. **Watch-through QC (qc-critic, max 2 rounds, report-only):** full watch at native res — transition correctness, audio sync, dialogue intelligibility under the mix, caption timing, LUFS, S17 iris lands on the dog's eye. Findings reported; fixes Director-ordered.
3. **Final gate:** the Director watches the cut → approves → `render_report.final_qc.verdict = pass`, checkpoint `completed --approved`, decisions logged. Renders live in `projects/<slug>/renders/`.

## Pitfalls
- Generating ANY cue before the paper gate or the tier check (d-114 + license risk).
- Uniform crossfades (the transition ruling exists per boundary; cuts are the default for a reason).
- Music under a protected silence, or a cue tail stepping on a dialogue entrance.
- Trusting `render_report` written by assemble.py as finished — its `final_qc` is born `fix`; only the Director's watch-through turns it `pass`.
- Editing `.claude/skills` copies instead of `skills/tech` sources (sync law), or forgetting `projects/` is gitignored — artifacts live as files + history archives, not in git.
