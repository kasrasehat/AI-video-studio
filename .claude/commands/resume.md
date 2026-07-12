---
description: Resume a production from its last checkpoint
argument-hint: <slug>
---

Resume production `$ARGUMENTS`.

1. Read `AGENT_GUIDE.md` if you haven't this session.
2. Run `.venv/Scripts/python scripts/checkpoint.py next $ARGUMENTS` and TRUST its output over any conversation memory (see `skills/meta/checkpoint-protocol.md` → Resume protocol).
3. If the next stage is `awaiting_human`: re-present that stage's gate summary and stop for the Director's verdict.
4. Otherwise read the stage's director skill and continue — from the first unit NOT in `partial_progress.completed_unit_ids` if partial progress exists.
