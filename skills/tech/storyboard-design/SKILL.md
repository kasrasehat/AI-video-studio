---
name: storyboard-design
description: Storyboard frame design and prompting — static keyframes that video generation travels between, conditioned on locked assets. Use when generating storyboard variants in stage 8, designing start/end frames, or repairing a frame that drifted from its references.
---

# Storyboard Design

A storyboard frame here is not a sketch — it is a **generated still that may become a clip's start or end frame**. Design frames as conditioning material first, pretty pictures second.

## Frames are pure static snapshots (BINDING)

The #1 failure mode (independently discovered by two reference systems): frames described with motion. "He is about to stand up" is forbidden; "He sits, leaning slightly forward, hands braced on the table" is required. If you can't freeze it, it's not a frame — it's motion, and motion belongs to the clip prompt.

## Per scene: grid pages (Director method 2026-07-18, d-043/d-044 — supersedes per-frame counts)

A scene×variant is ONE generated image: a numbered GRID of sequential frames (uniform cells, thin gutters, small frame number per gutter corner, no other text). **TWO variant pages per scene** (A coverage-first, B energy-first). Grid size by BEAT COUNT — the number of distinct storyboard-able instants in the scene_direction blocking; duration alone never decides (a 14s held tableau with 4 beats is still 2×2):

| Beats in the scene | Grid | Frames on the page |
|---|---|---|
| **≤ 4** — one held idea, a handful of moments (~2–3.5s/panel) | 2×2 | 4 |
| **5–9** — entrances, reveals, multi-stage blocking | 3×3 | 9 |
| **10+** — continuous-motion set pieces where in-betweens matter (~0.6–1s/panel) | 4×4 | 16 |

**Panel durations (Director rule 2026-07-18):** every panel gets `duration_seconds` allocated from the scene_direction's rhythm (protected silences keep their full length); a scene's panel durations sum to its `est_duration_seconds`. Durations live in `storyboard_set.json` and gallery captions ONLY — never printed on the page image (pages are passed to the video model as references; text would poison conditioning).

**No end frames:** panel 1 is the scene's start-frame candidate; the LAST panel *describes* the ending (it must be the logical result of panel 1 + the directed motion) but is never promoted or pinned as an `end_image` in this pass — end-frame pinning is reserved for the post-project edit phase. First scene at a location: panel 1 is the widest framing the scene allows. After the cherry-pick, ONLY the start panel is PROMOTED: re-rendered full-frame as the scene's KEYFRAME (panel + locked refs as conditioning) — the promoted keyframe carries the media_id stage 9 uses — as a STYLE + COMPOSITION reference, not a start frame (d-203). Promotion is the STORYBOARD-ARTIST's job (same artist whose panel was picked, d-200), and the keyframe model is **Higgsfield Soul, cinema preset** ("Soul cinema", d-200) — pages board on gpt_image_2, keyframes render on Soul; verify catalog id/preset + `get_cost` before the first paid promotion call of a production.

## Frame prompt template

`<shot size + framing/approved FOV from scene_direction>. <Character(s) via identity_anchors VERBATIM + scene outfit/state, positions in frame, facing directions>. <Location via its anchors and foreground/midground/background map>. <Sourced lighting + time_of_day + optional white balance>. <Palette as material + light + role>. Static composition at one visible instant. Medium/style: <brief.visual_medium + approved global look>.`

- **Live-action/hybrid boards:** look like plausible photographed film frames, not animation concept art. Preserve natural facial asymmetry, living skin and eyes, material texture, contact shadows, optical depth, and physically credible environmental interaction. Use the discrete FOV chosen in scene_direction and do not add equipment/director names.
- **Animation boards:** retain the approved rendering language and established design anchors; do not import live-action skin/optics language unless the hybrid brief explicitly assigns it to that element.

- Conditioning references (record in `refs_used`): locked character sheet views (matched to facing direction) + locked environment plate. **Never generate a character or location from text alone.**
- Element→reference binding in the prompt: `Mira's appearance follows reference image 1 (character sheet). The lane follows reference image 3 (environment plate).`
- State element positions concretely ("Mira frame-left facing right, stall occupying right third") — the clip model will inherit whatever geography you establish here.

## Camera economy & continuity across frames

