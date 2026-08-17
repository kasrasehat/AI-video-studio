# Directing Director — stage 5

Give every scene professional direction — global look first, then per-scene camera/lighting/blocking — with a blocking QA loop before the Director sees it. This stage decides what the film LOOKS like; stage 8 and 9 execute exactly what is written here.

**Consumes:** `scene_list`, `brief`. **Produces:** `artifacts/scene_direction.json` + `artifacts/qa_review_directing.json`.
**QA loop:** `qa-reviewer`, max 3 rounds, BLOCKING. **Parallel:** `director` per scene, ≤4. **Gate:** Director approves. **Resume unit:** scene.

## Process

1. **Derive the taste profile first** (read `skills/meta/taste-direction.md`): design read, dials, palette discipline, anti-patterns — from the brief. Store it in `scene_direction.metadata.taste_profile`. This is the creative contract every later choice must survive.
2. **Author the `global` block yourself** (it needs one mind, not a committee): `color_palette` (name + 3–5 hexes serving the design read), `grade`, `lensing`, `movement_grammar`. Each must trace to brief style/tone/references — if you can't say why, it's decoration.
3. **Dispatch `director` per scene** (Claude Code: up to 4 in parallel; else sequential). Each gets: the global block + taste profile, its scene(s) from scene_list, the brief path. `--unit-done <scene_id>` as each returns; `--total-units <N>` upfront.
   - Give each director its NEIGHBOR scenes' summaries too (previous + next) — transitions and light progression need context.
4. **Assemble** `scene_direction.json`; reconcile seams yourself: 180° axes consistent per location across scenes directed in parallel; light progresses with time_of_day; `transition_out` of scene N sensible against the opening of scene N+1; palette_overrides justified. Set `qa: {rounds: 0}` for now.
4a. **Engagement audit (BINDING — Director order d-111; §4a–4c are the CANONICAL home of these laws, d-194 — the director role file and the QA protocol point here and restate nothing):** before dispatching QA, sweep the assembled direction for the four engagement principles:
   - **Dynamism:** a locked camera never excuses a static scene — every scene's blocking must carry visible motion energy (performance beats, business, an energy line that builds or turns). If nothing moves but mouths, re-direct the scene.
   - **Camera variety:** one camera idea per scene stays law, but the FILM must vary its eye. Build a setup table across all scenes (shot size | height | angle | move) and check it like a melody: consecutive scenes at one location never reuse the same setup class without a stated reason; low, high, over-shoulder, POV, macro and wide each appear where the story earns them; the story's biggest moments deserve the frame's boldest geometry. A film shot entirely at one eye-level medium-wide is coverage, not direction.
   - **Density of life:** every scene where characters share the frame carries conversation or a stated reason for its silence; frames hold small believable business (hands doing things, background alive) — detail is what makes a world feel inhabited rather than staged.
   - **Performance variety:** each scene's blocking/mood names the FACES per beat — what each character visibly feels, and how it changes across the scene. Direct the listener as deliberately as the speaker; reaction is half of every conversation.
4b. **Spatial sanity audit (BINDING — added d-084 after the S14 contradiction shipped through every review layer):** before dispatching QA, reconstruct each scene's stage diagram from its own text — place every named element on the location's relative-position map, then trace every stated motion as source → path → target in screen space. Three checks, all must pass:
   - **Trajectory consistency:** a stated screen direction must agree with its own endpoints. A "left-to-right" path cannot start and end on the same side (S14's comet was directed to launch frame-left, "sail left-to-right across the kitchen," and land at a pitcher pinned frame-left — geometrically impossible, and both storyboard artists silently violated a different half of it).
   - **Causal visibility:** anything that ENTERS frame (object, effect, character) has a source, and the direction explicitly decides whether that source is on screen. Hiding a cause the audience needs requires a stated dramatic reason (S14 hid the sneeze itself with no reason — the film cut from inside a nose to a comet arriving from nowhere).
   - **Cross-boundary motion match:** scene N's exit vector equals scene N+1's entry vector in screen space wherever the transition implies continuity.
   A scene failing any check is re-directed BEFORE QA — the audit is yours, not the reviewer's safety net.
4c. **Boundary motion contract (BINDING — d-191, audience feedback: visible cuts read as unnatural):** every scene's `transition_out` is written against its ACTUAL next scene (the d-158 neighbor-bound rule, generalized from insertions to ALL boundaries) and must name BOTH sides of the seam: (a) the exit motion state — what is physically moving, in which screen direction, at what energy, on the scene's final beat (or "settled hold" if the action resolves); (b) the absorption — how the next scene's opening beat continues, receives, or deliberately breaks that motion. "Cut to next scene" is not a transition; it is the absence of one. Continuous-action boundaries must hand off a motion vector; new-beat boundaries must state the settle-then-cut rhythm; only location hinges may hard-reset, and even they choose an energy match (an S13 sneeze-launch cuts to a fast entry, not a still room).
5. **QA loop (blocking):** dispatch `qa-reviewer` with scene_direction + scene_list + brief + this stage's `review_focus` from pipeline.yaml. Apply every critical's proposed_fix (yours to apply directly, or re-dispatch the affected scene's director when the fix is creative). Update `qa.rounds`; keep the final round's report as `artifacts/qa_review_directing.json`. Max 3 rounds; unresolved criticals go to the gate labeled as such — never buried.
6. **Write + validate both artifacts,** attach to the checkpoint, gate.

## Gate presentation

Global look first (palette swatches as hex list + one line each for grade/lensing/movement grammar + the design read), then a per-scene table: scene | framing | camera move | lighting idea | mood | transition out. QA verdict + what was fixed. Options: approve / notes on the look / notes on specific scenes / abort. Scene-level notes re-dispatch only THOSE scenes' directors, then a fresh QA round on the changed scenes.

## Pitfalls

- Letting parallel directors invent four different visual dialects — the global block and taste profile exist precisely so scene direction varies in CONTENT, not in language of style.
- Compound camera moves surviving into the artifact (the #1 clip-generation killer — QA hunts them, but don't rely on QA for what assembly can catch).
- Palette stated as adjectives ("warm tones") instead of hexes + name.
- Directing transitions as an afterthought — stage 10 executes `transition_out` literally.
- Defaulting every scene to the same safe setup (eye-level medium-wide, locked static) — safety repeated seventeen times is monotony; the d-111 setup table exists to catch it before the Director does.
- An internally unsatisfiable direction (source and target on the same side of a stated crossing path; a hidden cause the audience needs). Downstream agents will silently pick which half to violate rather than reporting the contradiction — it cost a full boarding round on S14 (d-082) before the Director caught what four review layers missed.
