---
description: Start the next episode of an existing series — canon and format inherited from the series bible
argument-hint: <series-slug> [episode-slug]
---

Start the next episode of series `$ARGUMENTS`.

1. Read `AGENT_GUIDE.md` if you haven't this session (Rule Zero), then `skills/meta/series-continuity.md` (BINDING).
2. Read `projects/_series/<series_id>/series_bible.json` + the previous episode's bible entry (`continuity_notes`, `divergences`) BEFORE asking anything.
3. `checkpoint.py init <episode-slug>`, add the `series` block to the episode's `project.json`, register the episode `in_production` in the bible (archive → edit → validate).
4. Delta-only intake per the continuity skill: show the Director the inherited format block for confirmation, then ask only for this episode's story idea, title, and any overrides (log overrides + bible `divergences`).
5. Run the normal 12-stage pipeline (`skills/stages/executive-producer.md` → `01-intake-director.md`). At stages 6–7, IMPORT canon (descriptors verbatim, assets pre-locked at zero cost) and generate only what is new. At episode close, update the bible (promote new canon, episode `complete`, next-episode continuity notes).
