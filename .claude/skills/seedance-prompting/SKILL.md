---
name: seedance-prompting
description: >
  Seedance 2.0 prompt-writing system. Use whenever the user wants to write a
  Seedance prompt, build a cinematic shot or scene, turn an idea or script beat
  into a prompt, set up references/assets, regenerate a clip, or audit Seedance
  prompt quality. Always consult this skill before writing any Seedance prompt.
---

# Seedance 2.0 Prompt Writer — Clean Contract

Turn scripts, scenes, and ideas into Seedance prompts. Block, light, and pace
each shot like a film.

**Output: always one standalone English prompt in one code block.** In stage 9,
the clip-producer takes that prompt string and records it in the generation
manifest; the prompt writer itself does not return JSON, commentary, a reference
report, or alternatives.

This contract incorporates the Director-supplied `seedance-clean` skill and
supersedes conflicting older prompt rules in this repository. In particular:

- multishot is no longer the default;
- timed cuts are allowed when the beat needs them;
- prompts open with `SCENE CONTEXT`, followed by `ACTIVE REFERENCES`;
- style is distributed into the block it governs, never used as a prefix;
- prompt optics use the approved FOV degrees, not millimeters;
- age may be stated in the minimal reference anchor;
- content and continuity constraints are written as positive target states;
- long anti-drift appearance paragraphs around strong references are removed.

Compatible production laws remain binding: approved/locked assets only, exact
dialogue, voice/reference threading, continuity artifacts, paid-call gates,
chaining inputs, model capability limits, and provenance recording.

## Model envelope

Seedance 2.0 is the default: native synced speech/SFX/ambience, quoted-dialogue
lipsync, up to 9 images + 3 videos + 3 audio references, 4–15 second clips, and
the aspects/resolutions in `config/model_capabilities.yaml`. Seedance 2.5 uses
the same prompt contract with its Director-ordered 30-second ceiling. Model
choice, cost preflight, and capability verification remain Director-gated.

## Core principle: write the visible

The model reacts to what can be seen, heard, and measured, not mood words.
Translate every abstraction into observable direction.

- `tense scene` → `the man freezes, slowly clenches his fist; side light leaves
  half his face in shadow`
- `cool cinematic shot of a fast car` → `low tracking shot alongside the car as
  it powers through a wet curve; headlights glow, tyre spray crosses frame, the
  camera takes short buffeting impacts`

Use plain instruction-style language. Fewer precise words beat many vague ones.
Before returning, mentally watch the prompt: the first frame is occupied; the
subject, gaze, geography, light source, movement, and ending are unambiguous.

## Workflow

1. Read as a director. Find where the beat turns, lands, and breathes.
2. Define continuity anchors: who is present, their current state, carried props,
   geography, light, weather, and emotional carry.
3. Close material gaps before writing. In a gated production, flag ambiguous
   blocking, first frame, angle, light, timing, behavior, or ending instead of
   inventing against approved artifacts.
4. Choose the least rigid format mode that still lands the beat.
5. Write the prompt using the canonical blocks below; omit blocks the shot does
   not need.
6. Build and verify the two-way asset map.
7. Run the checklist.

## Asset tagging

A reference image sets appearance and identity. Text sets what happens and locks
critical state. Both are required.

- Preserve tags explicitly supplied by the user, such as `@tag_name`.
- Otherwise tag assets by their actual load order: `@image1`, `@image2`, …;
  `@video1`, `@video2`, …; `@audio1`, `@audio2`, ….
- Provider-required spellings such as SJinn's `@Image1/@Audio1` count as an
  explicit instruction and take precedence.
- Never attach or tag a person, object, place, video, or sound that is unused in
  this shot. The model will try to force it into frame.
- State critical small text, logo, color, damage, wetness, wardrobe, and carried
  state in words even when visible in the reference.

Use minimal text around a strong character reference:

```text
@TAG: age + role/build + current state + unique visible features +
action-critical details + voice only when speaking. 100% matches the reference.
```

Repository identity anchors remain verbatim, but do not add a second long
appearance description. The locked reference carries pixels; the 3–6 anchors
and action-critical state stabilize the text channel.

### Two-way map before submission

Write one internal line per attached media item:

```text
load position → role → file/media id → @tag
```

Every attached item must have one tag and every tag must resolve to an attached
item. Rebuild the map for every call; numbering shifts when a start image or
other reference is added or removed.

## Context isolation

Each generation is a blank slate. The prompt is a sealed shot document. Do not
carry scene numbers, script headings, prior-scene summaries, unused tags, or
phrases such as `as above`. A chained shot may say what motion it inherits only
after explicitly restating the visible motion, state, light, and geometry.

## Style is distributed, not a prefix

