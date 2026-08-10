---
description: Found a new series — create the series bible, then start episode 1 (or adopt a finished film as episode 1)
argument-hint: [series-slug]
---

Found a new series.

1. Read `AGENT_GUIDE.md` if you haven't this session (Rule Zero), then `skills/meta/series-continuity.md` (BINDING).
2. Derive a kebab-case series slug from `$ARGUMENTS` (ask if empty). Series-level intake with the Director: title (mark `title_locked` honestly), premise (the show's engine), and the `format` defaults every episode inherits.
3. Write `projects/_series/<series_id>/series_bible.json` (schema `series_bible`; create the sibling `history/`). Canon starts empty unless adopting.
4. **Adopting a finished film as episode 1:** build `canon`/`voice_presets`/`laws` from its approved artifacts (`asset_manifest` locked picks, `lock_descriptors`, decision log), register it `complete` with `continuity_notes` — touch nothing inside the finished production.
5. Otherwise register episode 1 as `planned` and continue as `/new-episode` for it.
