---
name: seedance-prompting
description: Prompt engineering for Seedance 2.0 — our primary video model (native voice + lipsync + reference conditioning, ≤15s clips, via Higgsfield MCP). Use when assembling any Seedance generation call (stage 9 prompt-smith), regenerating a failed clip, or auditing prompt quality.
---

# Seedance 2.0 Prompting

Seedance 2.0 (ByteDance) is this pipeline's default video model: single-pass native synced audio (speech + SFX + ambience), lipsync from quoted dialogue, multi-shot inside one generation, director-level camera control, and reference conditioning of up to **9 images + 3 video clips + 3 audio clips**. Max clip 15s (our scene unit), 4–15s range, aspects 21:9/16:9/9:16/4:3/1:1. Access is via the Higgsfield MCP (`skills/tech/higgsfield-mcp`); routing/capabilities live in `config/model_capabilities.yaml`.

## The prompt contract (200–1000 words — Director order 2026-07-29, raised from 200–400)

Seedance rewards structured density: 200–1000 words, every one earning its place. The raised ceiling buys room for the reference blocks, per-beat state restatement and performance layers the binding rules require — it is NOT license for padding: stop when every law is stated once per beat. Assemble in this order — it is the 5-aspect formula with Seedance's 8 components folded in:

1. **Format declaration (first line).** Declare the shot structure before any creative text: `Single continuous shot, medium close-up, slow dolly push-in, photorealistic, 35mm film grain.` — or for multi-beat scenes a shot-block plan (below). Never open with story prose.
2. **Subject** — every present character via their `lock_descriptors.identity_anchors` VERBATIM + this scene's outfit. Key objects with their anchors.
3. **Subject Motion** — action beats in temporal order, one beat per sentence. Use temporal markers on longer clips: `0–4s: … 4–9s: … 9–14s: …`. Strong specific verbs (darts, weaves, plants, spins); avoid generic ones (goes, moves, does). **Every temporal beat names each visible character's FACE (Director order d-111)** — the emotion at that instant and where it turns (`2–4s: Milo's grin falters into wide-eyed doubt as…`). Faces that change across the clip are the cheapest engagement multiplier the prompt controls; a clip whose characters hold one expression start-to-finish is a flat clip regardless of action.
4. **Dialogue** — `Name says: "line."` / `Name replies: "line."` exactly; mouth shapes key off the quoted strings. **≤6 words per line on fast cuts**; longer lines only on a close, calm, single-speaker framing. **One speaker at a time** — overlapping dialogue breaks sync. Delivery rides as a parenthetical: `Mira, worried, calls: "Kenji, wait — stay close!"`. **Direct the listener too (d-111):** on every line, state the non-speaker's visible reaction (`Gramps' eyebrows climb; he bites back a smile`) — the cutaway face sells the exchange, and Seedance animates reactions only if the prompt asks for them.
5. **Scene** — location via its anchors, time_of_day, weather/atmosphere with sensory detail (wet asphalt, lantern haze). One lighting idea, committed — never mix conflicting light ("bright noon" + "neon night").
6. **Spatial** — who is where in frame, facing which direction, FG/MG/BG layers, the 180° axis.
7. **Camera** — the direction's ONE move with speed and end state. Name primitives precisely (dolly/truck/pedestal = translation; pan/tilt/roll = rotation; zoom/rack focus = lens; static = strictly nothing). **State what the camera is NOT doing**: `no cuts, no zoom` on continuous shots — ambiguity is Seedance's main misfire.
   **Emotional beats earn camera freedom (Director ruling d-118).** An absolute static lock fights the model's cinematic instincts exactly where they're best: on S06, Seedance broke a hard "the frame must not move" to push into a close two-shot for a whispered line — and the Director judged the result BETTER than the boarded stillness ("gives more freedom and transfers emotion better than static"). The rule now: static-locked framing remains the default for staging clarity, but when a scene lands on an emotional peak, either DIRECT the move explicitly ("the camera eases slowly closer as the line lands, settling in a close two-shot") or grant room for it ("the camera may drift gently toward the faces on the final beat"). Reserve absolute no-move language for shots where stillness IS the storytelling (the S01 tabletop-magic shrink) — and say why in the prompt, which the model respects far more than a bare prohibition.