There is no style block at the top. Put every descriptive aspect where it has
the clearest effect:

| Aspect | Home block |
|---|---|
| source, direction, exposure, key/fill, haze | `LIGHTING` |
| natural color | `LOCATION MAP` + `LIGHTING` |
| strong stylized grade | `COLOR GRADE` |
| FOV, rectilinear/anamorphic character, motion blur | `OPTICS` |
| tonal latitude, highlight roll-off, color response | `CAMERA` |
| acting, skin, eyes, breath, restraint | `PERFORMANCE` |
| gravity, mass, inertia, contact, fluids, particles | `PHYSICS` |
| composition and initial motion | `FIRST FRAME / BLOCKING` |
| wardrobe material and condition | `WARDROBE` |
| identity, prop, environment and cut continuity | `POSITIVE LOCKS` |
| resolution, grain, fps, bitrate, overall output look | `STYLE` + `OUTPUT SETTINGS` suffix |

Use only what the shot needs. A naturalistic oner may omit `COLOR GRADE`,
`WARDROBE`, and `OUTPUT SETTINGS`; a designed multishot may earn the full stack.

## Canonical prompt structure

Write blocks in this order. Do not move style to the top.

```text
SCENE CONTEXT
[One or two sentences: visible event, place, time, character geo-positions.]

ACTIVE REFERENCES
[@tag + minimal critical anchor + "100% matches the reference."]

LOCATION MAP
[Foreground / midground / background; camera and light origin; movement paths.]

FIRST FRAME / BLOCKING
[Initial positions, orientation, gaze, hands/props, composition, motion from frame one.]

FORMAT MODE
[Single continuous shot / sequential cuts / timed multishot / freestyle b-roll.]

OPTICS
[Shot size + approved FOV per segment + optical character.]

CAMERA
[Height, distance, operator axis, movement, focus, tonal response.]

ACTION
[Ordered events; subject motion and camera motion stated separately.]

PERFORMANCE
[When acting matters: muscle-level behavior, eyelines, pauses, living skin/eyes.]

PHYSICS
[Mass, inertia, contact, fabric, fluids, particles, contact shadows.]

LIGHTING
[Source, direction, exposure, key/fill, haze depth, fixed white balance.]

COLOR GRADE
[Only when strong: color as material + light + compositional role.]

WARDROBE
[Only when costume matters: material, fit, wear, wetness/damage.]

AUDIO
[Only required dialogue, voice delivery, foley, ambience, and effects.]

STYLE
[Overall visual finish, realism/render treatment, format, fine grain.]

OUTPUT SETTINGS
[Only when pinned: resolution, aspect, real-time/slow-motion, fps/bitrate intent.]

POSITIVE LOCKS
[Short positive fixers for likely failures and cross-cut continuity.]
```

`CAMERA` is the third core directing layer after subject/blocking and action
intent; the literal block order above keeps format and optics resolved before
operator behavior. Never bury camera direction at the end.

## Cuts and timing

Pick the precision the shot needs:

- **Single continuous shot:** `One continuous shot, the camera does not cut on
  its own.` State one executable operator path and ending.
- **Sequential cuts:** write `CUT 1`, `CUT 2`, `CUT 3` when order matters but
  exact seconds do not.
- **Timed multishot:** use explicit ranges and cut points when beats must land on
  a clock.
- **Freestyle b-roll:** describe coverage intent and continuity without locking
  cuts.

Timed form:

```text
0.0s to 1.0s — [visible action and camera]
1.0s HARD CUT
1.0s to 3.0s — [visible action and camera]
```

Sequential form:

```text
CUT 1 — [visible action and camera]
CUT 2 — [visible action and camera]
```

When cuts are specified, use the control phrase `cuts only at the specified
points, the camera does not cut on its own.` Deliberate cut types include
`HARD CUT`, `SMASH CUT`, `MATCH CUT`, `INSERT CUT`, `REVERSE CUT`, and
`WHIP CUT`. Fades and crossfades appear only on Director instruction.

Across internal cuts hold character set, geometry, screen direction, gaze,
light, wardrobe, prop state, and per-segment FOV. Re-anchor positions after a
cut. Use `no drift mid-segment` when a segment's FOV must remain fixed; these
exact camera-control phrases are the only sanctioned negative constructions.

## Directing

### Blocking and first frame

State where each person stands or sits, where they face and look, what their
hands do, what sits between them, and where they move. Everyone who is meant to
move is already moving from frame one. Left/right is from the camera's view.

### Pace

Read the dramatic shape. A confession earns air, held shots, micro-pauses, and
silence. Action compresses time and uses shorter cuts. A reveal lands on a held
composition or close-up instead of being buried in coverage.

### Acting