- **State-transition rule (Director rule 2026-07-19):** when a prop or wardrobe item is introduced, removed, or changed MID-SCENE (per `outfit_by_scene` / the object's scenes list), panel 1 must show the BEFORE state — identical to the previous scene's end state — and the change itself must happen in a visible panel. An item may never pop into existence between scenes or between panels. Before boarding any scene, diff its entry state against scene N−1's exit state (wardrobe, props, wet/dry, goggles) and board every difference as an on-screen beat.
- Reuse camera setups: within a scene, frames should come from as few camera positions as possible; a new angle needs a reason (the direction's move, a reveal).
- Respect the 180° axis established by scene_direction blocking; left/right positions must NOT flip between frames — a flipped axis in the storyboard becomes a flipped axis in the film.
- **Chain-by-reference (Director rule 2026-07-18):** at CHAINED boundaries (same location or continuous action per `transition_out_hint`), scene N's page generation passes scene N−1's PICKED page as an extra `image` reference with the prompt clause "PANEL 1 CONTINUES from the final panel of the reference storyboard page: same axis, same character state, compatible composition" — this requires generating scenes in order, each after the previous pick. At promotion, a chained scene's start frame is re-rendered conditioned on N−1's picked final panel + locked refs, so the cut lands seamlessly. At HARD HINGES (location changes) frame-chaining is impossible — carry state (wet/dry, goggles, bracelet) and motion direction (exit right → enter left) in the prompt instead.

## The 3-variant discipline (stage 8)

Variants A/B/C must be different INTERPRETATIONS, not rerolls — assign each a strategy before generating: e.g. A coverage-first (classical shot/reverse), B energy-first (one dynamic composition), C intimacy-first (close and held). Same direction, same locked refs, different visual thinking. The Director cherry-picks frames ACROSS variants, so every frame must stand alone: any variant's end frame may follow any variant's start frame — keep axis and palette compatible across variants of the same scene.

## Performance across panels (BINDING — Director order d-111)

A page is a performance, not a pose repeated N times. Each panel's prompt names what every visible character FEELS in that instant, taken from the direction's per-beat emotions — and those faces must CHANGE across the page as the scene's beats turn. Two adjacent panels showing a speaking character with the same expression is a boarding failure unless the direction explicitly holds that emotion. Board the listener's reactions as deliberately as the speaker's delivery: on dialogue beats, the panel's interest is often the face that ISN'T talking. Static composition stays law (a frozen panel can still hold a mid-laugh, a widening eye, a faltering grin) — freeze the emotion at its most legible instant.

## Frame self-QC (before presenting)

- Every present character's anchors visibly true (check against the locked sheet side-by-side).
- Positions/axis consistent with the direction's blocking and with sibling frames.
- Start-frame candidates: stable, geography-establishing, nothing mid-action. End-frame candidates: holdable, resolved.
- No readable text in frame; no borders/letterboxing (poisons i2v conditioning).
- **Faces move through the page (d-111):** expressions across panels trace the scene's emotional turns; no speaking character wears one face across the whole grid.

## V2 additions (Director passage 2026-07-30 — apply from production V2 onward; V1 rules above stay binding for V1)

Adopted from the Director's "AI Storyboard Prompt Builder" passage. These extend the V1 method; where the passage contradicted a V1 binding rule, the conflict is listed at the end for a joint Director decision, NOT silently applied.

1. **Per-panel spec, extended.** Every panel's description in the page prompt carries seven fields: panel number · **time position** (its start second within the scene, from the duration allocation — stated in the JSON artifact and the page prompt text, still never printed ON the image) · camera angle · main action · character expressions · important environment details · **emotional focus** (the one feeling this panel must transmit). V1 had the first five implicitly; time-position and emotional-focus are now explicit slots.
2. **Shot-type mixing, reconciled with camera economy.** Draw from the full menu — wide, medium, close-up, low angle, high angle, over-the-shoulder, dynamic action — and avoid repeating the same composition in consecutive panels **when the beat motivates a change**. The V1 economy rule still governs: a new angle needs a reason; the menu tells you what to reach for when the reason exists (a reveal, a reaction, a scale gag), not license to reroll angles per panel.
3. **Whole-story pre-board (NEW V2 artifact, optional).** Before per-scene pages, one 3×5 (15-panel) single-image board of the ENTIRE film — introduction, inciting event, rising action, emotional moments, climax, ending — cinematic 16:9 panels, conditioned on the locked sheets. Used at the story/direction gates as a cheap whole-arc visualization; per-scene pages remain the video-conditioning authority.
4. **One continuous page prompt + declared assumptions.** The page prompt is ONE polished continuous prompt (never per-panel fragments stitched loosely), and any assumption made about style or missing detail is stated to the Director alongside the generation — not silently embedded.
5. **Story auto-expansion guard.** If a scene's direction under-specifies beats for its grid size, expand from the scene's dramatic function (never invent plot) and DECLARE the expansion at the gate.
6. **Character-analysis preamble.** Before boarding, restate each present character's identity from the locked sheet in short form inside the page prompt (the passage's "short but detailed character descriptions") — V1 already does this via identity_anchors; V2 keeps anchors verbatim AND binds each to its reference image number.

### V2 conflict rulings (Director, 2026-07-30 — d-143; BINDING for V2)
- **A — On-page text ban REVOKED for V2.** Storyboard pages MAY carry timeline indicators and small production notes (the passage's sheet design). The V1 rationale is retained as a caveat, not a law: on-page text risks poisoning i2v conditioning — if V2 clips start reproducing board text or adherence degrades, the documented fallback is two renders per page (annotated presentation copy + clean conditioning copy), subject to a new Director ruling. V1 pages are untouched.
- **B — Default grid is 3×5, 15 panels (V2).** The Director prefers the passage's 15-panel 3×5 layout as the storyboard default. **The superseded V1 setting is logged here VERBATIM for exact restoration on a future Director order** — V1 sized grids per scene by BEAT COUNT, duration never deciding: ≤4 beats → 2×2 grid (4 frames, ~2–3.5s/panel) · 5–9 beats → 3×3 (9 frames) · 10+ beats → 4×4 (16 frames, ~0.6–1s/panel); panel durations allocated from the scene_direction rhythm and summing to `est_duration_seconds`. To restore, reinstate that table as the default and demote 3×5 to the whole-story pre-board only.
- **C — Sheet annotations: V1 approved and kept.** Character/location sheets continue to carry small text annotations exactly per the V1 spec; the passage's no-label rule is NOT adopted for sheets.

<!-- method adapted from ViMax two-prompt decomposition + variation taxonomy (MIT) and OpenMontage 5-aspect hero-frame rules, research extraction 2026-07-09; V2 additions from the Director's Character Turnaround / Storyboard Prompt Builder passage, 2026-07-30 -->
