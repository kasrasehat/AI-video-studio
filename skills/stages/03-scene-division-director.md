# Scene Division Director — stage 3

> STATUS: stub — full version lands at M3.

## IO contract (from pipeline.yaml)
- Consumes: `story`, `brief`.
- Produces: `artifacts/scene_list.json` (schema `scene_list`, `recheck.final=false`). No gate — flows into stage 4.

## Shape of the full skill (M3)
Run `scene-splitter` subagent: split the story into ≤15s scene units (Seedance clip length); dialogue lines live INSIDE their scene (native lipsync); every scene carries beat_refs, location_ref, characters_present, time_of_day, continuity_notes, transition_out_hint. Self-check: full beat coverage, durations, speakers listed.
