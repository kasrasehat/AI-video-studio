---
name: seedance-prompting
description: Prompt engineering for Seedance 2.0 — our primary video model (native voice + lipsync + reference conditioning, ≤15s clips, via Higgsfield MCP). Use when assembling any Seedance generation call (stage 9 prompt-smith), regenerating a failed clip, or auditing prompt quality.
---

# Seedance 2.0 Prompting

Seedance 2.0 (ByteDance) is this pipeline's default video model: single-pass native synced audio (speech + SFX + ambience), lipsync from quoted dialogue, multi-shot inside one generation, director-level camera control, and reference conditioning of up to **9 images + 3 video clips + 3 audio clips**. Max clip 15s (our scene unit), 4–15s range, aspects 21:9/16:9/9:16/4:3/1:1. Access is via the Higgsfield MCP (`skills/tech/higgsfield-mcp`); routing/capabilities live in `config/model_capabilities.yaml`.

## The prompt contract (200–400 words)

Seedance rewards structured density: 200–400 words, every one earning its place. Assemble in this order — it is the 5-aspect formula with Seedance's 8 components folded in:

1. **Format declaration (first line).** Declare the shot structure before any creative text: `Single continuous shot, medium close-up, slow dolly push-in, photorealistic, 35mm film grain.` — or for multi-beat scenes a shot-block plan (below). Never open with story prose.
2. **Subject** — every present character via their `lock_descriptors.identity_anchors` VERBATIM + this scene's outfit. Key objects with their anchors.
3. **Subject Motion** — action beats in temporal order, one beat per sentence. Use temporal markers on longer clips: `0–4s: … 4–9s: … 9–14s: …`. Strong specific verbs (darts, weaves, plants, spins); avoid generic ones (goes, moves, does).
4. **Dialogue** — `Name says: "line."` / `Name replies: "line."` exactly; mouth shapes key off the quoted strings. **≤6 words per line on fast cuts**; longer lines only on a close, calm, single-speaker framing. **One speaker at a time** — overlapping dialogue breaks sync. Delivery rides as a parenthetical: `Mira, worried, calls: "Kenji, wait — stay close!"`.
5. **Scene** — location via its anchors, time_of_day, weather/atmosphere with sensory detail (wet asphalt, lantern haze). One lighting idea, committed — never mix conflicting light ("bright noon" + "neon night").
6. **Spatial** — who is where in frame, facing which direction, FG/MG/BG layers, the 180° axis.
7. **Camera** — the direction's ONE move with speed and end state. Name primitives precisely (dolly/truck/pedestal = translation; pan/tilt/roll = rotation; zoom/rack focus = lens; static = strictly nothing). **State what the camera is NOT doing**: `no cuts, no zoom` on continuous shots — ambiguity is Seedance's main misfire.
8. **Style + Audio** — grade/era/grain per scene_direction global look; audio kept textural (`festival drums two streets over, crowd murmur`; diegetic foley like `sandals on stone`). Never request full music scores — scoring belongs to stage 10.

## Identity lock (BINDING — this is the consistency mechanism)

- Reference images: locked character sheet views (2–3 per present character, view matched to facing direction) + locked environment plate + selected storyboard frames. ≤9 total — prioritize present-character sheets first. Tag roles in the prompt: `[reference_image 1: Mira — character sheet, front view]`.
- Open the character block with an identity-lock block and stack the proven anti-drift phrases (redundancy measurably helps):
  `[identity_lock] The same character — straight black bob with blunt bangs, large dark-brown eyes, small mole under left eye — consistent across all shots, maintain exact appearance from reference image, no deformation, no face morph. Do not alter clothing category or primary color.`
- Add each character's `forbidden_drift` entries as explicit negatives.
- **Voice lock:** attach every speaker's locked voice sample as an audio reference (`reference_audio`) on EVERY clip where they speak. The quoted dialogue drives lips; the reference audio pins the voice. Never generate a speaking clip without it.

## Multi-shot inside one clip (use sparingly)

For montage-type scenes, explicit blocks: `Shot 1 (wide establishing, slow push-in, ~4s): … Shot 2 (medium close-up, static, ~5s): …` — ~2.5s minimum per shot, identity anchors re-stated verbatim in every block, subject transitions named with their cause ("revealed by camera movement"). Our default remains ONE idea per 15s scene; multi-shot only when the storyboard variant was designed that way.

## Params (via Higgsfield MCP — model id `seedance_2_0`, budget variant `seedance_2_0_mini`)

| Param | Use |
|---|---|
| duration | the scene's `est_duration_seconds` (4–15) |
| aspect_ratio | brief's `aspect_ratio_primary` (auto/16:9/9:16/4:3/3:4/1:1/21:9) |
| resolution + mode | finals: `1080p` (or `4k`) with `mode: std`; drafts: `720p` — or route to `seedance_2_0_mini` (480/720p only) |
| generate_audio | always true (native audio is the moat; independent of audio_references) |
| genre | optional cinematic hint (auto/action/horror/comedy/noir/drama/epic) — set from the brief's genre when it maps |
| bitrate_mode | `high` for the final pick of a scene, `standard` otherwise |
| medias[] roles | `start_image`, `end_image`, `image_references` (≤9 images total), `video_references` (≤3), `audio_references` = locked voice samples |
| get_cost | preflight `get_cost: true` before every batch and announce credits |

`mode: fast` / the mini variant trade camera-motion fidelity for cost — never use them for slow-mo, multi-shot, or dolly-heavy prompts; they are for blockout drafts and QC retries. Record every job_id (and seed, where returned) in `generation_manifest`.

## Anti-drift fallback ladder (when qc-critic returns regen for identity)

1. Re-emphasize the violated anchor at prompt start AND in the camera section; add the drift to negatives.
2. Add/replace a reference view matching the character's facing direction; cull references to the 3 most consistent rather than flooding all 9.
3. Shorten duration (10s → 6s) and simplify motion.
4. Escalate (bad start frame or impossible direction is upstream's problem — say so).

## Avoid table

| Don't | Why |
|---|---|
| 4+ simultaneous character actions | motion coherence breaks — split shots |
| Readable text/logos in-clip | unreliable rendering — captions belong to stage 10 |
| Two characters speaking in one breath | lipsync drift — alternate speaker beats |
| Emotional adjectives without visual cause | "sad" constrains nothing; "tears on cheek, shoulders slumped" renders |
| Names/pronouns as identity ("she", "the same girl") | the model never saw the cast list — anchors only |

<!-- adapted from OpenMontage seedance-2-0 pack + video-gen-prompting handbook (research extraction, 2026-07-09) -->
