---
name: storyboard-design
description: Storyboard frame design and prompting — static keyframes that video generation travels between, conditioned on locked assets. Use when generating storyboard variants in stage 8, designing start/end frames, or repairing a frame that drifted from its references.
---

# Storyboard Design

A storyboard frame here is not a sketch — it is a **generated still that may become a clip's start or end frame**. Design frames as conditioning material first, pretty pictures second.

## Frames are pure static snapshots (BINDING)

The #1 failure mode (independently discovered by two reference systems): frames described with motion. "He is about to stand up" is forbidden; "He sits, leaning slightly forward, hands braced on the table" is required. If you can't freeze it, it's not a frame — it's motion, and motion belongs to the clip prompt.

## Per scene: how many frames, which roles

Decide by how much the composition changes across the scene (the variation taxonomy):

| Scene's visual change | Frames | Roles |
|---|---|---|
| **small** — expression/pose/walk change, moderate camera move | 1–2 | one start_frame candidate; i2v carries the rest |
| **medium** — a character enters, someone turns from back to front | 2–3 | start + end candidates |
| **large** — composition/framing changes dramatically (wide→close) | 3–4 | start + end + a mid_reference |

The END frame must be the logical result of the start frame + the directed motion — check this explicitly. First scene at a location: the widest framing that scene allows (establishes geography for every later scene there).

## Frame prompt template

`<shot size + framing from scene_direction>. <Character(s) via identity_anchors VERBATIM + scene outfit, positions in frame, facing directions>. <Location via its anchors>. <Lighting per direction + time_of_day>. <Palette>. Static composition, no motion blur. Style: <global look>.`

- Conditioning references (record in `refs_used`): locked character sheet views (matched to facing direction) + locked environment plate. **Never generate a character or location from text alone.**
- Element→reference binding in the prompt: `Mira's appearance follows reference image 1 (character sheet). The lane follows reference image 3 (environment plate).`
- State element positions concretely ("Mira frame-left facing right, stall occupying right third") — the clip model will inherit whatever geography you establish here.

## Camera economy & continuity across frames

- Reuse camera setups: within a scene, frames should come from as few camera positions as possible; a new angle needs a reason (the direction's move, a reveal).
- Respect the 180° axis established by scene_direction blocking; left/right positions must NOT flip between frames — a flipped axis in the storyboard becomes a flipped axis in the film.
- **Chaining rule:** where the direction implies continuity into the next scene (match_cut, continuous action), design this scene's end frame and the next scene's start frame as a pair (same axis, compatible composition).

## The 3-variant discipline (stage 8)

Variants A/B/C must be different INTERPRETATIONS, not rerolls — assign each a strategy before generating: e.g. A coverage-first (classical shot/reverse), B energy-first (one dynamic composition), C intimacy-first (close and held). Same direction, same locked refs, different visual thinking. The Director cherry-picks frames ACROSS variants, so every frame must stand alone: any variant's end frame may follow any variant's start frame — keep axis and palette compatible across variants of the same scene.

## Frame self-QC (before presenting)

- Every present character's anchors visibly true (check against the locked sheet side-by-side).
- Positions/axis consistent with the direction's blocking and with sibling frames.
- Start-frame candidates: stable, geography-establishing, nothing mid-action. End-frame candidates: holdable, resolved.
- No readable text in frame; no borders/letterboxing (poisons i2v conditioning).

<!-- method adapted from ViMax two-prompt decomposition + variation taxonomy (MIT) and OpenMontage 5-aspect hero-frame rules, research extraction 2026-07-09 -->
