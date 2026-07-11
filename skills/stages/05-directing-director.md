# Directing Director — stage 5

> STATUS: stub — full version lands at M3.

## IO contract (from pipeline.yaml)
- Consumes: `scene_list`, `brief`.
- Produces: `artifacts/scene_direction.json` + `artifacts/qa_review_directing.json`.
- QA loop: `qa-reviewer`, max 3 rounds, BLOCKING on critical findings. Gate: Director approves direction.
- Parallel: `director` subagent per scene (max 4) under Claude Code; sequential elsewhere. Resume unit: scene.

## Shape of the full skill (M3)
Establish global look first (palette hexes + name, grade, lensing, movement grammar — informed by `skills/meta/taste-direction.md`), then direct each scene: ONE executable camera move per 15s clip, concrete lighting, blocking that respects the 180° line and continuity_notes, directed `transition_out` (consumed by stage 10). Mandatory qa-reviewer loop before the gate.
