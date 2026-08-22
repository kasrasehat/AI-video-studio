# Scene Recheck Director — stage 4

A FRESH read of the scene list against the full story: dedupe, fill gaps, reconcile continuity, rebalance. Then the Director approves the final list — the last cheap moment to fix structure before direction, assets and clips are built on it.

**Consumes:** `scene_list` (stage 3), `story`. **Produces:** `artifacts/scene_list.json` finalized (`recheck: {performed:true, final:true, dedupe_report, fixed_issues[]}`). **Gate:** Director approves.

## Why fresh eyes (binding)

The rechecker must NOT be the stage-3 context. Dispatch a NEW `scene-splitter` instance with a recheck mission — it receives the scene list + FULL story + brief and judges the split as an outsider. Same output contract, different mandate:

> "You did not write this scene list. Re-read the full story first, then audit the list against it: (1) merge or cut repeated/near-duplicate scenes (same dramatic job twice = one scene); (2) find story moments that got lost — add scenes only if a beat is genuinely uncovered; (3) reconcile continuity: time_of_day arcs, location_refs stable, characters_present complete, continuity_notes consistent with what the PREVIOUS scene established; (4) rebalance durations toward the brief target ±10% by trimming padding, never by squeezing dialogue; (5) re-verify every stage-3 rule (duration ceiling, speakability, coverage, generatability); (6) [SEAM d-211] audit the BOUNDARIES: every boundary classified (`boundary_class_out`), landing on an action articulation with a motion-onset `head_action`; every continuous boundary carries `overlap_from`/`overlap_seconds`; hinges carry the three-beat design; no dialogue straddling a boundary. Return the FINAL list with recheck.performed=true, final=true, an honest dedupe_report, and fixed_issues[] naming every change."

**Boundary enforcement ([SEAM d-211], active while `config/seam_policy.yaml` flag `boundary_classes_required` is true):** REJECT a scene list containing an unclassified boundary, or a `continuous` boundary without an overlap plan — send it back to the rechecker with the offending boundaries named. With the flag false, boundary fields are advisory (pre-d-211 behavior).

## Process

1. Archive the stage-3 version: copy `artifacts/scene_list.json` → `history/scene_list_<timestamp>.json`.
2. Dispatch the recheck mission (above) → receive the final list.
3. **Verify the recheck was real:** if `fixed_issues` is empty AND `dedupe_report` says "no issues", spot-check 2–3 scenes against the story yourself — an empty recheck on a first-pass split is suspicious more often than it's true. If you find something, re-dispatch with it named.
4. Write + validate; `write <slug> scene-recheck --status in_progress --artifact scene_list=artifacts/scene_list.json`.
5. **Gate.** Present: scene table (id | duration | type | one-line job | dialogue?), total runtime vs target, the dedupe_report, fixed_issues, and any flagged generatability risks. Options: approve / edit specific scenes (notes route back through a recheck dispatch) / abort.

## Pitfalls

- Letting the rechecker "improve" scenes stylistically — its job is structure and continuity, not taste (taste is stage 5).
- Merging scenes past 15 seconds to reduce count.
- Accepting a recheck that only praised the input — demand the audit, not the compliment.