Translate emotion into visible muscle behavior:

- `she looks sad` → `her eyes drop to the table, her jaw tightens, she swallows
  once before answering`
- `he is angry` → `his knuckles whiten on the glass, breath shortens, eyes never
  leave hers`

Restraint by default. Direct the listener as deliberately as the speaker.

### Camera

Be concrete: approved FOV, height, distance, operator axis, movement speed,
motivation, focus, and end frame. One shot gets one clean camera idea. Put the
camera on the shadow side unless the approved direction motivates an axis change.

### Light and color

State source, direction, exposure, key/fill relationship, and haze depth. Fix
white balance within a scene when it matters: 3200K, 4000K, 5600K, and 8500K are
useful anchors, not mandatory presets. Tie color to material + light beam +
compositional role: `a crimson silk scarf catches the cold corridor spill`, not
`red and blue palette`.

### Physical measurement

- Use km/h when speed matters.
- Use atmosphere percentages and visibility in meters. When it builds across
  shots, state deliberate steps such as 20% → 40% → 60%.
- Express giant scale relative to human height.
- State interaction: snow melts on skin, rain runs through hair, wind loads
  fabric, footwear compresses mud, particles respond to wake and gravity.

## Optics

Use FOV degrees in prompt text, never millimeters and never arbitrary values.

### Shot sizes

| Abbreviation | Visible area |
|---|---|
| ECU | one detail: eyes, hand, button, headlight |
| CU | full face or one large element |
| MCU | head and shoulders |
| MS | roughly to the waist |
| WS | full figure and surroundings |
| EWS | location and scale |

### FOV anchors

| FOV | Purpose |
|---:|---|
| 180° | fisheye POV or dream-state distortion |
| 107° | architectural ultra-wide, huge interiors |
| 84° | wide establish and group blocking |
| 63° | observational wide and intimate environment |
| 47° | neutral human perspective |
| 29° | dialogue bust and portrait isolation |
| 18° | identity-preserving close portrait |
| 12° | tele detail and distant observation |
| 8° | extreme compression and broadcast behavior |

In a multishot, state FOV per segment and add the fixed-segment control phrase.

## Optical techniques

### Observation / hidden-vantage pattern

Use all three: an out-of-focus foreground obstruction over 20–30% of frame;
visible haze/dust/shimmer between camera and subject; and an 8°–12° distant
vantage. Change occlusion type between beats while retaining one physical
vantage.

### Sports broadcast

Use 8° super-tele, handheld 1–2 cm tremor, and an operator anchored at distance
who finds and follows the action.

### Detail-on-wide

Use 84° wide FOV with the camera low and very close to a small foreground object,
exaggerating it while the background recedes.

### Intimate wide

Use 63°–84° wide FOV close to a centered face so surroundings remain readable.

### Compressed air column

At 8°–12°, state visible depth: dust suspended in the compressed air column or
heat shimmer compressed across the foreground.

## Special protocols

### Extreme-FOV multishot stack

At 8° or 107°, use all four:

1. one sequence-wide identity and location lock;
2. a `LENS LOCK` opener with exact FOV at every beat;
3. a `LENS CHECK` closer confirming the FOV at every beat;
4. color expressed as material + light + role.

### Whip-pan timing

```text
0.0s to 0.3s — Subject A settled.
0.3s to 0.8s — whip motion blur fills the frame.
0.8s to 1.4s — Subject B resolves and settles.
```

A whip shorter than about 0.8 seconds often reads as a hard cut.

### Mixed time speeds

Separate real-time and slow-motion segments with hard cuts. One speed mode lasts
for the full segment.

### Pressure cracks without impact

State the positive mechanism: sustained crowd pressure; fracture originating at
edge stress; an ordered edge-to-center crack; the surface remaining under
compression as fragments separate.

### Existing proven impact moves

Speed ramp, freeze-and-orbit, masked reframe, motivated emotional drift, and rear
chase lock remain available when compatible with this contract. Use at most one
conspicuous impact move per scene, state its boundaries, and reserve it for the
earned peak.

## Engine constraints retained from production evidence

- Only describe what can be seen or heard.
- Translate similes/metaphors into literal visible direction; Seedance may render
  comparisons as objects.
- Track at most three foreground characters across internal cuts; extras remain
  background texture.
- Re-anchor positions/facing after cuts and preserve the 180° line.
- Show state changes on camera before referring to them.
- Use one action intent or named technique rather than joint-by-joint mechanics.
- A character exiting frame remains absent for the rest of that continuous shot
  unless an explicit cut re-establishes them.
- Reflection-heavy geography is unreliable; use it only on explicit Director
  instruction with a simple spatial plan.

## Audio and dialogue

