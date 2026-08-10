# Series Continuity — BINDING

How episodes of a series share canon without re-arguing or re-buying it. A series is a **bible** (`projects/_series/<series_id>/series_bible.json`, schema `series_bible`, archived to a sibling `history/` on every edit) plus ordinary episode productions (`projects/<slug>/`, full 12-stage pipeline, unchanged). The pipeline is NOT restructured for series — continuity lives in what flows into stage 1 and stage 7 and what flows back out at episode close.

## Entry points

- **`/new-film`** — standalone film, no bible, exactly as before.
- **`/new-series`** — founding a series. Run series-level intake (title, premise, format defaults), write the bible with episode 1 `planned`, then proceed as `/new-episode` for episode 1. A completed standalone film may also be RETROACTIVELY founded as episode 1 (micro-explorers precedent): build the bible from its approved artifacts; nothing in the finished episode is touched.
- **`/new-episode`** — next episode of an existing series. The rest of this file is mostly about this path.

## Episode start (stage 1 with a bible)

1. Read the bible FIRST — before any intake question. Also read the previous episode's `episodes[]` entry (`continuity_notes`, `divergences`) and, for writing stages later, its `brief` + `story` artifacts.
2. `checkpoint.py init <episode-slug>` as usual; then add to the episode's `project.json`: `"series": {"series_id": "<id>", "episode_number": N}`.
3. Intake is DELTA-ONLY: the bible's `format` pre-fills audience/language/style/tone/platform/aspect/duration; ask the Director only for (a) this episode's story idea, (b) title, (c) any overrides. **An override is legal and Director's right** — log it as a decision AND append it to the bible episode entry's `divergences`. Never silently diverge; never argue against an ordered divergence.
4. The episode `brief` is written in full (schema unchanged) — inherited values are copied in, with `metadata.inherited_from_series: true` on the brief.
5. Register the episode in the bible (`status: in_production`) at init.

## Canon import (stages 6–7)

6. **Descriptors:** for every canon element appearing in this episode, copy its `lock_descriptors` entry VERBATIM from the source episode (the bible's `source_episode_slug` says where; that episode's lock_descriptors is the descriptor of record). Identity anchors never drift between episodes without a Director-approved unlock logged in BOTH the episode decision log and the bible.
7. **Assets:** stage 7 imports canon elements as pre-locked `asset_manifest` entries — same `element_id`, the locked sheet/plate/voice files and `media_id`s from the bible, `locked: true`, zero cost, `generator.params.imported_from: "<series_id>/<source_episode_slug>"`. **No regeneration of an imported asset, ever, without a Director-approved unlock** (consistency contract rule 1 applies across episodes).
8. Only genuinely NEW elements (new characters, new locations, new objects, new state-variant derived sheets) are generated — under the CURRENT sheet rules (V2 rules d-142/d-143: 4-view turnarounds incl. back view on neutral grey), even though older canon predates them. Old canon is not retrofitted.
9. **Voices:** new dialogue lines for a canon character use the bible's `voice_presets` preset id; video-model voice conditioning uses the canon `voice_sample_media_id`/`public_url` — the same locked sample every episode, forever, unless the Director unlocks.
10. Media-id hygiene: provider media ids and CloudFront URLs are recorded in the bible so later episodes (and other providers — the SJinn lesson, d-182) can reference them without re-uploading. If a stored URL/id has gone stale, re-host from the local file and UPDATE the bible.

## During the episode

11. Style drift is a QC dimension: storyboard/clip QC compares against the SERIES style (`format.style`/`palette`), not just the episode brief. The founding episode's look is the reference.
12. Bible `laws` are in force from stage 1 — they are the distilled standing rules of previous episodes. The full decision logs of previous episodes remain the authority when detail is needed.
13. Cross-episode callbacks (running gags, promises like "next time we go to X") come from `continuity_notes` — the writer reads them; the Director gates them like any story beat.

## Episode close (after stage 11, or stage 12 if run)

14. Update the bible in ONE archived edit: episode entry → `complete` (+ logline, duration, `continuity_notes` for the next episode, `completed_at`); PROMOTE newly locked elements into `canon` (and new presets into `voice_presets`); append any new standing `laws` with their decision ids; record divergences that became permanent (a Director may promote an override into the new `format` default — that is a bible-level decision, logged).
15. Validate the bible against its schema after every edit (`validate_artifact.py <path> --schema series_bible`).

## Pitfalls

- Re-generating a canon character's sheet "to freshen it" — that is an unlock, Director-gated, and almost always wrong (episode-to-episode identity is the product).
- Pre-filling intake and then not TELLING the Director what was inherited — always show the inherited format block for a one-look confirmation before writing the brief.
- Promoting an episode-specific derived sheet (a one-off costume) into canon — promote only what future episodes will plausibly reuse; the rest stays in the episode.
- Treating the bible summary of a descriptor as the descriptor — the source episode's `lock_descriptors` entry is the record; the bible points, it does not restate anchors.
- Editing the bible without archiving to `history/` first (same law as every artifact).
