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
5. **QA loop (blocking):** dispatch `qa-reviewer` with scene_direction + scene_list + brief + this stage's `review_focus` from pipeline.yaml. Apply every critical's proposed_fix (yours to apply directly, or re-dispatch the affected scene's director when the fix is creative). Update `qa.rounds`; keep the final round's report as `artifacts/qa_review_directing.json`. Max 3 rounds; unresolved criticals go to the gate labeled as such — never buried.
6. **Write + validate both artifacts,** attach to the checkpoint, gate.

## Gate presentation

Global look first (palette swatches as hex list + one line each for grade/lensing/movement grammar + the design read), then a per-scene table: scene | framing | camera move | lighting idea | mood | transition out. QA verdict + what was fixed. Options: approve / notes on the look / notes on specific scenes / abort. Scene-level notes re-dispatch only THOSE scenes' directors, then a fresh QA round on the changed scenes.

## Pitfalls

- Letting parallel directors invent four different visual dialects — the global block and taste profile exist precisely so scene direction varies in CONTENT, not in language of style.
- Compound camera moves surviving into the artifact (the #1 clip-generation killer — QA hunts them, but don't rely on QA for what assembly can catch).
- Palette stated as adjectives ("warm tones") instead of hexes + name.
- Directing transitions as an afterthought — stage 10 executes `transition_out` literally.
