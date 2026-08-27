# Lock Descriptors Director — stage 6

Extract the consistency backbone: every character, object and location that must stay identical across all clips, described precisely enough to prompt from VERBATIM — plus a voice spec for every speaker. Precision here is the cheapest quality money in the pipeline; every vague anchor becomes clip regenerations at 100× the cost.

**Consumes:** `scene_direction`, `scene_list`, `story`. **Produces:** `artifacts/lock_descriptors.json` + `artifacts/qa_review_lock_descriptors.json`.
**QA loop:** `qa-reviewer`, max 3 rounds, BLOCKING. **Gate:** Director approves.

## Process

1. **Dispatch `descriptor-extractor`** with paths to story, scene_list, scene_direction (it needs direction for lighting baselines and any look-dependent features). It returns lock_descriptors JSON + a coverage summary (N/M/K counts + unresolved scene refs).
2. **Resolve coverage HARD:** every `characters_present` entry and `location_ref` in every scene must map to a defined id. Unresolved refs are blockers — re-dispatch with them named, or (if a scene references someone the story never described) flag to the Director at the gate with a proposed invention.
3. **Run your own anchor audit before QA** (read `skills/meta/consistency-guard.md`):
   - Each anchor passes the two-character test (could two different-looking characters both satisfy it? → sharpen).
   - Static/dynamic filing correct — clothing/props NEVER in static_features.
   - Every character with a dialogue line anywhere has a complete `voice_spec`; voice fits role + story style + the audience (a children's film narrator ≠ a noir voice).
   - `forbidden_drift` populated per character with predictable failures, each paired implicitly with a concrete desired stable state for stage-9 `positive_locks`; raw negatives never enter the Seedance prompt.
   - Objects/locations that appear in ≥2 scenes are captured; single-scene props are not (registry bloat dilutes attention).
4. **QA loop (blocking):** `qa-reviewer` with lock_descriptors + all three upstream artifacts + this stage's `review_focus`. Apply proposed_fixes (re-dispatch the extractor for structural gaps; sharpen anchors yourself for wording). Final round → `artifacts/qa_review_lock_descriptors.json`. Max 3 rounds.
5. **Write + validate both, attach, gate.**

## Gate presentation

Per character: name, role, the anchors AS A LIST (these exact words will appear in every prompt — the Director should read them as such), default outfit + per-scene changes, voice spec in one line ("female child ~10, soft breathy, hesitant→brave"), forbidden drift. Then locations (anchors + lighting baseline) and recurring objects. QA verdict. Options: approve / edit any descriptor / abort. Edits are cheap here and expensive later — say exactly that.

## Pitfalls

- Beautiful prose instead of promptable anchors ("a face full of quiet sorrow" locks nothing).
- Voice specs copied between characters — every speaker distinct enough that a listener could tell them apart blind.
- Forgetting non-speaking background characters that recur visually (they drift too).
- Letting the Director approve without actually reading the anchors — they're approving the words the film will be built from; present them as the headline, not an appendix.
