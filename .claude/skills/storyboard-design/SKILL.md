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

**No end frames:** panel 1 is the scene's start-frame candidate; the LAST panel *describes* the ending (it must be the logical result of panel 1 + the directed motion) but is never promoted or pinned as an `end_image` in this pass — end-frame pinning is reserved for the post-project edit phase. First scene at a location: panel 1 is the widest framing the scene allows. After the cherry-pick, ONLY the start panel is PROMOTED: re-rendered full-frame (panel + locked refs as conditioning) — the promoted start frame carries the media_id stage 9 uses.

## Frame prompt template

`<shot size + framing from scene_direction>. <Character(s) via identity_anchors VERBATIM + scene outfit, positions in frame, facing directions>. <Location via its anchors>. <Lighting per direction + time_of_day>. <Palette>. Static composition, no motion blur. Style: <global look>.`

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

<!-- method adapted from ViMax two-prompt decomposition + variation taxonomy (MIT) and OpenMontage 5-aspect hero-frame rules, research extraction 2026-07-09 -->
