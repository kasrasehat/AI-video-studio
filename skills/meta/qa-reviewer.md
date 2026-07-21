# QA Reviewer Protocol

How the mandatory QA loops (stages 2, 5, 6, 9, 10 per `pipeline.yaml`) actually run. The `qa-reviewer` / `qc-critic` agents execute reviews; this protocol governs both them and the executive producer running the loop. Output schema: `qa_review` (criticals REQUIRE `proposed_fix` — schema-enforced).

## The three critique rules (binding, from CHAI findings)

1. **Accurate** — every finding cites a concrete location: an artifact field path, scene_id, frame_id, or timestamp. "The direction feels weak" is not a finding; "scenes[S04].camera_movement combines dolly + pan + tilt" is.
2. **Complete** — one instance found → hunt the entire class before returning. One impossible camera move means every scene's camera move gets rechecked THIS round, not next round.
3. **Constructive** — every critical carries a fix concrete enough to apply without asking the reviewer anything. A fix that says "make it better" fails the schema's spirit even when it passes its letter.

## Severity calibration

| Severity | Meaning | Effect |
|---|---|---|
| **critical** | Would visibly damage the film or break a downstream stage | Blocks: verdict must be `fix_and_rereview` |
| **suggestion** | Would measurably improve it | Shown at the gate; apply when cheap |
| **investigation** | Real concern, not yet pinpointed — says where to look | Shown at the gate honestly |
| **nitpick** | Taste | Never blocks, never argued about |

Calibration anchors: an ambiguous identity anchor is CRITICAL (it multiplies into clip regens); a geometrically impossible trajectory or a sourceless entering object is CRITICAL (it forces downstream agents to silently violate half the direction — the S14 class, d-082); a flat lighting choice at the emotional peak is a SUGGESTION; "S07 pacing feels off but I can't say why" is an INVESTIGATION.

## Trajectory audit (binding — added d-084)

For any artifact containing blocking or motion (scene_direction above all): RECONSTRUCT each scene's spatial diagram from its text — every named element placed on the location's relative-position map, every motion traced source → path → target in screen space. Flag as CRITICAL:
1. A trajectory whose endpoints contradict its stated screen direction (a "left-to-right sail across the room" that starts and ends frame-left).
2. An entering object/effect/character with no established source and no stated dramatic reason for hiding it.
3. An exit/entry vector mismatch across consecutive scenes wherever the transition implies continuity.

The S14 contradiction (sneeze source hidden without justification AND source + target both frame-left of a stated crossing path) shipped through this review because no reviewer drew the diagram. Drawing it is now mandatory, not optional — reading the prose and nodding is exactly how it slipped through.

## Running the loop (executive producer)

1. Dispatch the reviewer with: the artifact under review, its upstream sources, and the stage's `review_focus` bullets from pipeline.yaml — those bullets are the PRIMARY rubric; the reviewer's own expertise extends but never replaces them.
2. Write each round's report to `artifacts/qa_review_<stage>.json` (archive the previous round to `history/`).
3. `fix_and_rereview` → apply every critical's proposed_fix — directly when mechanical, via the producing role agent when creative — then re-dispatch the reviewer. The re-review checks the FIXES and re-scans the class; it does not re-litigate settled findings.
4. Respect `max_rounds`. At the cap with criticals still open: STOP and present them at the gate labeled "unresolved after N QA rounds" — the Director decides. Self-certifying past a blocking loop is a contract violation.
5. An empty-findings `pass` on round 1 of a large artifact deserves one skeptical spot-check by the producer before trusting it.

## Reviewer conduct

No praise padding, no restating the artifact, no softening criticals to be polite. If the work is genuinely clean, an empty findings list with verdict `pass` is a legitimate and welcome result — manufactured findings to look thorough are as corrosive as missed ones.
