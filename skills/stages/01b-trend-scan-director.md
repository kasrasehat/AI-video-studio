# Trend Scan Director — stage 1b (OPTIONAL, d-192)

Ride a cultural wave on purpose. After intake (and before the writers' room), the Director may order a live social-media trend scan; its output can shape the story subtly and boost every click surface (tags, title, description, thumbnail, trailer, teasers, spotlights).

**Consumes:** `brief` (+ the series bible for episodes). **Produces:** `artifacts/trend_kit.json` (schema `trend_kit`).
**Gates:** TWO — trend selection, then integration plan. **Optional:** like stage 12, this stage is OFFERED, never assumed; "no" → checkpoint `skipped --approved`, and `next` never blocks on it.

## Rule -1 — optionality

Offer in one short paragraph at the end of intake: a trend scan researches what's live on YouTube/TikTok/Instagram right now and proposes 10 brand-fit trends; picking one can lift discoverability materially; picking none costs nothing. The Director opts in or out; log the decision either way.

## Process

1. `checkpoint.py write <slug> trend-scan --status in_progress`.
2. **Dispatch `trend-scout`** with the brief (+ bible), today's date, and — when Higgsfield is connected — the output of `tiktok_music_trending` folded into its inputs. It returns 10 evidence-backed proposals (TR01–TR10). Research is FREE (web + MCP reads only).
3. Write `trend_kit.json` (proposals + empty selection), validate.
4. **GATE 1 (selection):** present the 10 as a table — name | kind | where it's trending (evidence 1-liner) | why it fits us | risk | longevity — strongest first, with the scout's coverage note. Options: **pick one or many / none / ask for a re-scan with different focus**. END TURN.
   - "None" → record `selection.selected_trend_ids: []`, checkpoint `completed --approved`, log, done — a legitimate outcome, never argue for a trend.
5. On selection: record it (archive → edit → validate), log the decision (`--decided-by user`). **Dispatch `trend-weaver`** with the selected proposals, brief/bible, and any existing story material. It returns the `integration` block (story plan with subtlety tests + per-surface metadata placements).
6. **GATE 2 (integration plan):** present the story plan (approach, where, the subtlety test verbatim) and the metadata placement table (surface → what appears there, including deliberate blanks). END TURN. Revise via the weaver on notes.
7. On approval: write the final kit, checkpoint `completed --approved --artifact trend_kit=artifacts/trend_kit.json`, log.

## Downstream consumption (who reads trend_kit)

- **Stage 2 (story):** the orchestrator passes `integration.story_plan` into the writer's brief; the qa-reviewer verifies the weave passes its own subtlety test (a trend-blind viewer loses nothing) — a trend that reads as bolted-on is a CRITICAL.
- **Stage 11 (publishing):** `metadata_placements` feed title options, description hook, TAGS, hashtags, thumbnail concept notes, trailer/teaser notes. The strategist re-verifies the trend is still live at publish time (longevity honesty) and drops stale placements with a note.
- **Stage 12 (spotlights):** `spotlight_note` feeds intake/scripting; `trend_refs` recorded in each video's metadata block.

## Pitfalls

- Running the scan from training-data memory — trends must be researched LIVE with dated sources, or the film chases last year's wave.
- Letting the scout pre-select or the weaver upsell — 10 honest options, Director picks, subtlety contract governs.
- Baking a "days"-class trend into generated clips — bake into METADATA (editable at upload) unless longevity justifies pixels.
- A trend integration whose removal would break the story — that's a plot pillar, not seasoning; redesign.
- Skipping the re-verify at publish time — stage 11 owns the staleness check.
- Trend material that violates content_boundaries or uses licensed IP/music — the brand filter is not negotiable.
