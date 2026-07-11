# QA Reviewer Protocol

> STATUS: stub — full version lands at M3. The severity contract below is already binding
> because `qa_review.schema.json` enforces it.

Used by the QA loops declared in `pipeline.yaml` (stages 2, 5, 6, 9, 10). Output: an `artifacts/qa_review_<stage>.json` per round (schema `qa_review`).

## Severity contract
- **critical** — blocks the gate; MUST carry `proposed_fix`. Fix, then re-review.
- **suggestion** — should fix; Director sees it at the gate either way.
- **nitpick** — may fix; never blocks.
- **investigation** — real concern, not yet pinpointed; surface it honestly.

## Review rules (full version at M3)
Accurate (every finding points at a concrete field/scene/frame), complete (found one issue → scan for its whole class), constructive (criticals propose the fix). Respect `qa_loop.max_rounds`; after the cap, report the impasse to the Director instead of looping.
