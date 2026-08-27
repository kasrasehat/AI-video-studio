# Asset Generation Director — stage 7

Generate the LOCKED reference assets every downstream generation will condition on: multi-view character sheets, environment plates, and voice samples — ~2 variants per element, the Director picks one, the pick becomes law.

**Consumes:** `lock_descriptors`. **Produces:** `artifacts/asset_manifest.json`.
**Gate:** the Director PICKS one variant per element (gallery) → `locked: true`. **Resume unit:** element.

## Before anything

Read `skills/tech/character-sheets` (the 3-view chain), `skills/tech/higgsfield-mcp` (media flow, cost preflight), `skills/meta/consistency-guard.md`. Check the live image-model catalog (`models_explore action=list type=image`) against `config/model_capabilities.yaml` — reconcile before spending.

## Element plan (derive from lock_descriptors)

- **character_sheet** per character, in narrative-importance order: 2 variants, each ONE single image containing 3 turnaround views + face close-up + detail insets + text annotations (see `skills/tech/character-sheets` — GPT-Image-2, quality high). Twin characters (documented identical) share ONE sheet element.
- **environment_plate** per location: 2 variants, each ONE single location SHEET — main establishing view + 2–3 alternate angles + detail insets + annotations, lit per `lighting_baseline`, empty of characters and time-varying props (per the descriptor's plate guidance).
- **voice_sample** per SPEAKING character: 2 variants auditioning the `voice_spec` on two lines — one neutral, one emotional, both from the character's actual scenes.
- Register every element with `element_id` = `<descriptor_id>_<sheet|plate|voice>`; `--unit-done` after each element completes.

## Generation rules (binding)

1. **Anchors verbatim** in every image prompt + default outfit + `metadata.render_style`; location prompts carry anchors + lighting baseline. Reference-generation prompts may be dense; downstream Seedance prompts stay minimal around the resulting locked image per the clean contract.
2. **Variants are genuinely distinct interpretations inside the approved brief style.** Depending on that style, the choice may be casting presence, silhouette/proportion language, production design, materials, or art-direction approach. Never change the rendering medium or inject a house style the brief did not request. Record the distinction in `generator.params.interpretation`.
3. **Cost discipline:** `get_cost: true` preflight per batch → announce credits in chat BEFORE generating → record actuals per variant (`cost_usd` in credits noted in metadata) and `--cost` on the checkpoint.
4. **Record provenance** per variant: gateway, model, full prompt, seed/job_id, params. Download/collect files under `assets/{characters,environments,voices}/` with the naming convention `<ID>_<variant>_<view>.<ext>`; record the Higgsfield `media_id`/job_id in `files[].media_id` (references for stages 8–9 need it).
5. **Self-QC before showing the Director** (per character-sheets skill): every anchor visibly true in every view; views are the SAME person; regenerate a drifted side view from the front — never the reverse. A variant that fails anchors is regenerated, not shown.
6. **Voice paths:** prefer the path that yields a reusable sample file + (ideally) a provider voice id: Higgsfield native voices (`create_voice`/`generate_audio`) or ElevenLabs voice design — whichever is available and passes the audition. The picked sample becomes the `reference_audio` voice lock; store as `assets/voices/<char_id>_<variant>.mp3` + media_id.
7. **Dry-run projects:** copy fixture placeholders, cost 0, never touch the MCP.

## The pick gate

1. Build the compare gallery: `python scripts/review_gallery.py <slug>` → `gallery/assets.html`; tell the Director the file path (opens in any browser) AND show inline paths per element.
2. Checkpoint `awaiting_human`; present per element: variant thumbnails/paths, the interpretation difference in one line, cost so far. END TURN.
3. On picks: set `selected_variant_id` + `locked: true` per element; log a `variant_selection` decision per element (`--decided-by user`); unpicked variants stay in the manifest (audit trail) but are NEVER referenced downstream.
4. Partial picks are fine — lock what's picked, iterate the rest (new variants count against `max_revisions_per_stage`).
5. After all elements locked: `--status completed --approved`, proceed to storyboards.

## Pitfalls

- Generating side views from text instead of chaining from the front (three siblings, not one character).
- Showing the Director a variant you already know violates an anchor — self-QC first.
- Environment plates with characters baked in (poisons every later composite).
- Forgetting media_id capture — stages 8–9 cannot reference a file that only exists locally.
- Voice samples that audition the WRONG line (use the character's real scene lines; the emotional line should stress the spec's hardest quality).
