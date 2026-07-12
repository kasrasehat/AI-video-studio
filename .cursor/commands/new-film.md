---
description: Start a new film production — init the workspace and begin conversational intake
argument-hint: [slug] [--dry-run]
---

Start a new film production.

1. Read `AGENT_GUIDE.md` if you haven't this session (Rule Zero).
2. Derive a kebab-case slug from `$ARGUMENTS` (or from the user's idea once given; ask if empty and no idea is offered). If `--dry-run` is present, pass it through.
3. Initialize: `.venv/Scripts/python scripts/checkpoint.py init <slug> --title "<working title>" [--dry-run]`
4. Read `skills/stages/executive-producer.md` and `skills/stages/01-intake-director.md`, then begin the intake conversation — one question at a time, starting from the user's story idea.
