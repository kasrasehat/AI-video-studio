---
name: character-sheets
description: "Single-image annotated model sheets for characters AND locations — the visual half of the identity lock. Use when generating character/location sheet variants in stage 7, adding views or expressions to a locked sheet, or repairing an identity-drifted reference."
---

# Character & Location Sheets

A sheet is ONE image that locks an identity: multiple views + detail callouts + text annotations, generated in a single call. Every downstream generation (storyboard frames, clips) conditions on the locked sheet. Method and defaults set by the Director (2026-07-17): **single-image sheets, GPT-Image-2, design-distinct variants.**

## Model default (Director decision, binding)

**`gpt_image_2`** (Higgsfield catalog, OpenAI) for ALL character and location sheets — chosen for its layout control, text/annotation rendering, and detail fidelity. `quality: high`, `resolution: 2k`, landscape `16:9` or `3:2` for sheets. Nano Banana Pro remains the fallback and the consistency-edit tool.

## Character sheet — ONE image containing (state each in the prompt):

1. **Three full-body views side by side of the SAME character**: front, three-quarter left, left profile — consistent height, same neutral standing pose, white/light-neutral background, subtle ground shadow.
2. **Face detail inset**: large close-up of the face (the identity's core), plus 1–3 small insets for the character's most identity-critical features (e.g. goggles, mustache, distinctive marks, footwear).
3. **Text annotations**: small clean labels calling out identity anchors and subtle features — professional film/character reference-sheet typography consistent with the approved brief style.
4. **Maximum prompt detail**: EVERYTHING the descriptor knows goes into the prompt — all identity_anchors verbatim, all static_features (face/body/age/marks), default outfit with palette hexes, height/build ratios, render style. GPT-Image-2 rewards density; a sparse sheet prompt is a wasted generation.

Layout instruction template: "Professional character model sheet, landscape: three full-body turnaround views (front, three-quarter left, left profile) of the same character evenly spaced; large face close-up inset top-right; small detail insets (X, Y); clean small text labels annotating features; white background, studio reference-sheet layout."

### Scene-conditional accessories (BINDING — Director rule 2026-07-22, d-098)

A picture always beats a text negative. If a character's sheet shows an accessory (a strapped-on bracelet, a held prop baked into the pose, a costume piece) and a downstream prompt says "this scene, no [accessory]", the model follows the reference image, not the negative clause — confirmed empirically (S01_C01 attempt 1: the locked sheet's bracelet close-up inset overrode an explicit "no recall bracelet yet" negative).

**Before locking any sheet whose character gains, loses, or swaps a discrete accessory partway through the film:**

1. **Count scenes.** From the character's `outfit_by_scene` (authored at stage 6), tally how many scenes show the accessory present vs absent.
2. **Build the locked default sheet as the MAJORITY state.** The sheet stays the character's single locked reference for most scenes — this is deliberate, not an oversight; redesigning the default sheet to the minority state would mean building a derived asset for MORE scenes, not fewer.
3. **Produce ONE derived reference for the minority-state scenes** — an edited copy of the locked sheet (via the `image-editor` skill, `gpt_image_2`) with the accessory removed/added across EVERY view that shows it, not just its dedicated inset (all full-body turnaround views typically carry it too — check each one). Save as a new file; NEVER overwrite the locked original. Use this derived reference only for the scenes whose `outfit_by_scene` state disagrees with the default sheet.
4. **If the minority/majority split is closer to even** (roughly 40/60 or beyond), skip step 2's asymmetric approach — generate two full peer sheets from the start (with-accessory / without-accessory) and pick the scene's reference by state, no derived-asset step needed.
5. This applies to discrete ADD/REMOVE accessories (bracelet, held prop, hat). Full-body MATERIAL/texture states across many scenes (soaked vs dry) are a different, likely more disruptive class — if a similar reference-vs-text conflict shows up there, treat it the same way (majority-state default sheet + a derived wet/dry variant for the minority) rather than fighting it with negatives alone.

## V2 additions (Director passage 2026-07-30 — apply from production V2 onward; V1 sheets stay locked as-is)