8. **Style + Audio** — grade/era/grain per scene_direction global look; audio kept textural (`festival drums two streets over, crowd murmur`; diegetic foley like `sandals on stone`). Never request full music scores — scoring belongs to stage 10.
   **The clip's baked audio IS the film's SFX track (BINDING — d-160):** every sound the scene needs (foley, ambience, directed effects like a heartbeat or a fridge hum) must be asked for HERE, in the prompt, from `sound_direction` — Seedance bakes it and stage 10 will NOT add it later. Post-audio never re-adds a sound class the prompt requested: a separately-mixed heartbeat bed doubled the clips' own baked heartbeats in this pipeline's first production and degraded the mix. If a directed sound spans a CUT into the next scene (continuity bed), still prompt it in BOTH clips consistently (same rate/character stated identically) — cross-cut consistency comes from consistent prompts, not from a post overlay.

## Negative prompts are unreliable (BINDING — d-099, confirmed empirically)

Seedance does not reliably honor "no X" / "zero X" / "without X" clauses — a negative is a much weaker signal to the model than a positive, concrete description of the desired state. Confirmed on S01_C01: "zero smoke, zero haze, zero ember, nothing lingering in the air" was added explicitly after attempt 1 showed a smoke wisp, and attempt 2 rendered MORE smoke, not less, despite the strengthened negative.

**Write every constraint as what SHOULD be on screen, not what must be absent:**
- Bad: `no smoke, no haze, no scorch marks`
- Better: `the beam ends in a single bright flash; the instant it fades, the apple sits pea-sized in perfectly clear, still air`
- Bad: `no camera movement, no pan, no zoom, no shake`
- Good (keep this one — camera primitives are a documented exception, see component 7 above): naming what the camera is NOT doing works for CAMERA MOVEMENT specifically, because Seedance treats camera primitives as a distinct instruction channel from scene content. Negatives about physical scene content (smoke, props, wardrobe, weather) are the unreliable case.
- Reference-image conflicts are a SEPARATE failure mode from this one and need a different fix: if a locked reference image itself shows the thing being negated (e.g. a character sheet depicting an accessory the scene says is absent), no amount of prompt wording — positive or negative — reliably overrides it. See `skills/tech/character-sheets/SKILL.md`'s scene-conditional-accessories rule (d-098): fix the reference, not the words, when the conflict is visual.
- On a `qc-critic` regen for a physical-content violation (smoke, debris, wrong prop, wrong material state): the `fix_directive` should propose a positive rewrite first, and only fall back to a stronger negative if no positive phrasing captures the constraint. If the defect persists after a positive rewrite, treat it as a possible model limitation for that effect and escalate rather than iterating on negative wording indefinitely.

## Impact moves — the special-effects vocabulary (Director order d-120)

Seedance executes in-camera effects well when they're directed as ONE named event, and they hit hardest when they're rare. The proven vocabulary:
- **Speed ramp** — real-time ramping smoothly into super slow motion for one held close-up, then snapping back HARD and instantly (the S05A bubble beat; the reference-prompt butterfly). Always: one ramp, a named subject for the slow beat, an instant (never gradual) return.
- **Freeze-and-orbit** — time stops entirely mid-action; the camera sweeps a smooth arc around the suspended subjects while particles (droplets, crumbs, sparks) hang crisp and individually readable; then time snaps back (the S05B frozen fall). Direct the frozen expressions explicitly — they're locked for the whole orbit.
- **Masked reframe** — a whiteout/flash/occlusion fills the frame and hides a full camera repositioning inside one continuous clip (the S03 shrink hinge, the boarded S15 FOOM).
- **Motivated emotional drift** — the d-118 push-in: the camera eases closer as an emotional beat lands (the S06 whisper).
- **Rear chase lock** — the camera rides the subject's tail through an action sequence, world rushing past (the S05A ride, from the Director's reference).

