# Story Director — stage 2

Run the writers' room: Writer drafts → Refiner re-reads and repairs → the Director (user) accepts or gives notes, looping until accepted.

**Consumes:** `brief`. **Produces:** `artifacts/story.json` (schema `story`).
**QA loop:** `refiner`, min 1 round, blocking. **Gate:** Director accept/comment loop.

## Process

1. **Dispatch `writer`** with the project dir + path to `artifacts/brief.json`. It returns a draft story JSON (`revision.round=1, changed_by=writer`) + one paragraph of intent.
2. **Dispatch `refiner`** with the brief path + the draft (write the draft to `artifacts/story.json` first so the refiner reads the real file). This round is MANDATORY even if the draft looks perfect — fresh eyes are the point. It returns the revised story (`round=2, changed_by=refiner`, honest `change_notes`) + `remaining_risks`.
3. **Sanity-check before the gate** (you, not the agents):
   - `estimated_runtime_seconds` within the brief's duration target ±10%; beats sum to it.
   - Every beat has a real `emotional_note`; the emotional arc actually progresses.
   - Cast size filmable (≤4 named characters for a 2–3 min film; be skeptical above that).
   - `content_boundaries` respected; language matches the brief.
   - Schema-valid (`validate_artifact.py artifacts/story.json`). Fix or re-dispatch on failure.
4. **Gate.** Present: title + genre, the synopsis, the beat map (one line per beat: summary → emotion → seconds), the full story text, WHAT THE REFINER CHANGED (from change_notes — the Director should see the room's work), and `remaining_risks`. Options: accept / give notes / abort.
5. **On Director notes:** route them through `refiner` (notes verbatim in the prompt; `changed_by` stays `refiner`, round increments, change_notes describe the response to each note). Archive the prior `story.json` to `history/` first. Re-run step 3, re-gate. Log each revision round as a decision (`--decided-by user`, their note as the reason). Cap: `max_revisions_per_stage` (3) — then present the impasse honestly.

## Judgment calls that are yours (not the agents')

- If writer and refiner disagree structurally (refiner's remaining_risks contradicts the draft's core), surface BOTH views at the gate rather than silently picking.
- If the Director's note would break the brief (e.g. doubles the runtime), say so before executing — propose honoring the note AND amending the brief, their call. An amended brief = re-approve the brief (stage 1 checkpoint superseded) before continuing.

## Pitfalls

- Skipping the refiner because the draft "reads well" — the mandate exists for the failure you can't see.
- Presenting only a summary at the gate: the Director must be able to read the ACTUAL story text.
- Letting change_notes say "improved flow" — they must name concrete changes or the audit trail is theater.
