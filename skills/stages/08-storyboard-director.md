# Storyboard Director — stage 8

Generate THREE genuinely different storyboard interpretations per scene — every frame a potential clip start/end frame conditioned on locked assets — then run the Director's cross-variant cherry-pick gate.

**Consumes:** `asset_manifest` (locked elements ONLY), `scene_direction`, `lock_descriptors`, `scene_list`.
**Produces:** `artifacts/storyboard_set.json` + (at the gate) `artifacts/shot_selection.json`.
**Gate:** the Director cherry-picks frames ACROSS variants (cuts 1–2 from A, 3 from C is first-class). **Resume unit:** `scene_variant` (`S07_B` done = never redo).

## Before anything

Read `skills/tech/storyboard-design` (frame rules — static snapshots, template, axis law, chaining), `skills/tech/higgsfield-mcp` (media flow, cost preflight), `skills/tech/storyboard-qc` (the mechanical self-QC procedure — panel-splitting and camera-lock diff tooling, the defect taxonomy, exact MCP call shapes — BINDING before you present any page), `skills/meta/consistency-guard.md`. Frames carry no text, so the sheet-text ban on nano-banana does NOT apply here.

## Grid storyboard pages (Director method, binding — d-043)

A scene×variant is ONE generated image: a storyboard PAGE containing the scene's sequential frames as a uniform grid, read left-to-right, top-to-bottom. **Default model: `gpt_image_2`** (layout control is the whole job here), quality high, 2k, 16:9.

0b. **Panels board the SHOT PLAN (d-201):** scene_direction now designs scenes as multi-shot cut sequences by default. Every CUT in the shot plan begins a new panel, and the double contrast must be visible across those panels (shot size and camera character both change); beats within one shot may add further panels. Panel 1 remains the start-frame candidate of the FIRST shot (the chaining anchor).
1. Classify each scene by **BEAT COUNT** (distinct storyboard-able instants in the scene_direction blocking — shots count as at least one beat each; duration alone never decides):
   - **≤ 4 beats** (one held idea) → **2×2 grid = 4 sequential frames**
   - **5–9 beats** (entrances, reveals, multi-stage blocking) → **3×3 = 9 frames**
   - **10+ beats** (continuous-motion set pieces where in-betweens matter) → **4×4 = 16 frames**
