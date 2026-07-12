---
name: character-sheets
description: Multi-view character sheet generation with identity chaining — the visual half of the character lock. Use when generating character sheet variants in stage 7, adding views/expressions to a locked character, or repairing an identity-drifted reference.
---

# Character Sheets

A character sheet is the set of locked reference images that every downstream generation (storyboard frames, clips) conditions on. Identity across 30 clips is only as strong as this sheet. Method: ViMax-style **3-view chaining** — identity is locked by images referencing images, never by re-describing in text.

## The 3-view chain (per variant)

1. **FRONT (text→image).** The only view generated from text. Template:
   `Full-body, front view portrait of <name>. Pure white background. Centered, standing, arms relaxed at sides, gazing straight ahead, natural expression. Features: <static_features.face>; <static_features.body>; <static_features.age>; <marks>. Wearing: <default_outfit>. Identity anchors: <all identity_anchors verbatim>. Style: <brief style>.`
   White background + neutral pose is not aesthetic — it's clean conditioning material.
2. **THREE-QUARTER (image→image, reference = the front view).** Same framing, same white background: `Same character as the reference image, exact same appearance and outfit, now facing three-quarter left.`
3. **PROFILE (image→image, reference = the front view).** `…now in full left profile.` (Add BACK — "no facial features visible" — only if the story has meaningful from-behind shots.)

Chaining side views FROM the front image is what locks the face; generating each view from text produces three siblings, not one character.

## Model & workflow

- Primary: **Nano Banana** (Google) — strong multi-image reference support and consistency edits. Alternative: Higgsfield image models (see `config/model_capabilities.yaml` image_models).
- Stage 7 produces **2 variants per character** (different seeds and a deliberate interpretation difference — e.g. crisper vs softer rendering — not random rerolls). Each variant = its own 3-view chain. The Director picks one in the gallery; picked variant → `locked: true`; file convention `assets/characters/<char_id>_<variant_id>_<view>.png`.
- Record per variant in `asset_manifest`: model, full prompt, seed, cost.

## Self-QC before presenting (per variant)

- Every `identity_anchor` visibly true in ALL views (bob length, mole side, outfit pattern — check each, per view).
- Views are the SAME person (face structure, build, palette) — if the profile drifted, regenerate the profile from the front view; never regenerate the front to match a drifted side.
- Outfit matches `dynamic_features.default_outfit` exactly; no invented accessories.
- Distinctness: two characters' sheets must not be confusable at thumbnail size.

## Expression / outfit extensions (dialogue-heavy or multi-outfit stories)

- Expression sheet (i2i from the locked front): happy / sad / shouting / afraid — same framing, only the face changes. Generate AFTER locking, as children of the locked front view.
- Per-scene outfits (`outfit_by_scene`): i2i from the locked front — `same character, exact same face and build, now wearing <outfit>` → stored as additional locked files, used as the reference for those scenes.

## Downstream use (how the sheet travels)

- Storyboard frames + clips condition on the locked views; select the view matching the character's facing direction in the shot (side-facing shot → profile view), 2–3 views per character max per call.
- In every downstream PROMPT the character appears via anchors verbatim — the sheet locks pixels, the anchors lock the text channel. Both, always (see `skills/meta/consistency-guard.md`).

<!-- method adapted from ViMax (MIT) 3-view portrait registry, research extraction 2026-07-09 -->