**The budget rule (BINDING): impact moves are spent, not sprinkled.** At most ONE per scene, reserved for the scene's peak moment, and neighboring scenes should not repeat the same move — a film that freezes time twice in three minutes has taught the audience the trick and lost it. The director role picks the moment; the prompt names exactly one effect and states its boundaries (what starts it, what ends it, what must stay crisp).

## Named @asset handles (Director order d-120 — extends the d-106 @-mention rule)

Asset names start with @ — that's the hook that pulls them straight into a prompt later. Beyond positional `@reference_image_N` tags, define memorable HANDLES for the production's recurring assets and bind each handle to its reference once in the references block, then use the handle everywhere:

```
ACTIVE REFERENCES
@gramps: reference image 2 — his character sheet; 100% match, identical design every frame.
@milo: reference image 3 — his character sheet; 100% match, same boy throughout.
@cookie-sled: the bitten cookie chunk they ride; keeps its shape every frame.
@stomach-cavern: reference image 4 — the location plate; the room must match it.
```

Then inline: `@gramps kneels at the rear, @milo up front`, `the camera orbits @milo and @gramps`, `the reveal matches @stomach-cavern`. Handles make long prompts readable, keep every mention consistently bound to its reference, and let a scene's cast be swapped by editing one block. Production handles are stable across scenes — reuse the same handle names film-wide so prompts can be assembled from parts.

## Similes and metaphors literalize (BINDING — confirmed twice)

Seedance renders comparisons as literal objects. "Dust motes drift overhead **like slow planets**" produced a banded Jupiter floating in the garage (S03); "inside the glass is a liquid amber **cathedral**" produced an actual gothic church interior with arched windows submerged in the lemonade (S05). Scene-direction prose is written for humans and full of these figures — NEVER carry them verbatim into a generation prompt. Translate every simile/metaphor into direct visual description before it ships: "sun refracting through the lemonade in tall shafts, bubbles as drifting gold sparks" renders the intended image; naming the thing it resembles renders the thing itself.

## Identity lock (BINDING — this is the consistency mechanism)

- Reference images: locked character sheet views (2–3 per present character, view matched to facing direction) + locked environment plate + selected storyboard frames. ≤9 total — prioritize present-character sheets first.
- **@-mention every reference in the prompt body (BINDING — Director order 2026-07-22, d-106).** Attaching an image without naming it in the text leaves the model to guess what each picture is for — confirmed on S03_C01 attempts 1–3, where the picked storyboard page rode along unlabeled among five images and the model ignored its staging entirely while following the prompt's prose instead. The fix: open the prompt with a references block that maps every attached image by its position in the medias array, then @-mention them inline wherever the element they depict is described:
  - `References: @reference_image_1 is this shot's start frame — begin on exactly this image. @reference_image_2 is the storyboard page for this scene — its numbered panels are the authoritative staging, composition and object scale for every beat. @reference_image_3 is Gramps' character sheet. …`
  - Inline: `GRAMPS (@reference_image_3): white walrus mustache…`, `the garage of @reference_image_5, staged exactly as drawn in @reference_image_2`.
  - Numbering = the order images are passed in `medias` (start_image first, then image_references in order). A mismatch between the block and the array silently mislabels every reference — verify the mapping against the actual call before submitting.
  - The storyboard page's @-mention must state its authority explicitly ("authoritative staging/composition/scale — match it"), not merely name it.
  - **When a clip has NO start frame (d-127):** `@reference_image_1` is then the FIRST image in `medias` — usually the storyboard page. The references block is ALWAYS derived from the actual medias array of the call being submitted, never copied from another scene's prompt or a template: with a start frame the numbering begins at it; without one, every number shifts down by one, and a copied block silently mislabels EVERY reference (expensive to debug — the failure looks like random non-adherence). Mandatory pre-submit check: list the medias array in order, write one line per entry (`position → role → what the file is → @tag used in prompt`), and only then finalize the block. If any attached media has no @tag, or any @tag has no attached media, do not submit.
  - **NO reference may be left unnamed — the start frame included (Director order 2026-07-26, d-124; confirmed on S07_C01 attempt 1).** Passing `start_image` in the medias while giving @-numbers only to the other references broke the chain: the start frame was attached but referred to as just "the provided start frame", and the motion text opened on a different composition — the model followed the prose and discarded the frame entirely (126cr lost). Binding rules: (a) the start frame is ALWAYS `@reference_image_1`, described by content: `@reference_image_1 is this shot's start frame — begin on exactly this image (<what it shows>)`; (b) the 0–2s beat must be written as a BRIDGE from the start frame's actual composition to the scene's staging — never open the motion on a composition that contradicts the start frame, because when prose and an attached image disagree, the prose wins and the chain breaks.
