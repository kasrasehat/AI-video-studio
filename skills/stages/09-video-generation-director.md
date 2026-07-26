# Video Generation Director — stage 9

Turn each scene's picked storyboard into a real ≤15s clip. This stage is the pipeline's most expensive per-unit spend by far (10–140 credits/clip vs 7–14 for a storyboard page) — cost discipline and the regen budget matter more here than anywhere upstream.

**Consumes:** `shot_selection`, `storyboard_set`, `lock_descriptors`, `asset_manifest`, `scene_list`, `scene_direction`.
**Produces:** `artifacts/generation_manifest.json` + `artifacts/clip_qc_report.json`.
**Gate:** the Director approves per scene batch. **Resume unit:** `clip` (`clip_id` = `S{nn}_C{nn}`, attempt tracked separately in `generation_manifest`).

## Before anything

Read `skills/tech/seedance-prompting/SKILL.md` (or the equivalent tech skill for the chosen model), `skills/tech/higgsfield-mcp` (media flow, cost preflight), `skills/meta/consistency-guard.md`. Read `ISSUES.md` ISSUE-008 before generating the first clip of any new scene pair — it tracks the open question of how cross-scene continuity (visual + audio) should be conditioned, and records what has and hasn't been tested yet.

## Model selection (binding — log as `model_selection`)

1. Pick the project default from `config/model_capabilities.yaml`. **HARD RULE: dialogue scenes only on models satisfying `policy.dialogue_scene_requires`** (verify per model entry, not by assumption — `reference_audio: true` + `quoted_dialogue_lipsync: true` at minimum).
2. **Cost is resolution- and duration-dependent, not fixed** — always preflight with `get_cost:true` using the ACTUAL params you intend (model, duration, resolution, aspect) before trusting any number from a skill file, a memory, or a prior session. Confirmed 2026-07-21: `seedance_2_0` 15s/1080p = 135cr; `seedance_2_0_mini` 15s/720p = 37.5cr. Announce the batch total before generating.
3. Per-scene override is allowed (`model_selection.per_scene_overrides`) with a stated reason — e.g. a non-dialogue establishing shot on a cheaper model.
4. **Budget check before scaling up:** sum the batch's estimated cost (scene durations × model's per-second rate, from a fresh preflight) against remaining balance (`show_plans_and_credits`) BEFORE committing to more than a few scenes at a time. Never silently downgrade quality to fit budget, never silently overspend — surface the arithmetic to the Director and let them choose (see decision d-095/d-096 for the pattern).

## Per-clip assembly (`prompt-smith` subagent, parallel per clip)

Each clip's generation call is built from six inputs, looked up per scene — **never invented, never approximated**:

1. **`start_image`** — the picked frame's **`promoted_media_id`** from `storyboard_set` (NOT the raw panel crop, NOT the page). Look up: `shot_selection[scene].selected_frames` → the entry with `role: start_frame` → its `frame_id` → find that frame in `storyboard_set[scene].variants[picked variant].frames` → read `promoted_media_id`. If a picked start frame has no `promoted_media_id`, STOP — the promotion pass is incomplete for that scene; do not fall back to the raw panel.
2. **`image_references`** (≤9 total, prioritize in this order): the scene's present characters' locked sheets (2–3 views each if budget allows) → the locked location plate → the scene's picked storyboard **PAGE** media_id (from `storyboard_set[scene].variants[picked].frames[0].media_id` — same value on every frame of that variant) → any locked object sheets referenced in the scene.
3. **`audio_references`** — the locked voice sample media_id for EVERY speaking character in the scene (from `asset_manifest`, the `*_voice` element's selected variant). Never omit, never substitute, never generate a new sample.
4. **`end_image`** — **INTENTIONALLY UNUSED this pass (Director decision d-046).** Do not set it, even though `shot_selection` records an `end_frame` role for most scenes — that role is an audit record for the future edit phase only (see the reconciliation note in `shot_selection.metadata`), not a value to promote or pin now. The page's final panel + the prompt's motion text carry the ending.
5. **`video_references`** — UNUSED by default this pass; only used inside the ISSUE-008 test or a Director-ordered method change. If used, log which decision authorized it.
6. **Prompt text** — 5-aspect assembly per `prompt-smith.md`: Subject / Subject Motion (dialogue as quoted lines) / Scene / Spatial / Camera, within the model's `prompt_words` window, every present character's `identity_anchors` verbatim + this scene's `outfit_by_scene` state, negative content from `negative_notes` + `forbidden_drift`.

**Chained-boundary continuity (Director order d-112 — last-frame chaining, supersedes the method-(a) baseline):** at CHAINED boundaries (same location / continuous action), scene N+1's `start_image` is the LAST FRAME of scene N's APPROVED clip — extracted with `scripts/extract_last_frame.py <clip.mp4>`, uploaded via `media_upload` (+ `media_confirm`), and passed as `start_image` in place of the promoted storyboard frame. The @-references block names it as "this shot's start frame — begin on exactly this image." This makes every cut pixel-continuous by construction: the new scene literally begins where the old one stopped.
- **The start frame must be `@reference_image_1`, named and described, and the opening beat must bridge from it (d-124 — confirmed on S07_C01 attempt 1, 126cr lost):** attaching the frame as `start_image` is NOT enough. If the prompt's references block doesn't name it (with a description of what it shows) and the 0–2s motion text opens on a contradicting composition, the model follows the prose and silently discards the frame — the chain breaks with no error. No fed reference of ANY role may be left unnamed in the prompt text.
- **No-start-frame clips (d-127):** at hard hinges or any clip without a chained start frame, the @-numbering SHIFTS — `@reference_image_1` becomes the first image actually in `medias`. Always rebuild the references block from the actual medias array of THIS call (position → role → file → @tag, verified both directions) before submitting; a block copied from a chained scene mislabels everything and wastes a full generation to debug.
- The promoted start frames remain the `start_image` at HARD HINGES (location changes), where pixel continuity across the cut is impossible and unwanted.
- Consequence to respect: chained scenes must now be generated IN ORDER, each after its predecessor's clip is APPROVED (the chain input doesn't exist until then) — parallel clip generation only across hard-hinge groups.
- Consequence to accept: the boarded panel-1 composition of a chained scene is advisory once the real last frame exists — the storyboard PAGE still rides along as an image_reference for beat staging, but the actual pixels of the cut come from the previous clip. If a predecessor's ending drifted from its board, the successor inherits the drift; catch it at the predecessor's QC, not the successor's.

