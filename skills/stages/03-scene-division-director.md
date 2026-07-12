# Scene Division Director — stage 3

Split the approved story into ≤15-second scene units — the atomic clips of production. No gate here: output flows straight into stage 4's recheck, and the Director gates THERE on the final list.

**Consumes:** `story`, `brief`. **Produces:** `artifacts/scene_list.json` (schema `scene_list`, `recheck: {performed:false, final:false}`).

## Process

1. **Dispatch `scene-splitter`** with paths to `artifacts/story.json` + `artifacts/brief.json`. It returns the scene_list JSON + a 3-line summary (scene count, total vs target, trickiest scene).
2. **Self-check before writing** (the stage's own QA — no external loop, so be strict):
   - Every `est_duration_seconds` in (0, 15]; **dialogue speakability**: words in the scene's lines ÷ 3 wps + ~2s of reaction beats must fit the duration — recompute, don't trust.
   - **Coverage:** every story beat_id appears in some scene's `beat_refs`; no scene without one.
   - **Speakers present:** every dialogue `character` is in that scene's `characters_present`.
   - **Continuity fields real:** location_ref/time_of_day progress logically scene-to-scene; `continuity_notes` state carryable facts (props in hand, wardrobe), not vibes.
   - `total_est_seconds` within the brief target ±15% (stage 4 fine-tunes to ±10%).
   - **Generatability scan:** flag any scene needing >3 characters, multiple locations, or complex physics — either restructure now or note it explicitly for the recheck.
3. Failures → re-dispatch `scene-splitter` with the specific violations named. Loop until clean (cap 3 attempts, then surface the problem).
4. **Write + validate** `artifacts/scene_list.json`, checkpoint:
   `write <slug> scene-division --status completed --artifact scene_list=artifacts/scene_list.json`
   (ungated — proceed directly to stage 4 in the same session).

## Pitfalls

- Squeezing a 20-second moment into 15 by shaving reaction time — split it into two scenes with a designed join instead.
- Duration optimism on dialogue: spoken lines + a look + a beat of silence is SLOWER than word count suggests.
- Scene summaries that restate the story instead of naming the scene's single dramatic job.
- Padding to hit total duration — if the story is short, tell stage 4 / the Director rather than inventing filler scenes.
