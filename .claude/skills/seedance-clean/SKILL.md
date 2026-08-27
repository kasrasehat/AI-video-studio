---
name: seedance-clean
description: >
  Write production-ready Seedance 2.0/2.5 prompts for live-action or hybrid
  cinematic shots. Use for standalone Seedance prompt requests and for stage 9
  when brief.visual_medium is live_action or hybrid. Do not use for animation
  projects, which route to seedance-prompting.
---

# Seedance Clean — Live-Action Prompt Writer

Turn a script beat, scene, or shot idea into one sealed Seedance prompt. Block,
light, pace, and constrain the shot as observable live-action cinema.

For a direct prompt-writing request, return **one standalone English prompt in
one code block and nothing else**. Inside this repository's stage-9 workflow,
write that same standalone text into the `generation_manifest.clips[].prompt`
field; the clip-producer owns the surrounding JSON and generation call.

## Routing and precedence

- Use this profile when `brief.visual_medium` is `live_action` or `hybrid`.
- Use `skills/tech/seedance-prompting/SKILL.md` when it is `animation`.
- For an older brief without `visual_medium`, route obvious photoreal/live-action
  styles here and obvious animated/illustrated styles to `seedance-prompting`.
  Stop for a Director decision when the style is ambiguous.
- Project laws still bind: locked assets only, identity anchors verbatim,
  reference/audio threading, continuity fields, paid-call gates, and exact
  dialogue. This skill controls prompt form and live-action craft.
- User-supplied prompt text or blocks are preserved verbatim unless they conflict
  with a locked artifact or an explicit safety/production constraint.

## Core principle: write the visible

Seedance reacts to what can be seen, heard, and measured, not mood labels.
Translate abstractions into physical evidence:

- `tense scene` → `he freezes, slowly clenches his fist; side light leaves half
  his face in shadow`
- `epic fast car shot` → `low tracking shot beside the car through a wet curve;
  headlights glow, tyre spray crosses frame, the camera takes short buffeting
  impacts`

Use plain instruction-style language. Before returning, mentally watch the
prompt: the first frame is occupied, geography and eyelines are clear, the light
has a source, subject and camera motion are distinct, and the ending is visible.

## Workflow

1. Read as a director: identify where the beat turns, lands, and breathes.
2. Resolve gaps that materially change blocking, first frame, angle, light,
   timing, performance, or ending. In a gated production, surface the gap rather
   than inventing against an approved artifact.
3. Define continuity anchors: present people, appearance, wardrobe, carried
   state, props, geography, light, weather, and emotional carry.
4. Choose the least rigid format mode that still lands the required beats.
5. Write only the blocks the shot earns, in the canonical order below.
6. Build a two-way asset map and verify every attached asset is tagged exactly
   once and every tag refers to an attached asset.
7. Run the checklist before returning or submitting.

## Asset tagging

A reference sets appearance and identity; text sets action and critical state.
Both are required.

- Preserve user-specified tags such as `@tag_name`.
- Otherwise tag by actual load order: `@image1`, `@image2`, `@video1`, and
  `@audio1`.
- Repository media-array aliases such as `@reference_image_1` are permitted when
  they exactly match the submitted array. Never copy numbering from another
  shot.
- Include a tag only where that asset is present. Do not feed or mention unused
  people, props, or prior-scene material.
- State critical small text, logos, colors, damage, wetness, and carried state in
  words even when visible in the reference.

Use a minimal character anchor around a strong reference:

```text
@TAG: age + role/build + current state + unique visible features +
action-critical detail + voice only when speaking. 100% matches the reference.
```

The repository's 3–6 locked identity anchors remain verbatim, but add no
redundant appearance prose beyond those anchors and action-critical state. Long
text competes with the reference and can reduce likeness.

## Context isolation

Every generation is a blank slate. The prompt is a sealed shot document.
Exclude scene numbers, script headings, prior-scene summaries, unused tags,
`as above`, and `continues` without explicitly restating the visible inherited
motion and state. Chained inputs are references, not memory.

## Canonical prompt structure

Use the blocks below in this order and omit optional blocks that add no control.
The prompt starts with content and references; descriptive style lives beside
what it governs; technical style is a suffix immediately before locks.

```text
SCENE CONTEXT
[What visibly happens, where and when; character geo-positions.]

ACTIVE REFERENCES
[@tag + minimal critical anchor + 100% reference match.]

LOCATION MAP
[Foreground, midground, background, camera position, light source, paths.]

FIRST FRAME / BLOCKING
[Initial positions, orientation, gaze, hands, composition, immediate motion.]

FORMAT MODE
[Single continuous shot / sequential cuts / timed multishot / freestyle b-roll.]

OPTICS
[Shot size, approved FOV degree, optical character; per segment when cutting.]

CAMERA
[Height, distance, operator axis, movement, focus, tonal response.]

ACTION
[Ordered visible events; subject motion and camera motion stated separately.]

PERFORMANCE
[Observable muscle-level acting, eyelines, pauses, living skin and eyes.]

PHYSICS
[Mass, inertia, contact, fluids, fabric, particles, contact shadows.]

LIGHTING
[Source, direction, exposure, key/fill, haze depth, fixed white balance.]

COLOR GRADE
[Only for a strong grade: color as material + light + compositional role.]

WARDROBE
[Only when costume state matters: material, fit, wear, wetness/damage.]

AUDIO
[Only the required dialogue, voice delivery, foley, ambience, and effects.]

STYLE
[Live-action realism, optical/tonal finish, grain and format character.]

OUTPUT SETTINGS
[Only when pinned: resolution, aspect, speed mode, fps/bitrate intent.]

POSITIVE LOCKS
[Short positive fixers for identity, geography, props, light, cuts, continuity.]
```

