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
2. **Cue sheets with timecodes:** every music cue (`MC..`) gets timeline in/out points derived from the Phase-1 cut. Complete generation prompts saved per cue, instrumental by default.
2b. **SFX LIVE IN THE VIDEO MODEL (BINDING — d-160, the heartbeat-doubling lesson):** sound effects are generated WITH the clips — `sound_direction` goes into every generation prompt and Seedance bakes the SFX/ambience into the clip audio. Post-audio SFX cues are EXCEPTION-only, limited to: (a) sounds that CANNOT exist in any clip (an audio button under post-iris black, sound across an added transition), and (b) repairing a directed sound VERIFIED ABSENT at the assembled-cut QC listen. Never author a post bed that duplicates a sound class the clips carry — this production's separately-added heartbeat bed doubled the clips' own baked heartbeats and audibly degraded the mix. When in doubt: the clip's baked audio wins, the post cue is not written. Every exception cue still cites its `source_line` and is Director-gated.
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

## Seam pass (d-191, audience feedback: visible cuts read as unnatural — BINDING)

Before the watch-through QC, walk EVERY clip boundary in the assembled cut and treat it explicitly:

**[SEAM d-217] The seam pass is an ENFORCED ESCALATION LADDER — per boundary, in order, stop at the first rung that makes the seam read invisible/acceptable:**

① **Classify** the seam from scene_list `boundary_class_out` (verify against scene_direction and the d-158 hint-target rule — a hint written for a scene that is no longer adjacent is void). Record the class per boundary in `edit_decisions` notes.
② **Micro-trim to motion match.** Cut on MOTION ONSET (~⅓ into an action; never rest-to-rest). Trim `out_s`/`in_s` to the frames where motion states agree — a limb mid-swing on both sides. Frame-step ±6 frames each side (ffmpeg extraction) and LOOK; never judge a seam from the timeline alone. Distrust the first ~2–12 and last ~12 frames of every generation (AI dead zones) — the edit boundary must never equal the generation boundary; overlap clips (d-213) put the splice inside re-covered footage precisely for this.
③ **Color-match the incoming clip.** Measure mean Y/U/V of the outgoing last ~12 frames and incoming first ~12 frames; if ΔY>3 or chroma drifts, correct the incoming clip and EASE the correction in over ~12 frames (a stepped correction is its own pop).
④ **Audio treatment.** J/L-cut via `audio_treatment` (d-216), the continuous music/ambience bed crossing the cut (d-161), and — when the motion match is imperfect — a sourced TRANSIENT (impact/splash/footfall that belongs to the scene) placed ON the cut frame as a masking device. Picture and sound never cut on the same frame.
⑤ **Micro-crossfade** — 2–4 frames, ≤0.15s, CONTINUOUS seams only (at that length it reads as motion blur; ≥6 frames reads as a time transition). Never on new_beat or hinge seams — those want a clean cut.
⑥ **Optical-flow bridge** — 3–7 interpolated frames (RIFE/FILM) between the last good outgoing frame and first good incoming frame; local, free, no credits.
⑦ **Report to the Director:** this seam is a GENERATION problem. Options: overlap regeneration of the successor (d-213, priced, d-114-gated) or the POSTPONED WAN VACE joiner (Director-only unlock). Never bury a rung-7 seam in the render.

**Objective seam gate (flag `seam_metrics_gate` in `config/seam_policy.yaml`):** per boundary record into `clip_qc_report`/`render_report` (assemble.py writes its half into render_report.metadata.seam automatically): tail & head motion energy (rest→rest detector — rest→rest on a `continuous` boundary is an AUTOMATIC finding), frame-0 SSIM (duplicate detector, d-215), ΔY/ΔU/ΔV across the cut, and the qc-critic's invisible/acceptable/visible rating. **The film's target is zero `visible` seams.**

**Hinge checklist (every location/time change):** establishing shot HELD 2–5s after the change before anything tight (audience re-orientation is a measurable cost); J-cut mandatory (incoming ambience 12–24 frames early); dip-to-black/wipe reserved for ACT boundaries only — mark between dramatic units, hide within them.

Root cause note (why this section exists): E01 audiences reported "clear cuts / unnatural transitions." Upstream, d-191 also hardened stage 5 (boundary motion contract: every transition_out names exit motion + absorption) and stage 9 (handoff beat: chained clips settle into describable states; successors continue inherited motion) — this pass is the last line, not the only one.

## Cue-transition smoothing (d-161)

Phase 2 cue design and Phase 3 generation follow `skills/tech/music` → "Cue-transition craft": sneak-in entrances by default, dovetails at cue→cue splices, directed hard exits preserved as events, and SUBTLE emotional gradation — adjacent cues share ≥2 bridge parameters (instrument overlap / related key / tempo step ≤~15%), and a cue following a tender scene opens in the inherited warmth before rotating to its own character. Mix ramps are recorded per cue in `edit_decisions.audio.music[].fade_in_s/fade_out_s`.
