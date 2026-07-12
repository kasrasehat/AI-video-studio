---
description: Show a production's stage-by-stage progress
argument-hint: [slug]
---

Show production status.

1. If `$ARGUMENTS` is empty, list the directories under `projects/` and ask which one (or show all, if few).
2. Run `.venv/Scripts/python scripts/checkpoint.py status <slug>` and relay the table.
3. Add one sentence: what the pipeline is waiting on right now (Director approval? next stage? a blocked unit?) and the cost so far if checkpoints carry cost snapshots.