`SCENE CONTEXT` and `ACTIVE REFERENCES` are the opening pair. `CAMERA` is the
third core directing layer after subject/blocking and action intent; keep the
literal block order above so optics and format are resolved before operator
behavior. Never add a generic style prefix at the top.

## Distributed style

Put each aspect in the block that controls it:

| Aspect | Home |
|---|---|
| source, direction, exposure, haze | `LIGHTING` |
| palette/grade | `COLOR GRADE`, or natural color in `LOCATION MAP` + `LIGHTING` |
| FOV, rectilinear/anamorphic character, motion blur | `OPTICS` |
| tonal latitude, highlight roll-off, color response | `CAMERA` |
| pores, capillary flush, catch-lights, breath, restraint | `PERFORMANCE` |
| gravity, inertia, contact, fluids, particles | `PHYSICS` |
| composition and movement from frame one | `FIRST FRAME / BLOCKING` |
| material and condition | `WARDROBE` |
| resolution, grain, fps, bitrate, overall realism | `STYLE` + `OUTPUT SETTINGS` |
| identity, prop, geography, and cross-cut continuity | `POSITIVE LOCKS` |

For a naturalistic shot, omit `COLOR GRADE`, `WARDROBE`, or `OUTPUT SETTINGS`
when their information already lives clearly elsewhere.

## Cuts and timing

Choose precision based on the dramatic need:

- **Single continuous shot:** `One continuous shot.` State the operator path and
  uninterrupted ending positively.
- **Sequential cuts:** `CUT 1`, `CUT 2`, `CUT 3` in order when exact seconds do
  not matter.
- **Timed multishot:** use explicit ranges and cut points only when beats must
  land on a clock.
- **Freestyle b-roll:** describe subject, environment, coverage intent, and
  continuity but let Seedance find the angles.

Timed form:

```text
0.0s to 1.0s — [visible action and camera]
1.0s HARD CUT
1.0s to 3.0s — [visible action and camera]
```

Supported deliberate transitions include `HARD CUT`, `SMASH CUT`, `MATCH CUT`,
`INSERT CUT`, `REVERSE CUT`, and `WHIP CUT`. Use fades or crossfades only when
the Director requests them. Across cuts restate character set, geometry, screen
direction, gaze, light, wardrobe, prop state, and segment FOV. Add `no drift
mid-segment` as the documented camera-control phrase when needed.

## Directing laws

- Block bodies, hands, props, furniture, paths, orientation, and gaze. Left and
  right are always from the camera's view.
- Translate emotion into action: eyes drop, jaw tightens, knuckles whiten,
  breathing shortens, a swallow delays the answer. Restraint is the default.
- Motivate every camera move. State FOV, height, distance, operator axis, speed,
  and ending composition.
- Keep the camera on the shadow side unless the approved direction specifies a
  motivated axis change.
- Separate foreground, midground, and background.
- Describe what should happen in positive terms. Convert `negative_notes` and
  `forbidden_drift` into desired visible states inside `POSITIVE LOCKS`.
- Use speeds in km/h where speed matters; atmosphere in percentage and visible
  depth in meters; giant scale by comparison to human height. When atmosphere
  intensifies across cuts, state deliberate steps (for example 20% → 40% → 60%)
  rather than asking for an undefined gradual increase.
- State physical interaction: water runs through hair, wind loads fabric, shoes
  compress mud, particles respond to wake and gravity.
- Use one white balance per scene, expressed in Kelvin when it materially controls
  the look: common anchors are 3200K, 4000K, 5600K, and 8500K.
- Describe the look, never camera, film-stock, lens-brand, director, or signature
  work names.
- Tie color to material, light beam, and compositional role rather than listing
  colors.

## Audio and dialogue in this pipeline

Stage 9 keeps `AUDIO` whenever the clip needs dialogue, foley, ambience, or a
directed sound because Seedance's baked audio supplies the source track. Quote
approved dialogue exactly as `Name says: "line."`; attach every speaker's locked
voice sample and tag it in `ACTIVE REFERENCES`. Do not request a full score;
music belongs to stage 10.

## Positive locks

Locks are short hard fixers, not a second prompt. Restate a critical fact once in
positive form near what it protects, and collect only the highest-risk invariants
at the end. Examples: `headlights stay glowing through every cut`; `her wet black
coat remains buttoned`; `the doorway stays background-right`; `cuts occur at the
specified points`.

## Advanced optics and effects

Read [references/optics-and-protocols.md](references/optics-and-protocols.md) when
the shot uses precise FOV design, extreme wide/tele optics, observation/sports
coverage, whip transitions, mixed time speeds, or pressure-based breaking.

## Preflight checklist

- Correct profile selected from `brief.visual_medium`?
- One sealed shot; no history, scene headings, or unused assets?
- First frame occupied and moving; subject, geography, gaze, and light clear?
- Every attached image/video/audio appears once in the two-way tag map?
- References carry minimal text plus verbatim locked anchors and critical state?
- Blocks follow the canonical order; no style prefix?
- Style distributed to its governing blocks and adapted to this scene?
- Positive phrasing throughout, including converted drift/content constraints?
- Emotion is muscle movement; physics and environmental contact are visible?
- FOV comes from the approved discrete table; per segment for multishot?
- White balance fixed where needed; camera axis and shadow side stated?
- Foreground/midground/background separated?
- Dialogue exact, speaker named, voice reference attached, listener directed?
- Chained opening restates inherited visible motion; final beat provides the
  approved handoff state?
- English only; no director, equipment, or signature-work names?

## Final rules

- English prompts only.
- Positive phrasing only; camera-control clauses may use the model's documented
  `no drift mid-segment` wording.
- No director names, signature-work references, or equipment names.
- Direct request output: one standalone prompt in one code block.
