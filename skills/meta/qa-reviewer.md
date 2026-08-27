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

## Engagement audit (binding — Director order d-111)

For story, scene-division and directing artifacts, hunt flatness as a first-class defect class alongside correctness:
1. **Monotone coverage** — three or more consecutive scenes sharing the same setup class (size + height + angle + move) without a stated rhyme: CRITICAL on scene_direction (it compounds into a visually monotonous film no clip-level fix can rescue).
2. **Unearned silence** — characters sharing a frame with no dialogue AND no stated reason for the silence in the beat/scene: SUGGESTION per scene, CRITICAL when it spans a consecutive stretch (a talking film that falls mute drops its audience).
3. **Single-expression scenes** — a scene whose blocking/mood names no facial emotion, or names one flat state for all beats and characters: SUGGESTION; CRITICAL at an emotional peak (the audience reads faces before anything else).
4. **Static life** — blocking where nothing moves but the mouths: SUGGESTION, paired with a concrete business/motion proposal in the fix.

## Comprehension audit (binding — added d-191 after real viewers lost the plot)

For story, scene_list and scene_direction: perform the **naive retell test** — reconstruct the entire narrative using ONLY what a first-time viewer will see and hear, in order. Flag as CRITICAL:
1. A world/location entry or exit whose mechanism is off-screen, split across cuts such that cause and effect never appear together, or inferable-only (the E01 bug: viewers could not say how the heroes got inside Grandma — the cookie-dunk-swallow chain never played as one legible on-screen sequence).
2. A plot-critical object or character whose first appearance does the story work before the audience has been shown what it is.
3. Any step of the retell that requires author knowledge to complete ("she must have drunk it").
The proposed_fix must name the missing on-screen beat, not a caption or dialogue patch-over. Runtime pressure is never an accepted reason — mechanism beats outrank gags (stage-2 skill, causal clarity law).

Additionally, grade **conversation density** (d-191, raises the d-111 bar): compute exchanges per dialogue-capable beat/scene; a stretch of 2+ consecutive company-beats carried by single lines or silence without stated reason is CRITICAL; a story averaging under ~2 exchanges per dialogue-capable beat gets a CRITICAL on the artifact as a whole.

## Trajectory audit (binding — added d-084; check definitions canonical in stage-5 skill §4b, d-194)

For any artifact containing blocking or motion (scene_direction above all): RECONSTRUCT each scene's spatial diagram from its text — then apply the three checks exactly as written in `skills/stages/05-directing-director.md` §4b (trajectory consistency, causal visibility, cross-boundary motion match). Any failure is CRITICAL.

The S14 contradiction (sneeze source hidden without justification AND source + target both frame-left of a stated crossing path) shipped through this review because no reviewer drew the diagram. Drawing it is mandatory, not optional — reading the prose and nodding is exactly how it slipped through.

## Stage hunting grounds (moved here from the agent role file, d-194)

- **story (as refiner backup):** logic holes, length math, genre-emotion mismatches; the comprehension and conversation-density audits above (law text canonical in the stage-2 skill, "The room's laws").
- **directing:** compound camera moves; framing without positions; 180° violations across same-location scenes; palette drift without stated reason; transitions that fight the scene rhythm or lack the boundary motion contract (stage-5 skill §4c); PLUS the trajectory audit above — mandatory.
- **lock-descriptors:** anchors that are not verbatim-promptable ("kind eyes" — unpromptable; "large dark-brown eyes" — promptable); static/dynamic misfiling (clothing in static_features is a classic); characters_present in any scene that resolve to no char_id; speakers without voice_spec; missing forbidden_drift for known model failure modes (long hair, palette flips).

## Running the loop (executive producer)

1. Dispatch the reviewer with: the artifact under review, its upstream sources, and the stage's `review_focus` bullets from pipeline.yaml — those bullets are the PRIMARY rubric; the reviewer's own expertise extends but never replaces them.
2. Write each round's report to `artifacts/qa_review_<stage>.json` (archive the previous round to `history/`).
3. `fix_and_rereview` → apply every critical's proposed_fix — directly when mechanical, via the producing role agent when creative — then re-dispatch the reviewer. The re-review checks the FIXES and re-scans the class; it does not re-litigate settled findings.
4. Respect `max_rounds`. At the cap with criticals still open: STOP and present them at the gate labeled "unresolved after N QA rounds" — the Director decides. Self-certifying past a blocking loop is a contract violation.
5. An empty-findings `pass` on round 1 of a large artifact deserves one skeptical spot-check by the producer before trusting it.

## Reviewer conduct

No praise padding, no restating the artifact, no softening criticals to be polite. If the work is genuinely clean, an empty findings list with verdict `pass` is a legitimate and welcome result — manufactured findings to look thorough are as corrosive as missed ones.