- Open the character block with an identity-lock block and stack the proven anti-drift phrases (redundancy measurably helps):
  `[identity_lock] The same character — straight black bob with blunt bangs, large dark-brown eyes, small mole under left eye — consistent across all shots, maintain exact appearance from reference image, no deformation, no face morph. Do not alter clothing category or primary color.`
- Add each character's `forbidden_drift` entries as explicit negatives.
- **Voice lock:** attach every speaker's locked voice sample as an audio reference (`reference_audio`) on EVERY clip where they speak. The quoted dialogue drives lips; the reference audio pins the voice. Never generate a speaking clip without it.

## Multi-shot inside one clip (use sparingly)

For montage-type scenes, explicit blocks: `Shot 1 (wide establishing, slow push-in, ~4s): … Shot 2 (medium close-up, static, ~5s): …` — ~2.5s minimum per shot, identity anchors re-stated verbatim in every block, subject transitions named with their cause ("revealed by camera movement"). Our default remains ONE idea per 15s scene; multi-shot only when the storyboard variant was designed that way.

## Handoff beat (BINDING — d-191, audience feedback: visible cuts between clips)

Chained clips share a start FRAME (d-112) but audiences see a jump when they don't share MOTION. Every prompt therefore books its last ~1–1.5s as an explicit **handoff beat**, and every chained successor's 0–2s bridge (d-124) continues it:

- **Outgoing clip, final beat:** either (a) the action DECELERATES into a describable settle — name the exact end pose, gaze direction, and any residual motion ("Milo lands the jump and holds, knees still flexed, cape settling, eyes frame-right"), or (b) for boundaries the direction marks continuous, name the exact motion state crossing the cut — what is moving, screen direction, energy ("still sliding left-to-right at full speed as the clip ends").
- **Incoming chained clip, 0–2s bridge:** restate the start frame content per d-124 AND the inherited motion — the first beat continues it before anything new happens ("continuing the left-to-right slide from the opening frame, he decelerates as…"). A bridge that poses a moving character static is how seams become visible.
- The `transition_out` in scene_direction (stage-5 boundary motion contract, d-191) is the source of truth for which mode each boundary uses; the prompt-writer copies it, never invents it.
- End-frame pins (`end_image`) remain the strongest handoff for hard choreography — when one exists, the handoff beat describes THAT frame.

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
| `end_image` caveat | **Steers, doesn't lock (confirmed S05B):** the clip arrived at the target's CONTENT (same location, same event, same palette) but not its framing — the final frame was a closer composition than the pinned image. Treat `end_image` as a strong destination hint; if a frame-exact join matters, plan to trim the tail or cut on action instead. `start_image` remains pixel-exact. |
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
