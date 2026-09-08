# Scene Division Director — stage 3

Split the approved story into scene units — the atomic clips of production — sized to the ACTIVE VIDEO MODEL's max clip length (d-204): **≤15s on Seedance 2.0 (the default)**, **≤30s on Seedance 2.5 (only when the Director has explicitly ordered 2.5** for the production or a segment; a mixed production sizes each scene to the model the Director assigned it). No gate here: output flows straight into stage 4's recheck, and the Director gates THERE on the final list.

**Consumes:** `story`, `brief`. **Produces:** `artifacts/scene_list.json` (schema `scene_list`, `recheck: {performed:false, final:false}`).

## Process

1. **Dispatch `scene-splitter`** with paths to `artifacts/story.json` + `artifacts/brief.json`. It returns the scene_list JSON + a 3-line summary (scene count, total vs target, trickiest scene).
2. **Self-check before writing** (the stage's own QA — no external loop, so be strict):
   - Every `est_duration_seconds` in (0, ceiling] — ceiling = 15 (Seedance 2.0 default) or 30 (Seedance 2.5, Director-ordered, d-204); **dialogue speakability (tightened d-201)**: ≈2 wps + reaction beats — ~25–30 spoken words fit a full 15s clip, ~50–60 fit a 30s clip — budget each scene's lines to its ceiling and recompute, don't trust. The d-191 conversation-density law is satisfied by dividing talk across MORE scenes, never by cramming one clip.
   - **Coverage:** every story beat_id appears in some scene's `beat_refs`; no scene without one.
   - **Speakers present:** every dialogue `character` is in that scene's `characters_present`.
   - **Continuity fields real:** location_ref/time_of_day progress logically scene-to-scene; `continuity_notes` state carryable facts (props in hand, wardrobe), not vibes.
   - `total_est_seconds` within the brief target ±15% (stage 4 fine-tunes to ±10%).
   - **Generatability scan:** flag any scene needing >3 characters, multiple locations, or complex physics — either restructure now or note it explicitly for the recheck.
   - **Boundary design ([SEAM d-211]):** every boundary classified (`boundary_class_out`), landing on a natural action articulation (never mid-gesture), incoming `head_action` = a new motion beginning. Continuous boundaries are last-resort and MUST carry `overlap_from`/`overlap_seconds` (3–4s, counted once in `total_est_seconds`); hinges carry the three-beat design (intention tail → transition → 2–3s establishing head); dialogue never straddles a boundary mid-exchange; ~1s non-plot trim handles at each head and tail.
3. Failures → re-dispatch `scene-splitter` with the specific violations named. Loop until clean (cap 3 attempts, then surface the problem).
4. **Write + validate** `artifacts/scene_list.json`, checkpoint:
   `write <slug> scene-division --status completed --artifact scene_list=artifacts/scene_list.json`
   (ungated — proceed directly to stage 4 in the same session).

## Pitfalls

- Dividing by window instead of by beat (d-121): a beat is never cut to fill 15s; consecutive whole beats that fit one window are PACKED later, by stage 4's tag and stage 9's single generation.
- Squeezing a 20-second moment into 15 by shaving reaction time — split it into two scenes with a designed join instead.
- Duration optimism on dialogue: spoken lines + a look + a beat of silence is SLOWER than word count suggests.
- Scene summaries that restate the story instead of naming the scene's single dramatic job.
- Padding to hit total duration — if the story is short, tell stage 4 / the Director rather than inventing filler scenes.