**Turnaround view set (V2 default for character sheets).** The four canonical views, replacing V1's three-quarter-heavy trio:
1. **Full Body Front** — slight three-quarter front, entire body head to toe.
2. **Full Body Back** — straight rear view, full body. (NEW vs V1 — V1 sheets had no back view, which forced the video model to invent rear hair/outfit details whenever a character turned away. Board it in.)
3. **Front Portrait** — detailed head-and-shoulders front: facial features, hair, textures, upper clothing.
4. **Side Portrait** — head-and-shoulders left profile (true 90°), neck and upper shoulders included.
Layout rules: same character identical across all views (face, proportions, hairstyle, outfit, colors, accessories); **neutral grey studio background** (V2 default over V1's white — grey conditions more neutrally and reads texture better); clean balanced studio lighting, soft shadows, realistic material textures; symmetrical layout, equal spacing; **no props, no extra characters, no logos/watermarks**.

**Annotations (Director ruling C, 2026-07-30 — d-143):** V2 sheets KEEP the V1 annotation style — small clean text labels calling out identity anchors and features. The source passage's "no text/labels" rule is not adopted for sheets.

**Object/prop reference sheets (V2 — formalizes what V1 did ad hoc for the Minimizer/bracelet/cookie).** One image, four studio views on neutral grey: Front (main design), Rear, 90° Side (thickness/profile), and a **Close-Up Detail of the object's most identity-critical feature** (the dial face, the trigger, the bitten edge). Identical design/proportions/colors/materials across views; realistic textures and material-true reflections; no hands, packaging, or extra objects.



1. **Main establishing view** from the location's declared camera axis (the largest panel).
2. **2–3 alternate angles** (reverse angle, opposite end, or a high overview) so downstream stages know the geography from more than one side.
3. **Detail insets** of the location's identity anchors (the vise, the window, the valve, the memory-glow wall…).
4. **Text annotations** naming fixtures and features; lighting_baseline rendered faithfully in every panel; time-varying props per the descriptor's plate guidance (usually excluded).

### The spatial contract (BINDING — Director rule 2026-07-18)

Multi-angle sheets confuse fixture positions across panels unless the prompt pins them. Before generating ANY location sheet:

1. **Write a floor plan** from the descriptor: assign every fixture to a WALL (name walls by compass or by role — "window wall", "bench wall", "door wall") plus exact along-wall positions and adjacencies ("door at the EAST end of the bench wall; fridge against the EAST wall beside it; stool at the bench's east end"). Include a fixture COUNT ("exactly one workbench, one door, one window, one fridge").
1b. **Relative-position map (Director rule 2026-07-18):** wall assignment alone is not enough — the prompt must ALSO state pairwise relationships between objects so panels agree on adjacency and distance: "the sink sits directly BELOW the window; the dishwasher is immediately beside the sink; the door is two strides from the northeast corner; the table stands two strides from the counter and two from the door." Every fixture appears in at least one relative statement (what it is next to / below / across from, and roughly how far). These relationships live in the LOCATION DESCRIPTOR (the base file) so every future sheet, storyboard frame, and clip prompt inherits the same spatial truths — author them at stage 6, refine them here.
2. **Spell out each panel's screen geometry explicitly** — never let the model infer a camera flip: "MAIN VIEW (camera on the south side facing the bench wall): window frame-LEFT, vise at the bench's left end, door deep frame-RIGHT. REVERSE ANGLE (camera behind the bench facing south): the SAME room mirrored — window now frame-RIGHT, door and fridge now frame-LEFT." The reverse-angle mirror is the #1 failure; state it as "now frame-X" per fixture.
3. **Constrain the overview**: "top-down floor plan showing EXACTLY the fixtures listed, one of each, on their stated walls" — overviews love to invent duplicate furniture.
4. Close the prompt with: "ALL panels depict the SAME single room; identical fixtures, identical positions, consistent with the stated floor plan; no added or duplicated furniture."
5. **Self-QC across panels** before presenting: pick two fixtures and trace them through every panel — positions must agree with the floor plan (mirrored where the camera flips). A sheet whose panels disagree is regenerated, not shown.
6. **Functional completeness (Director rule 2026-07-18):** the room must read as its TYPE, not as a generic "working room". Before writing the floor plan, inventory what a viewer expects of that room type (a kitchen cooks: stove, sink, dishwasher, coffee maker, utensils, dishes; a workshop builds: tools, vises, materials) and wall-assign each item in the floor plan. If the descriptor lacks the type inventory, amend the descriptor FIRST (archived, validated) — never generate a room that fails the "would a child name this room correctly?" test.

## Variant discipline (Director rule, binding)

The ~2 variants must create a real Director choice inside the approved brief style. Vary casting presence, silhouette/proportion language, natural styling, production design, materials, or another style-appropriate interpretation. Do not silently change the rendering medium. "Crisper vs softer texture" is not a meaningful pair. Record the interpretation explicitly in `generator.params.interpretation`.

## Workflow

- One call per variant (`gpt_image_2`, quality high). Record model, full prompt, job_id as media_id, cost per variant in `asset_manifest`; file naming `assets/characters/<char_id>_<variant>_sheet.png` / `assets/environments/<loc_id>_<variant>_sheet.png`.
- **Self-QC before presenting:** every anchor visibly true in every view/panel; the three views are the SAME design (not siblings); annotations legible and correct (a wrong label on a locked sheet becomes canon — check them); palette respected. Regenerate a failed sheet, never show it.
- After the Director's pick → `locked: true`. For per-scene outfits or expression additions: i2i from the LOCKED sheet (`medias role image`) — "same character as the reference sheet, exact same design, now …".
- Downstream: the locked sheet is the reference image for storyboard frames and clips. Per the clean Seedance contract, the video prompt uses age + role/build + anchors verbatim + current/action-critical state and avoids a second long appearance description.

<!-- v2 method per Director notes 2026-07-17; v1 (3-view i2i chaining, ViMax-style) retired — see git history -->