Use `AUDIO` only for sound this clip needs: exact approved dialogue, voice
delivery, foley, ambience, and directed effects. In this pipeline Seedance's
baked audio supplies the source SFX track, so ask for required diegetic sound but
not a full score; music belongs to stage 10.

Write dialogue exactly as `Name says: "line."` Quoted strings drive lipsync.
Attach and tag every speaking character's locked voice sample. Never generate a
speaking clip without its reference audio.

## Reference and identity lock

- Use locked character sheets, the locked environment plate, selected
  storyboard/keyframe material, and voice samples; never unlocked variants.
- Stay within the model's image/video/audio reference limits.
- `ACTIVE REFERENCES` is second, after `SCENE CONTEXT`, and follows the actual
  media load order.
- Around each character reference include the 3–6 identity anchors verbatim,
  current outfit/state, action-critical details, and voice only when speaking.
  Keep everything else minimal.
- Convert every `forbidden_drift` risk into a desired visible state in
  `POSITIVE LOCKS`: stable hair length/color, same facial age and geometry,
  unchanged wardrobe material/color, correct prop hand, stable location fixtures.
- If a reference itself shows the wrong state, fix or derive the reference with
  Director approval; text cannot reliably fight an image.

## Chained-scene conditioning

Keep the repository's proven conditioning set:

1. previous approved clip's final 3 seconds as `@video1` (or its true load-order
   tag), carrying motion, light, and state;
2. the scene's promoted keyframe as a style/composition reference, not a start
   frame;
3. locked character sheets and location plate;
4. picked storyboard page when stage 8 ran;
5. for continuous overlap generation, the sharp mid-motion predecessor frame at
   `overlap_seconds` before the end as `start_image`.

The opening `FIRST FRAME / BLOCKING` restates the inherited mid-motion pose,
weight, screen vector, energy, light, and carried state, then re-covers the
predecessor's final beat before new action. Do not reduce a moving start frame to
a static furniture description. The final action books the exact approved
handoff state for the successor.

## Params and generation call

Use the selected model entry in `config/model_capabilities.yaml` as authority:

- `duration`: approved scene duration within model range;
- `aspect_ratio`: approved brief aspect;
- `resolution`/`mode`: valid combination only;
- `generate_audio`: true when the clip needs the pipeline's native audio;
- `bitrate_mode`: selected production setting;
- `medias`: actual ordered references matching the prompt tag map;
- `get_cost: true`: preflight before every paid attempt.

Record final prompt, params, media paths/ids, job id, seed when returned, cost,
attempt, and output in `generation_manifest`. Regeneration requires a new
Director-authorized attempt.

## Positive locks

A lock is a short hard fixer, not a second prompt. State critical facts once near
what they protect and repeat only the highest-risk invariants at the end:

- `headlights stay glowing through every cut`;
- `her wet black coat remains buttoned`;
- `the doorway stays background-right`;
- `cuts occur only at the specified points`.

## Anti-drift fallback ladder

1. Strengthen the violated positive lock once and verify the reference map.
2. Replace/add the facing-matched locked view; prefer a few coherent references
   over flooding all slots.
3. Shorten duration and simplify action/cuts.
4. Escalate an impossible direction, bad reference, or contradictory start frame
   upstream. Two failed attempts on the same anchor stop autonomous iteration.

## Checklist

- One sealed standalone prompt, English only?
- Opens `SCENE CONTEXT`, then `ACTIVE REFERENCES`?
- Tags follow explicit names or actual `@imageN/@videoN/@audioN` load order?
- Every attached asset tagged exactly once; no unused assets/tags?
- Reference text minimal, locked anchors verbatim, critical state explicit?
- First frame occupied; positions, orientation, gaze, light and motion clear?
- Format mode uses only the control actually needed?
- Timed cuts only when timing matters; specified cuts are the only cuts?
- FOV uses the discrete degree table, per segment, never millimeters?
- Camera height, distance, axis, movement, focus and end state concrete?
- Acting is muscle movement and eyelines, not emotion labels?
- Physics, contact, environment interaction and atmosphere measurable where useful?
- Lighting has a source/direction and fixed white balance when needed?
- Color is material + light + role, not a flat list?
- Style is distributed; technical `STYLE`/`OUTPUT SETTINGS` sit at the end?
- Content constraints and drift risks expressed as positive target states?
- Exact dialogue and every speaker's tagged voice reference present?
- Chained opening absorbs inherited visible motion; ending provides its handoff?
- No director names, signature-work references, or equipment names?

## Final rules

- English prompts only.
- Positive content phrasing only; use only the exact camera-control clauses
  documented under format mode and fixed-segment optics.
- No director names, signature-work references, or equipment names.
- Return one standalone prompt in one code block and nothing else.
