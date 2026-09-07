---
name: seedance-prompting
description: Prompt engineering for Seedance 2.0 — our primary video model (native voice + lipsync + reference conditioning, ≤15s clips, via Higgsfield MCP). Use when assembling any Seedance generation call (stage 9 prompt-smith), regenerating a failed clip, or auditing prompt quality.
---

# Seedance 2.0 Prompting

Seedance 2.0 (ByteDance) is this pipeline's default video model: single-pass native synced audio (speech + SFX + ambience), lipsync from quoted dialogue, multi-shot inside one generation, director-level camera control, and reference conditioning of up to **9 images + 3 video clips + 3 audio clips**. Max clip 15s (our scene unit), 4–15s range, aspects 21:9/16:9/9:16/4:3/1:1. Access is via the Higgsfield MCP (`skills/tech/higgsfield-mcp`); routing/capabilities live in `config/model_capabilities.yaml`.

**This skill was merged with the Director-supplied "Seedance 2.0 Universal Director" skill (d-201, 2026-08-17). Director rulings on the merge: prompts are ENGLISH ONLY (the source skill's bilingual EN+ZH output is eliminated); MULTI-SHOT cut grammar is the DEFAULT scene form; per-shot timing marks are dropped; the age-blind rule applies with a single exemption for locked identity anchors. Where this skill and old E01 prompt patterns disagree, this skill wins.**

## Seedance 2.5 — the parallel 30s flow (d-204)

Seedance 2.5 (`seedance_2_5` in `config/model_capabilities.yaml`) generates clips up to **30 seconds** and runs as a PARALLEL flow beside 2.0: **every rule in this skill applies to 2.5 verbatim** — prompt contract, archetype router, engine rules, cut grammar, chaining/conditioning (d-202/d-203), identity lock, handoff beats, word window. Only the ceiling changes: scenes may be divided up to 30s (stage 3), the dialogue budget scales at ≈2 wps (~50–60 words per 30s clip), and a 30s shot plan carries proportionally more cuts.

- **Model choice is the Director's command, never yours:** 2.0 remains the default; route to 2.5 ONLY when the Director explicitly orders it ("use seedance 2.5") — log the pick as `model_selection`.
- **Verify before the first paid call:** the 2.5 catalog id, params and per-second rate are UNCONFIRMED (`verify: true`) — `models_explore` + `get_cost:true`, announce, Director-gate (d-114). Never assume 2.0's rate.
- **The A/B protocol (Director-designed):** the same story stretch produced both ways — N short 2.0 clips vs one long 2.5 clip (e.g. 3×10s vs 1×30s), each spend gated, judged side by side at the gate. The Director then proceeds with one model, or uses BOTH together (per-scene assignment; stage 3 sizes each scene to its assigned model's ceiling).
- The 2.5 long take reduces SEAM COUNT (fewer clip boundaries = fewer d-191 handoffs) at the price of a bigger single-generation risk (one 30s reject costs more than one 10s reject) — surface both sides in the comparison report.

## The prompt contract (200–1000 words, EN only — d-138/d-201)

One continuous English string with inline section labels, present tense, active voice, 200–1000 words (the window buys room for the reference block and per-shot state restatement — never padding). Sections in this order:

1. **ACTIVE REFERENCES** (empirical law d-106/d-124/d-127 — opens every prompt; see Identity lock below): the @-map of every attached media, positional tags + named handles.
2. **Style & Mood:** palette, lighting, lens/grain, atmosphere. Never skip, always specific. One lighting idea, committed — never mix conflicting light ("bright noon" + "neon night").
3. **Narrative Summary:** one sentence of scene intent. Optional — first to trim when the word budget is tight.
4. **Dynamic Description:** shot-by-shot prose per the direction's SHOT PLAN — camera, movement, action, faces. The cut rules below are binding. **No per-shot timing, no "Shot 1:" labels (d-201)** — rhythm is implied by description density; transitions are woven into the prose ("Hard cut to low-angle close-up: …").
5. **Static Description:** location via its anchors, key props, ambient details, time_of_day/weather with sensory detail (wet asphalt, lantern haze). Everything Dynamic references must be established here or in the references block.
6. **Audio:** ALWAYS present in our pipeline — this overrides the source skill's dialogue-scenes-only rule, on production evidence (d-160): **the clip's baked audio IS the film's SFX track.** Every sound the scene needs (foley, ambience, directed effects like a heartbeat) must be asked for here, from `sound_direction` — stage 10 will NOT add it later, and post-audio never re-adds a sound class the prompt requested (a separately-mixed heartbeat bed doubled the baked heartbeats in E01). Keep it textural (`sandals on stone, festival drums two streets over`); never request full music scores — scoring belongs to stage 10. **Enforced as a written clause (d-103):** close every Audio block with `No music.` — the S39 att2 block omitted it while its neighbours carried it, asked for a motif that "swells into a bloom", and seedance baked a musical layer into the clip's single mixed track, where d-160 makes it untouchable and unmixable forever. When `sound_direction` itself names scoring (S40: "chimes resolving into the swelling wonder orchestration"), translate it to the physical sound that produces it and let the stage-10 cue deliver the swell; disclose the translation at the gate. If a directed sound spans the cut into the next scene, prompt it in BOTH clips identically. Dialogue lines live here too: `Name says: "line."` — exact quoted strings drive lipsync.

## Scene archetype router (d-201)

Classify every scene before writing — the archetype guides camera behavior, spatial logic, and what changes across time. The stage-5 direction names the archetype; the prompt executes it.

**Action:** chase/being chased → **Pursuit** (distance closing/opening; pursued ahead in frame, pursuer behind; path narrows/opens). Two opponents trading advantage → **Duel** (camera lower on the dominant side; dominance MUST alternate — neither side dominates more than one consecutive beat, else write it as a one-sided assault). Single decisive contact → **Impact** (build-up slow → hit fast → aftermath slow; point of contact = frame center). Default: Duel.

**General:** subject moves through space → **Journey** (tracking/aerial/traveling alongside; landscapes pass). Hidden becomes visible → **Reveal** (pan/crane/dolly reveal; the camera controls WHEN the viewer sees the subject). Nothing changes, mood IS the content → **Atmosphere** (minimal movement; slow push-in or static hold; micro-changes carry all drama). Default: Atmosphere.

**Dialogue:** both push, dominance trades → **Confrontation** (tight OTS, camera crosses axis on the power shift). One extracts, one resists → **Interrogation** (low-angle on the questioner, push-in on silence). Both need something, balanced → **Negotiation** (symmetrical framing, matching shot sizes). Default: Confrontation.

**Dialogue budget:** ~25–30 spoken words fit 15 seconds. If the scene carries more, keep the power-shift exchange (the line where dominance flips or truth emerges), one line before (setup), one after (reaction) — convert the rest to physical behavior. Stage 3 budgets scenes to this ceiling at division time, so the d-191 conversation-density law is satisfied across MORE scenes, never by cramming one.

## Engine rules (hard rendering constraints — d-201 + E01 evidence)

- **Action beats = intent + named technique, not biomechanics.** ✅ "spinning back kick connects." ❌ "left forearm rotates 45° to deflect the hook at wrist level." A named move from the direction is preserved; joint mechanics are compressed to the move's name or intent.
- **Describe force and direction, not destruction sequence.** ✅ "driven into the shelf, jars rattling." ❌ "thrown into the shelf, glass shatters, uses the rebound to sweep."
- **Spatial continuity breaks on cuts** — re-anchor positions and facing after any cut (see Cut rules).
- **≤3 characters tracked across cuts.** Name the acting pair and their interaction vector per shot; extras stay background texture.
- **Exit-frame = implicit cut.** A character who leaves frame is gone for the remainder of that shot — never choreograph exit + re-entry inside one continuous shot.
- **Off-screen = nonexistent.** State changes must be shown on camera before being referenced.
- **Avoid reflection shots** (blades, puddles, mirrors, chrome) — Seedance breaks scene geography rendering reflections.
- **Only describe what can be seen or heard.** ❌ "The air smells of ozone." ✅ "Fine dust drifting in the beam, wind moving the ferns."
- **Micro-expressions as physics (merges d-111).** ✅ "jaw clenches, nostrils flare; the grin falters, eyes widening." ❌ "looks angry," "is amazed." Every shot names what each visible face DOES — and faces must change across the clip; the listener's face on a dialogue line is directed as deliberately as the speaker's. Emotion words without a visible cause constrain nothing.

## Cut rules — multi-shot is the DEFAULT (d-201, Director ruling)

A scene's clip is a designed shot sequence by default; a single continuous shot is now the deliberate exception (Atmosphere archetype, tableaux, or wherever stage 5 explicitly designs one). Within the sequence:

1. **Double contrast (mandatory):** every cut changes BOTH shot size AND camera character. Shot-size scale: `extreme wide → wide → medium → medium close-up → close-up → ECU`. Camera modes: Handheld | Static/locked-off | Stabilized tracking | Crane/vertical | Aerial/drone — never repeat a mode across a cut.
2. **Re-anchoring + 180°:** after any cut returning to established space, re-state who is where and which direction they face. Screen direction survives the cut (moving left-to-right before = left-to-right after); state it explicitly.
3. **Inserts:** sub-second (0.3–0.5s) dramatic punctuation, any shot size, NO story beats (static moments only), **causally motivated** (the viewer must understand why they see this detail — the hand of the character just slammed down, not a generic boot in a puddle), and **the subject is named** (WHOSE hand — unattributed inserts render wrong content). Inserts obey double contrast.
4. **No per-shot timing** in the prompt — density carries rhythm. (This supersedes E01's `0–4s:` temporal markers. The per-beat STATE restatement those markers carried survives per-shot: every shot re-states each visible character's wearable/prop state — goggles, wet/dry, bracelet — and faces.)
5. **Within one shot, ONE clean camera idea still rules** — compound choreography inside a single shot ("dolly in while panning then tilt") remains forbidden (the E01 clip-killer). Framing changes now happen at CUTS, which is what they're for. The d-118 motivated emotional drift stays legal inside a shot.
6. **Chain edges are exempt from restructuring:** the FIRST shot must begin on the start frame and bridge from its actual composition (d-124); the FINAL shot books the handoff beat (d-191). Cuts live between those two anchors.
7. **In medias res** is the default entry energy — the scene is already in progress — expressed WITHIN the start-frame bridge, never instead of it.

## A reference only covers the angle and the state it shows (BINDING — d-115, Director order 2026-09-07)

d-098 says a sheet-vs-render drift is fixed by a derived sheet rather than by words. This is its limit, and it was learned the hard way across S42-S45, where the Whisper-Wing's cockpit changed shape between clips and the two riders swapped sides from scene to scene while a correct sheet was attached to every one of them.

**A locked reference is authority ONLY over what it actually depicts.** It says nothing about a view it does not contain and nothing about a state it does not show. Two consequences, both binding:

1. **THE ANGLE RULE.** Before writing a shot, ask whether the attached sheet actually shows the subject *from this shot's camera*. A four-view turnaround covers front, side and back; it does NOT cover an over-the-shoulder from behind and above, a low three-quarter from the flank, or a tight interior. **When a scene needs an angle the sheet does not contain, generate a derived sheet at that angle before generating the clip** (gpt-image-2 with the locked sheet as reference, ~100cr — the same cheap route that produced the bare-wrist, rope-tie and loaded-glider sheets, each of which fixed its drift in one attempt). Do not hope the model will extrapolate the view: it will invent one, and it will invent a different one next scene.

2. **THE STATE RULE.** Attach the sheet that matches the character's state **in this scene**, not the character's default sheet. If the goggles are down in the scene, the goggles-DOWN sheet is the reference; if no such sheet exists, either the scene is written to the state that IS locked, or a derived state sheet is generated first. The same holds for any tracked state — wristwear, carried props, clothing changes. Attaching a sheet that contradicts the scene is the reference conflict d-098 exists to prevent, pointed at your own scene instead of at a neighbour.

**The corollary that catches the subtle failures: a fixture with no depicted geometry is not locked.** The craft's descriptor said "open two-seat cockpit" and never said the seats sit side by side, so scene_direction invented "front cockpit / rear cockpit" and three clips were lost. **Where a sheet cannot settle a relationship, the descriptor must state it in words** — which seat is whose, which side of the vehicle a rider occupies, which hand holds the tool. Pin it to the WORLD (the craft, the set, the other character), never to the frame; the screen side is then derived per camera under d-093, and it stops flipping between clips.

**Cost discipline:** a derived sheet is ~100cr against ~4,000-8,000cr for a rejected clip. When in doubt, generate the sheet.

## The silent performance (BINDING — d-094, extracted from the approved S36 Milo pass)

d-111 already says the listener is directed as deliberately as the speaker. This is the HOW, and it applies hardest to a character who has **no line at all** in the scene: they are not "reacting", they are performing a second, wordless part, and the prompt writes it with the same care as the spoken one. The S36 rule-zero clip is the standard — Milo says nothing for nine seconds and carries half the scene. All five of these, every time:

1. **Give them a named SHARE of the scene, not a reaction beat.** State whose face owns which stretch: *"@milo's face carries the second half."* Screen time that belongs to nobody gets filled with idling.
2. **Write an ARC of at least three stages with a direction of travel** — never one held state: *"taking it in → the protest draining out of his brows → tender resolve arriving."* One adjective is a pose; three stages is a performance.
3. **Locate every stage in a named part of the body** (brows, jaw, mouth corner, shoulders, hands) — this is the d-111 micro-expressions law applied per stage, not restated: emotion words without a body part constrain nothing.
4. **Give them one BORROWED gesture** that echoes the other character: *"his jaw setting the way @gramps's does."* The echo is what makes two people read as related rather than merely co-located — it is the cheapest bond in the vocabulary.
5. **Let them ANSWER with an action instead of a line, written with its own beats** so it lands where a reply would: *"answers without a word: one soft step in, and his hands come down and close on the handle, settling there."* Give the answer a verb chain, never a single verb — the chain is what makes it read as a decision rather than a movement.

Cost: 60–80 words of prompt. It buys the beat the audience remembers, and it is free of the dialogue budget.

## Practicals aimed at the lens earn atmosphere (BINDING — d-095)

Correct staging will regularly point a practical light source at the camera: a lantern, headlamp or glowing fragment aimed at the subjects is, from the establishing camera of that set, also aimed at the lens (the Whisper-Wing's lantern on the box-site's establishing angle is the standing example). **Do not re-aim the source to avoid it** — that breaks the staging (d-093) and silently re-lights the scene — and do not leave it as a bare bright disc. Direct it as a visible beam with something IN the beam:

- fine dust or motes drifting slowly across the shaft;
- a soft warm halation ring around the source, blooming and settling;
- the beam picking out ONE surface it crosses — the lid's engraved letters, a shelf edge, a wing membrane;
- the source partly occluded by a character or prop, so the shaft breaks and re-forms as they move.

Constraints, all phrased positively per d-099: the beam stays warm and cozy — a lantern in a library, never a searchlight or an interrogation lamp; soft halation only, never streak or anamorphic flare (it reads as artifact); the atmosphere never buys darkness — blacks stay lifted per the grade, and a shaft is not a licence for a dark frame; the source holds steady — no flicker, no strobe (photosensitivity + kids' law).

**Budget:** atmosphere is NOT an impact move. It is continuous texture, it does not count against the one-per-scene d-085 budget, and scenes marked "no impact move" still get it.

## Impact moves — the special-effects vocabulary (Director orders d-120, d-085)

Seedance executes in-camera effects well when they're directed as ONE named event, and they hit hardest when they're rare — but not TOO rare: E01 viewer feedback singled out S05A (the ride) and S05B (the frozen fall) as the most-loved moments, so the density is now planned, not left to chance. Full study, anatomy of the two source clips and prompt patterns: **`skills/meta/impact-moves.md`** (BINDING reference). The vocabulary:
- **Speed ramp** — real-time ramping smoothly into super slow motion for one held close-up, then snapping back HARD and instantly. Always: one ramp, a named subject for the slow beat, an instant (never gradual) return. Variant: *ramp on a passing thing* (one bubble / ring / butterfly / spark comes to the lens in slow motion, subjects soft beyond it).
- **Freeze-and-orbit** — time stops mid-action; the camera sweeps a smooth arc around suspended subjects while particles hang crisp and individually readable; then time snaps back. Direct the frozen expressions explicitly.
- **Masked reframe** — a whiteout/flash/occlusion fills the frame and hides a full camera repositioning inside one continuous shot. Variant: **through-the-ring pass** (a diegetic aperture — sound ring, lantern bloom, membrane — wipes the frame).
- **Motivated emotional drift** — the d-118 push-in: the camera eases closer as an emotional beat lands. Everyday grammar; NOT counted against the budget.
- **Rear chase lock** — the camera rides the subject's tail through an action sequence, world rushing past; vertical variant for shafts (plunge / rise-through).
- **Beat-ladder ride** — one continuous take built as 4–6 named physical beats (plunge / skim / swarm / weave / gap / reveal) with the mount in named physics modes, camera position locked (usually rear chase); the ride's single time trick is its ONE impact move, the other beats are physics. The highest-engagement class; ≥2 per episode on the biggest travel scenes.
- **Near-miss gap** — threading a razor-narrow passage, walls blurring inches from the lens, light dipping (never grey, under 2s) then flooding back.
- **Burst-reveal** — from a tight passage into a vast space in one crane-back; the whole world opens at once, the subject becomes a speck.
- **Rack-focus hold** — a foreground particle/object takes the lens and the focus, subjects soften beyond; no time change (the affordable cousin of the slow-mo bubble).
- **Time-snap hold** — the freeze without the orbit: static camera, particles hang crisp, expressions locked, snap.
- **Orbit-in-flight** — a real-time orbit around the moving subject, world wheeling behind.
- **Curved-reflection cameo** — subjects reflected in a bubble/droplet/brass dome, ONLY inside a ramp or rack-focus hold on a curved surface (flat mirrors/puddles stay forbidden).
- **Pinned micro-bridge** — a 4–5s inserted scene between two chained scenes, start and end frames pinned (Director-ordered end_image exception, the S05B precedent), carrying one impact move.

**The budget rule (BINDING): at most ONE impact move per scene**, reserved for the peak moment, never repeating a neighboring scene's move. Cuts (above) are the everyday grammar; impact moves are the exclamation points. The prompt names exactly one effect and states its boundaries (what starts it, what ends it, what must stay crisp).

**The density rule (BINDING, d-085): one impact move every 3–4 scenes of runtime, never in adjacent scenes, the same move never within 5 scenes** — planned at stage 5 as `scene_direction.metadata.impact_plan` and executed here. Action, journey, reveal and hinge scenes carry them; lesson scenes, tableaux and dialogue-stillness scenes carry none. The producer follows the plan; a proposed deviation (adding, moving or dropping a move) goes to the Director at the gate with the reason — never silently.

## Age-blind rule (d-201, with the anchors exemption)

Never describe characters by age in free prose: *boy, girl, child, kid, young, teen, little* and equivalents are forbidden. Describe by **role** (rider, figure, speaker), **clothing**, and **action** — label what they do, never who they are; unnamed figures get functional labels ("a figure in a wool cloak").
**The single exemption (Director ruling 2026-08-17):** locked `identity_anchors` are quoted VERBATIM even where they contain age wording — the cross-episode identity lock outranks the age-blind rule for exactly those quoted phrases and nothing else. New characters' anchors (Luna onward) should be authored age-neutral where possible so the exemption shrinks over time.

## Negative prompts are unreliable (BINDING — d-099, confirmed empirically)

Seedance does not reliably honor "no X" / "zero X" / "without X" for physical scene content — a negative is a far weaker signal than a positive, concrete description of the desired state. Confirmed on S01_C01: a strengthened "zero smoke" clause produced MORE smoke.

- Bad: `no smoke, no haze, no scorch marks` → Better: `the beam ends in a single bright flash; the instant it fades, the apple sits pea-sized in perfectly clear, still air`
- **Camera primitives are the documented exception:** `no cuts, no zoom` works on continuous shots because Seedance treats camera language as a separate instruction channel. Keep those.
- If a locked reference image itself shows the thing being negated, no wording overrides it — fix the reference (derived state sheet, d-098), not the words.
- On a qc-critic regen for physical content: propose a positive rewrite first; escalate rather than iterating negatives indefinitely.

## Similes and metaphors literalize (BINDING — confirmed twice)

Seedance renders comparisons as literal objects: "dust motes **like slow planets**" produced a banded Jupiter (S03); "a liquid amber **cathedral**" produced an actual gothic church inside the lemonade (S05). Direction prose is full of figures — NEVER carry them into a prompt. Translate every simile/metaphor into direct visual description ("sun refracting through the lemonade in tall shafts, bubbles as drifting gold sparks").

## Identity lock (BINDING — this is the consistency mechanism)

- Reference images: locked character sheet views (2–3 per present character, matched to facing direction) + locked environment plate + selected storyboard material. ≤9 total — present-character sheets first.
- **@-mention every reference (d-106):** the ACTIVE REFERENCES block opens the prompt, mapping every attached image by its position in the medias array, with named handles for recurring assets (d-120):

```
ACTIVE REFERENCES
@reference_image_1: this shot's start frame — begin on exactly this image (<what it shows>).
@reference_image_2: the storyboard page — its numbered panels are the authoritative staging, composition and scale; match them.
@gramps: reference image 3 — his character sheet; 100% match, identical design every frame.
@luna: reference image 4 — her character sheet; 100% match throughout.
```

  Then inline: `@gramps kneels at the rear`, `the reveal matches @stomach-cavern`. Handles are stable film-wide.
- **Numbering = the actual medias array order** of THIS call (d-127): with a start frame it is `@reference_image_1`; without one, everything shifts — the block is always derived fresh, never copied. Mandatory pre-submit map: one line per medias entry (`position → role → file → @tag`); any attached media without an @tag, or @tag without media, = do not submit.
- **The start frame is never left unnamed (d-124, 126cr lesson):** always `@reference_image_1 … begin on exactly this image (<content>)`, and the opening beat is written as a BRIDGE from that frame's actual composition — when prose and image disagree, prose wins and the chain breaks.
- Open the character description with an identity-lock block and stack the proven anti-drift phrases: `[identity_lock] The same character — <anchors verbatim> — consistent across all shots, maintain exact appearance from reference image, no deformation, no face morph. Do not alter clothing category or primary color.` Fold in `forbidden_drift` entries (rewritten positively where possible, d-099).
- **Voice lock:** every speaker's locked voice sample attached as `reference_audio` on EVERY clip where they speak. Quoted dialogue drives lips; the reference audio pins the voice. Never generate a speaking clip without it.

## Chained-scene conditioning (BINDING — d-202, supersedes d-112 last-frame chaining)

Every CHAINED scene's generation call attaches, by Director order (2026-08-17):

1. **The last 3 seconds of the previous scene's APPROVED clip** as a `video_references` entry — `scripts/extract_last_seconds.py <clip> -s 3` → media_upload → media_confirm. This is the motion/lighting/state continuity carrier: the model sees how the previous scene actually ENDED (real footage, not a frozen frame). It is @-mentioned like every reference (`@reference_video_1: the final 3 seconds of the previous scene — the opening beat continues this motion, lighting and character state exactly`).
2. **The scene's own promoted Soul-cinema KEYFRAME** (d-200) as an `image_reference` — a **STYLE + COMPOSITION reference, NOT a start frame (d-203)**. @-mention it as such: `@keyframe: the scene's cinematic keyframe — match its look, lighting, palette and composition language; the scene travels through this image, it does not have to open on it.`
3. **The locked reference sheets** — present characters' sheet views + the location plate — as `image_references`.
4. **The picked storyboard PAGE** also rides as an `image_reference` (authoritative staging). The Director has ordered that the keyframe + storyboard combination be CHECKED in production — at each early E02 gate, report how well the clip honored keyframe vs page so the Director can tune what stays attached.
5. **`start_image` — OVERLAP GENERATION is the settled default for continuous seams ([SEAM d-213], resolving d-203's planned A/B; active while `seam_policy.overlap_generation_default` is true).** The 2026-08-19 A/B (S05A→S05B, 144cr, Director-approved) measured the candidates: last-frame-class starts re-stage (start_image infidelity, see the params caveat), tail-only conditioning re-staged worse (diff 51), 2.5 video_extension failed (diff 55 + skipped time), and **one generation started from the frame `overlap_seconds` (3–4s) BEFORE the predecessor's end won decisively** (diff 25.7, same staging, no dead-stop, ended 2× closer to the next pin). The method: `extract_last_frame.py <predecessor> --from-end <overlap_seconds>` → a SHARP, MID-MOTION frame (never the final frame — final frames are the most motion-blurred and compressed) → `start_image`. The generation RE-COVERS the predecessor's final beat plus the scene's own content; the visible boundary then lives INSIDE the clip, and the splice lands on mid-motion footage that exists on both sides. Record `chain_start_offset_s` in the manifest entry. All d-124 laws apply to this start frame — named `@reference_image_1` and described as a MID-MOTION STATE WITH ITS MOTION VECTOR (repo-priority reconciliation: d-124's naming law stands; what the mission's "don't re-describe" rule actually forbids is describing the frame as a static tableau, which freezes motion — so state the motion, not the furniture). New-beat and hinge boundaries keep normal generation (fresh composition is wanted there) with the d-212 direction fields. Flag false → revert to the d-203 default (no start_image; d-202 tail + start_variant framework).

Consequences: the ≤3 video_references budget means the previous-scene tail (item 1) always claims one slot on chained scenes. NOTE (repo priority, open Director check): the d-202 tail reference remains attached alongside the overlap start — the A/B tested them separately, never together; if E02's first chained clips show reference-hijacked composition, dropping the tail on overlap clips is the Director's one-line call.

## Handoff beat (BINDING — d-191, audience feedback: visible cuts between clips)

Chained clips inherit the previous scene's ending via the last-3s video reference (d-202), but audiences still see a jump when prompts don't share MOTION. Every prompt books its last ~1–1.5s as an explicit **handoff beat**, and every chained successor's 0–2s bridge (d-124) continues it:

- **Outgoing clip, final beat:** either (a) the action DECELERATES into a describable settle — exact end pose, gaze direction, residual motion — or (b) for boundaries marked continuous, the exact motion state crossing the cut (what moves, screen direction, energy).
- **Incoming chained clip, 0–2s bridge:** restate the start frame content AND the inherited motion — the first beat continues it before anything new happens. A bridge that poses a moving character static is how seams become visible.
- The `transition_out` in scene_direction (stage-5 boundary motion contract, d-191) is the source of truth; the prompt-writer copies it, never invents it.
- End-frame pins (`end_image`) remain the strongest handoff for hard choreography — when one exists, the handoff beat describes THAT frame.

## Language rules (d-201)

- English only — the source skill's ZH output is ELIMINATED by Director order; never author or submit Chinese prompts.
- Present tense, active voice. Vivid but economical — concrete visual direction, no poetic padding.
- No metadata headers ("Shot 1:", "Beat 2:") — weave transitions into prose.
- Identity is carried by @handles + verbatim anchors, never by bare names or pronouns the model can't resolve ("she", "the same girl").
- No dialogue or on-screen text unless the scene direction provides it; dialogue lines are never paraphrased or translated.
- **Antislop — never use:** breathtaking, stunning, captivating, mesmerizing, awe-inspiring, masterfully, meticulously, exquisitely, beautifully crafted, cinematic masterpiece, visual feast, a symphony of, seamlessly, effortlessly, flawlessly, cutting-edge, state-of-the-art, next-level, rich tapestry, vibrant tapestry, kaleidoscope of, elevate, unlock, unleash, harness, groundbreaking, a testament to, speaks volumes, resonates deeply.

## Camera language appendix (d-201)

**Angles:** low-angle, high-angle, dutch angle, bird's-eye, worm's-eye, eye-level, OTS (over-the-shoulder).
**Focal length:** wide 14–24mm, standard 35–50mm, telephoto 85–200mm, macro.
**Movement:** tracking, dolly-in, dolly-out, crane, pan, tilt, whip-pan, orbit, push-in, pull-back, handheld, Steadicam, aerial.
**Time:** slow-motion, speed ramp, freeze frame.
**Transitions:** smash cut, match cut, whip-pan transition, hard cut, L-cut.

Camera primitives named precisely (dolly/truck/pedestal = translation; pan/tilt/roll = rotation; zoom/rack focus = lens; static = strictly nothing). A shot's camera states its move, speed, and end state; user/Director camera instructions ALWAYS appear in the final prompt.

## Params (via Higgsfield MCP — model id `seedance_2_0`, budget variant `seedance_2_0_mini`)

| Param | Use |
|---|---|
| duration | the scene's `est_duration_seconds` (4–15) |
| aspect_ratio | brief's `aspect_ratio_primary` (auto/16:9/9:16/4:3/3:4/1:1/21:9) |
| resolution + mode | finals: `1080p` (or `4k`) with `mode: std`; drafts: `720p` — or route to `seedance_2_0_mini` (480/720p only) |
| generate_audio | always true (native audio is the moat; independent of audio_references) |
| genre | optional cinematic hint (auto/action/horror/comedy/noir/drama/epic) — set from the brief's genre when it maps |
| bitrate_mode | `high` for the final pick of a scene, `standard` otherwise |
| medias[] roles | `start_image` = predecessor's last frame on the d-203 continuity variant only (keyframe is NEVER the start frame), `end_image`, `image_references` (≤9 images total: Soul keyframe as STYLE reference d-203 + sheets + plate + storyboard page), `video_references` (≤3; slot 1 = previous scene's last-3s tail on chained scenes, d-202), `audio_references` = locked voice samples |
| `end_image` caveat | **Steers, doesn't lock (confirmed S05B):** content arrives, framing may not. Strong destination hint; for frame-exact joins plan to trim the tail or cut on action. |
| `start_image` caveat | **[SEAM d-210] NOT pixel-exact — the old "pixel-exact" claim was FALSE.** Measured on E01: frame 0 of every chained clip differed from its conditioning PNG by mean-luma 22–47 (re-staging, not drift). Vendor-confirmed: ByteDance's Seedance 2.0 tech report (arXiv 2604.14148) scores its own first-frame preservation 2.71/5 (vs Kling 3 Omni 4.31/5) — the model deliberately trades start-frame fidelity for motion. The 2026-08-19 A/B (S05A→S05B, 144cr, Director-approved) confirmed: last-2s video_reference conditioning diff 51 (worse), 2.5 video_extension diff 55 + skipped time, overlap generation diff 25.7 with SAME staging — the winner. **Never rely on start_image for frame-continuity; use overlap generation (see Chained-scene conditioning, d-213).** |
| get_cost | preflight `get_cost: true` before every batch and announce credits |

`mode: fast` / the mini variant trade camera-motion fidelity for cost — never for slow-mo, multi-shot, or dolly-heavy prompts; they are for blockout drafts and QC retries. Record every job_id (and seed, where returned) in `generation_manifest`.

## Anti-drift fallback ladder (when qc-critic returns regen for identity)

1. Re-emphasize the violated anchor at prompt start AND in the camera section; add the drift to negatives (positively phrased where possible).
2. Add/replace a reference view matching the character's facing direction; cull references to the 3 most consistent rather than flooding all 9.
3. Shorten duration (10s → 6s) and simplify the shot plan (fewer cuts).
4. Escalate (bad start frame or impossible direction is upstream's problem — say so).

## Avoid table

| Don't | Why |
|---|---|
| 4+ simultaneous character actions | motion coherence breaks — split shots |
| >3 characters tracked across cuts | engine limit — name the acting pair per shot |
| Readable text/logos in-clip | unreliable rendering — captions belong to stage 10 |
| Two characters speaking in one breath | lipsync drift — alternate speaker beats |
| Emotion labels without visible physics | "sad" constrains nothing; "tears on cheek, shoulders slumped" renders |
| Names/pronouns as identity ("she", "the same girl") | the model never saw the cast list — @handles + anchors only |
| Reflection shots (mirrors, blades, puddles) | Seedance breaks scene geography on reflections |
| Exit + re-entry in one continuous shot | exit-frame = implicit cut; the character is gone |
| Age words outside verbatim anchors | d-201 age-blind rule |
| Antislop vocabulary | reads as filler; see Language rules |

<!-- adapted from OpenMontage seedance-2-0 pack + video-gen-prompting handbook (research extraction, 2026-07-09); merged with the Director-supplied Seedance 2.0 Universal Director skill (d-201, 2026-08-17) -->
