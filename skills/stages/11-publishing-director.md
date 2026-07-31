# Publishing Director — stage 11

Turn the finished film into a post that gets clicked: thumbnail + title + description + hashtags/tags + platform settings, packaged as `artifacts/publishing_kit.json`. Created by Director order 2026-07-31. Runs AFTER integration (the cut's runtime and chapters feed the metadata), though thumbnail concept work may be prepared earlier since it conditions on locked assets, not the render.

## IO contract (from pipeline.yaml)
- Consumes: `brief`, `story`, `scene_list`, `asset_manifest`, `render_report`.
- Produces: `artifacts/publishing_kit.json`.
- Gate: the Director approves the selected thumbnail AND the copy. Claude never uploads or posts anything — the kit is a hand-off.

## Standing laws that bind here
- **d-114 extends to every paid call:** thumbnail prompts are written and SAVED first; generation only on the Director's explicit go, one concept at a time if the Director so chooses.
- **d-147 Higgsfield-first:** `gpt_image_2` on the Higgsfield MCP is the thumbnail generator (quality high — it silently defaults low — 2k, 16:9). If a future need exceeds it, check Higgsfield first, then propose alternatives.
- **Reference discipline d-106/d-124/d-127:** locked sheets attached and @-named with content descriptions; characters never generated from text alone.
- **Archive-before-edit** for every artifact touch; schema-validate after; decisions logged at their ids.

## Track T — Thumbnail (`thumbnail-artist` subagents, parallel, different strategies)

1. EP assigns 2–3 curiosity strategies from `skills/tech/thumbnail-design/SKILL.md` (e.g. emotion-close-up vs scale-contrast vs mid-action freeze) — one per artist instance, genuinely different ideas, variant discipline as everywhere.
2. Each artist reads the film artifacts, finds its strategy's best moment, writes curiosity_hook + the COMPLETE gpt_image_2 prompt (on-image text allowed, ≤4 words, quoted verbatim — Director order 2026-07-31), returns a `concepts[]` entry with status `proposed`. **Prompts are saved into the artifact BEFORE any generation.**
3. Present the concepts on paper (strategy, hook, prompt summary, text, cost preflight) → **Director picks which to generate** → generate → QC per the skill (168×94 stamp test, native-res zoom, text spelling, identity vs locked sheets) → present images → **Director approves one** → `selected_concept_id`, downscale/export the 1280×720 `delivery_path`.

## Track M — Metadata (`youtube-strategist` subagent, after or alongside Track T)

1. Strategist receives artifact paths + final runtime/chapters + the leading thumbnail's on_image_text and hook (title and image text are two halves of one curiosity gap — never authored blind to each other).
2. Uses the Director's expert-persona method (three-part briefs, `skills/tech/youtube-publishing/SKILL.md` — BINDING) to author title_options (distinct angles), description (hook_first_125 + full_text + chapters + CTA), hashtags (≤15, best 3 first), tags, category, pinned_comment.
3. `made_for_kids` is presented as an explicit Director decision with the COPPA tradeoff stated — never defaulted.
4. Present all copy → **Director picks the title and approves the block** → `selected_title` recorded.

## Assembly & gate

Merge both tracks into `publishing_kit.json` (schema `publishing_kit`), validate, checkpoint `awaiting_human`, present the complete kit (thumbnail image + full copy in one view). On approval: checkpoint `completed --approved`, log the gate decision. Deviations the Director accepts are rulings, recorded in `notes`.

## Pitfalls
- Generating a thumbnail before its prompt is saved in the artifact (kills provenance) or before the Director's go (d-114 violation).
- Title echoing the on-image text — the pair must add up, not repeat.
- 16 hashtags (YouTube ignores ALL above 15), hook_first_125 that reads like a summary, chapters that drift from the real cut.
- Treating the thumbnail as a pretty film still instead of a curiosity machine — the stamp-size test is the arbiter, not full-size beauty.