2. Panel discipline: uniform cells, thin clean gutters, a small frame number in each gutter corner (panels are cited at the gate as "S07 B panel 7"); NO other text, no captions inside panels. Every panel is itself a frozen static composition obeying the frame rules below; the panel sequence tells the scene's beats in order; panel 1 = the start-frame candidate; the LAST panel describes the scene's ending (never promoted or pinned as an end_image in this pass — reserved for the future edit phase).
3. **Author panel durations**: allocate `duration_seconds` per panel from the direction's rhythm (protected silences keep full length); panel durations sum to the scene's `est_duration_seconds`. Durations go in `storyboard_set.json` + gallery captions only — never onto the page image.
4. **Chain-by-reference**: at chained boundaries (same location / continuous action per `transition_out_hint`), scene N's generation call ALSO passes scene N−1's PICKED page in `medias` (role `image`) plus the clause "PANEL 1 CONTINUES from the final panel of the reference storyboard page: same axis, same character state, compatible composition." Hard hinges (location changes) instead carry state + motion direction in the prompt. Generate scenes in order, each after the previous pick.
4b. **State transitions on screen**: diff scene N's entry state against N−1's exit state (wardrobe, props, wet/dry, goggles, per `outfit_by_scene` + object scene lists). Panel 1 always shows the BEFORE state; any mid-scene introduction/change (a bracelet strapped on, goggles snapped down) is boarded as its own visible beat — nothing pops into existence between scenes or panels.
4c. **Unsatisfiable-brief escalation (d-084)**: before any artist generates, the direction's trajectories are traced against the location's locked geography (source → path → target in screen space). Contradictory constraints — a stated crossing path whose endpoints sit on the same side, an entering object with no established source — HALT the scene: the artist reports the conflicting clauses to the EP, the EP escalates to the Director for a direction amendment, and only then does boarding resume. Silently picking which half of a contradiction to violate is forbidden (it cost S14 a full 28-credit round, d-082).
5. Present the full plan (grid size per scene, image count, credits) to the Director and get explicit approval BEFORE the first paid call. Model choice is a Director decision — log it.
6. **Promotion step (after the cherry-pick) — KEYFRAMES, artist-owned (d-200):** grid panels are selection artifacts, too small for direct i2v conditioning. ONLY the picked START panel per scene is promoted: cropped and re-rendered as ONE full-frame KEYFRAME (locked refs + the cropped panel as an additional reference, "recreate this exact composition full-frame"; for chained scenes also conditioned on N−1's picked final panel). **The keyframe is generated by the SAME storyboard-artist whose panel was picked** — promotion is part of the artist's job, briefed in their assignment, not a separate EP pass; the EP still independently verifies every keyframe before registration. **Keyframe model = Higgsfield Soul, cinema preset ("Soul cinema", Director order d-200)** — grid PAGES stay on `gpt_image_2` (layout control), keyframes switch to Soul for cinematic single-frame quality. Before the FIRST paid promotion call of a production: confirm the exact catalog id/params (`models_explore action=list type=image` → soul model; `presets_show` for the cinema style) and preflight cost (`get_cost:true`), then Director-gate the batch (d-114). Promoted keyframes carry the media_ids stage 9 conditions on; stage 9 additionally passes the picked PAGE itself as an image_reference. Announce promotion cost separately at the gate.

## Variant strategies (BINDING — Director rule d-044: TWO pages per scene)

- **A — coverage-first:** classical framing per the scene_direction as written; the safe master interpretation.
- **B — energy-first:** one bolder compositional idea (deeper diagonal, stronger foreground, more dynamic framing, or intimacy where the scene is quiet) that still obeys the direction's camera law and axis.

Same direction, same locked refs, same axis, same palette — different visual thinking, never a reroll. Any variant's panels must be able to mix with the other's (the Director cherry-picks across A and B), so axis and palette stay compatible.

## Generation rules (binding)

1. **Model default: `nano_banana_pro`** (multi-image refs, strong character adherence, 2k, ~2 cr/frame). `gpt_image_2` is the premium fallback for frames that keep failing anchors.
2. **Never from text alone.** Every frame passes as `medias` (role `image`): the locked sheet of every present character + the scene's locked location sheet (media_ids from `asset_manifest`). Record their element_ids in `refs_used`.
3. **Prompt per the template** in storyboard-design: shot framing from scene_direction (verbatim where possible) + characters via identity_anchors VERBATIM + outfit/state for THIS scene (goggle law, wet/dry law, bracelet wrist) + location anchors + relative-position map facts for on-screen geography + lighting per direction + palette hexes + "Static composition, no motion blur. Stylized 3D Pixar-like family film." + explicit element→reference binding ("Gramps follows reference image 1; the cavern follows reference image 3").
4. **Freeze it.** No "about to", no mid-air unless the direction freezes mid-air as the composition. State every element's frame position and facing.
5. **16:9, no borders, no letterboxing, no readable text in frame** (poisons i2v conditioning).
6. Aspect/cost preflight per batch (`get_cost:true`) → announce → generate. Record model, full prompt, job_id as `media_id`, cost per frame. Files: `assets/storyboards/<frame_id>.png` (`S07_B_F01.png`).
7. `--unit-done <scene>_<variant>` after each scene×variant lands; write `storyboard_set.json` incrementally (archive before rewrite, validate before checkpoint).

## Self-QC before presenting (per frame)

- Anchors of every present character visibly true vs their locked sheet; location fixtures where the relative-position map puts them; axis matches the direction's blocking (left/right NEVER flipped).
- Goggle law / wet-dry law / bracelet wrist correct for THIS scene.
- Start candidates: stable, geography-establishing. End candidates: holdable, resolved, the logical result of start + directed motion.
- Chained pairs actually chain (compare side by side).
- **Regen budget (Director rule d-057): ONE self-QC regeneration per page, maximum.** If the regen still fails QC, STOP — present the page at the gate with the defect disclosed; further fixes are Director-ordered manual edits (image-editor skill), never more silent regens. Log every regen.
- **Run the mechanical procedure, not a visual skim:** `skills/tech/storyboard-qc` is BINDING — split the page into per-panel crops, check each against the defect taxonomy, and `diff` any two panels the direction requires to share a camera setup, before presenting. Camera-continuity breaks (taxonomy class D) are invisible on a skim of the full grid and were the direct cause of two Director-facing defects (d-070, d-072).

## The cherry-pick gate

1. Rebuild gallery: `python scripts/review_gallery.py <slug> --source storyboard_set` → per-scene A/B/C rows.
2. Checkpoint `awaiting_human`; present per scene: the 3 approach notes + frame paths, flagged start/end candidates, cost so far. END TURN.
3. On picks: write `shot_selection.json` (selected_frames with variant_id, frame_id, order, role; rationale in the Director's words), validate, log a `shot_selection` decision per scene (`--decided-by user`). Unpicked frames stay in storyboard_set (audit trail), never referenced downstream.
4. Partial picks fine — lock picked scenes, iterate the rest (revisions count against `max_revisions_per_stage`).
5. All scenes selected → `--status completed --approved` with both artifacts attached; proceed to stage 9.

## Pitfalls

- 3 rerolls instead of 3 interpretations (assign strategies FIRST).
- Motion language in frame prompts; frames that can't hold as a still.
- Axis flips between variants (kills cross-variant mixing) or across a chained pair.
- Forgetting a present character's sheet in medias (drift) or exceeding the model's reference budget (prioritize: location sheet + speaking/foreground characters).
- Wrong per-scene state: goggles, wetness, bracelet readout, dog asleep-vs-one-eye.
