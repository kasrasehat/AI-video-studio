# Scene Recheck Director — stage 4

> STATUS: stub — full version lands at M3.

## IO contract (from pipeline.yaml)
- Consumes: `scene_list` (from stage 3), `story`.
- Produces: `artifacts/scene_list.json` finalized (`recheck.performed=true, final=true`, honest `dedupe_report` + `fixed_issues`). Gate: Director approves the scene list.

## Shape of the full skill (M3)
FRESH read (do not trust stage 3's framing): compare every scene against the full story — merge/cut repeated or near-duplicate scenes, fill coverage gaps, reconcile continuity fields (time_of_day, location_ref, characters_present) scene-to-scene, rebalance durations. Archive the stage-3 version to history/ before rewriting.
