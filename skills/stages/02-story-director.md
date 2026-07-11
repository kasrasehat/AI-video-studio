# Story Director — stage 2

> STATUS: stub — full version lands at M3.

## IO contract (from pipeline.yaml)
- Consumes: `brief`.
- Produces: `artifacts/story.json` (schema `story`).
- QA loop: `refiner` agent, ≥1 round, blocking. Gate: Director accept/comment loop.

## Shape of the full skill (M3)
Run `writer` subagent (drafts from brief: beats sized to duration) → `refiner` subagent (adds detail, fixes broken logic, injects genre-appropriate emotion, trims/pads to length; emits change_notes) → present story + what the refiner changed → gate. On Director notes: revise via refiner, re-gate.
