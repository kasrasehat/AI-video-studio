# Checkpoint Protocol

Binding contract for state persistence and Director gates. `pipeline.yaml` decides WHICH stages gate; this skill defines HOW. The enforcement lives in `scripts/checkpoint.py` — never write checkpoint files by hand.

## The cycle for every stage

1. **Enter** → `python scripts/checkpoint.py write <slug> <stage> --status in_progress`
   (signals liveness; on long stages do this BEFORE the first expensive call).
2. **Work** the stage per its director skill. After each finished unit on long stages (scene directed, element generated, storyboard variant done, clip rendered):
   `... write <slug> <stage> --status in_progress --unit-done <ID> [--total-units N]`
3. **Attach artifacts** as they finalize:
   `... write <slug> <stage> --status in_progress --artifact <name>=artifacts/<name>.json`
   The script validates each artifact against its schema and records a sha256. Fix validation errors immediately — an invalid artifact must never survive to a gate.
4. **Gate** (stages with `human_approval_default: true`):
   `... write <slug> <stage> --status awaiting_human` → present to the Director (see format below) → **END YOUR TURN**.
5. **On the Director's reply:**
   - Approve → `... write <slug> <stage> --status completed --approved`
   - Feedback → revise per the stage skill (archive-then-rewrite artifacts, see below), re-run the stage's QA loop, go back to step 4. Count the round; `orchestration.max_revisions_per_stage` caps it — after that, summarize the impasse honestly instead of looping.
   - Abort → `... write <slug> <stage> --status failed --note "<reason>"`
6. **Non-gated stages** → `... write <slug> <stage> --status completed` directly.

The script exits 2 with `GATE VIOLATION` if you try to complete a gated stage without `--approved`. That exit is never a bug to work around — it is the system working.

## Gate presentation format

```
## Stage complete: <stage> — awaiting your approval

### What was produced
<key content summary — logline, scene count, palette, variant counts…>
<file paths the Director should open / gallery link>

### QA
<qa_review verdict, rounds used, notable findings and how they were fixed>

### Cost
<stage cost + production total so far>

### Your options
approve · give notes (I'll revise) · abort
```

Keep it scannable. Never bury the thing the Director actually needs to look at.

## Revision hygiene

- Before rewriting an artifact during a revision, copy the current version into `history/` (the CLI archives checkpoints automatically, but the artifact file itself is yours to archive: copy `artifacts/story.json` → `history/story_<timestamp>.json`, then rewrite).
- Every revision logs a decision: `checkpoint.py log-decision <slug> --stage <stage> --category other --subject "revision round N" --selected "<what changed>" --reason "<Director's note>" --decided-by user`.
- A Director approval is itself a decision: category `gate_approval`, decided_by `user`.

## Resume protocol

On `/resume`, a fresh session, or any doubt: `python scripts/checkpoint.py next <slug>` and trust its output over conversation memory. If it reports partial progress, continue from the first unit NOT in `completed_unit_ids` — never regenerate finished units without an explicit Director request.

## Invalidation on upstream change

If the Director changes an already-completed upstream artifact (e.g. edits the story after scenes exist), downstream stages are stale: say so explicitly, list what must re-run, get confirmation, then re-enter the earliest affected stage (its checkpoint returns to `in_progress`; superseded versions are archived automatically). Never leave a stale artifact silently in play.