**Director-inserted scenes (mid-production; precedents S05A/S05B d-117/d-120, S09A d-130):** the Director may insert new scenes between existing ones at any point during stage 9. Scene ids take a letter suffix (`S09A` — the `[A-Z]?` schema extension covers this in all artifact schemas). The insertion protocol, in order:
1. **Amend `scene_list.json` AND `scene_direction.json`** — archive both to `history/`, insert the full scene + direction entries at the correct position, bump `total_est_seconds`, validate both against their schemas. The inserted entries are written to the same field-completeness standard as original scenes (dialogue with delivery, continuity_notes, negative_notes, transition hints) — they are canon from that moment.
2. **Log the insertion** as its own decision id (`--decided-by` the Director) before generating anything.
3. **No storyboard page exists** for an inserted scene — it skips stage 8. The references block is built per d-127 from what IS attached (chain frame, character sheets, location plate); do not fabricate a page reference or borrow another scene's.
4. **Chain/hinge decision is explicit:** prefer chaining from the neighbor's approved last frame when the location and moment continue (S05B, S09A); use a generated/derived start frame or run frame-free only when the inserted scene breaks location. State the choice in the gate message.
5. The neighboring scenes' `transition_out_hint`/entry expectations may need touching — check the scene AFTER the insertion still cuts correctly from the new clip's ending, and flag any mismatch to the Director rather than silently regenerating.
6. Everything else is unchanged: cost preflight + announcement, per-clip Director gate (d-114), manifest recording, effects budget (max one impact move, never repeating a neighbor's).

## Generation, QC loop, gate

1. Preflight (`get_cost:true`), announce, generate via the model's MCP call. Poll `job_display` to completion; download; record `job_id`, `output_path`, actual cost in `generation_manifest`.
2. `qc-critic` scores the clip per `clip_qc_report` schema (identity/continuity/lipsync/prompt_adherence + artifacts_detected). Thresholds in `qc-critic.md`: identity ≥0.85, continuity ≥0.8, lipsync ≥0.8 (when applicable).
   **Zoom before you accuse (BINDING — the S04 lesson, 99cr):** never declare a wearable/prop/state violation from a downscaled contact-sheet frame. Crop-zoom the exact region at native resolution (ffmpeg crop on the extracted frame) and re-look before writing the finding. Straps, bands, wrist items and eyewear systematically misread at low resolution — this production logged two false alarms from small stills (S02 "wrist flip", S04 "goggle drift"), the second of which cost 99 credits of regens against a clip that was law-true. When the Director's read of the moving clip contradicts a still-frame finding, the moving clip at full resolution is the evidence that counts.
3. **REGENERATION IS DIRECTOR-GATED (BINDING — Director order d-114, supersedes the autonomous qa_loop):** QC findings — the EP's and the qc-critic's alike — are RECOMMENDATIONS presented at the clip gate, never triggers. After ONE generation, present the clip to the Director with the QC report (defects named, severity, proposed fix_directive) and STOP. The Director personally checks the clip; only their explicit instruction authorizes a regen attempt — and they may equally approve a clip QC flagged (their call outranks every threshold; record their pick and move on). Generating a second attempt on your own judgment cost 99 credits of unused clips on S04 — that is the failure mode this rule exists to prevent. The 3-attempt ceiling remains as an outer bound on Director-ORDERED regens, not a budget the EP may spend.
4. `--unit-done S{nn}_C{nn}` after each clip reaches `approved`. Write `generation_manifest.json` incrementally (archive before rewrite, validate before checkpoint).
5. Gate per clip (d-114 tightened this from per-scene-batch): checkpoint stays `in_progress`, but every generated clip goes to the Director with its QC summary + cost before ANY further generation — the next scene's clip included, since chained scenes consume the approved clip's last frame.

## Pitfalls

- Passing the raw storyboard panel (or the wrong frame_id) as `start_image` instead of its `promoted_media_id` — silently reintroduces the low-resolution/soft-detail problem the promotion pass exists to solve.
- Setting `end_image` from `shot_selection`'s `end_frame` role — that role is a future-phase audit record only (d-046); pinning it now risks the stiff "reaching for the pose" motion the Director explicitly ruled against.
- Trusting a remembered or skill-documented credit cost instead of a fresh `get_cost:true` preflight — costs vary by resolution/duration/model and have changed materially between sessions.
- Scaling to many scenes before confirming the batch cost against remaining balance — video generation costs 5–10x what storyboard generation did per unit.
- Dialogue scene assigned to a model without verified `policy.dialogue_scene_requires` capabilities — silent quality failure, not a hard error, so it must be checked explicitly per model entry.
- Treating the current no-cross-reference chaining method as settled — it is method (a) of five under ISSUE-008 evaluation, deferred to run after scene 4, not before.
