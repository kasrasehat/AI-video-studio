---
name: image-editor
description: "Interactive image editing via Higgsfield — gpt_image_2 is the DEFAULT edit model (Director order d-054; nano_banana_pro only on explicit request). Use when the user asks to edit, retouch, add/remove/move objects in, recolor, restyle, or fix an existing image. This skill ELICITS FIRST (structured questions, confirmed edit brief + cost) and runs a BINDING Edit QC after every edit."
---

# Image Editor

Editing an existing image is a different job from generating a new one: the user already has pixels they like, and the risk is destroying what they wanted kept. This skill's contract: **never fire an edit from a one-line request** — elicit, confirm, then edit.

## Model routing (binding — Director order 2026-07-19, d-054)

- **DEFAULT: `gpt_image_2`** — edits run as an instruction-guided re-render conditioned on the source image (`medias` role `image`, value = media_id/job_id — never a URL or local path; `media_upload` local files first) plus an edit prompt that states the corrections AND everything that must stay identical. Chosen after nano repeatedly failed production edits (ignored instructions, altered untouched panels, left targets unchanged — d-049/d-053).
- `nano_banana_pro` is the cheap spot-edit alternative (~2 cr vs 7) — use ONLY when the Director explicitly asks for it, and never for anything whose on-image text must survive (d-023: nano corrupts rendered text).
- Photoreal portrait/fashion retouching: `soul_2` is the alternate; state why if chosen.
- The user may name a model; log the choice, never switch silently.

## Edit QC (BINDING — run after EVERY edit, before showing the result)

The checker (EP self-QC or a QC subagent) consults TWO skills: this section, plus the skill governing the edited artifact's type — `character-sheets` for sheets (anchors, spatial contract, label spelling), `storyboard-design` for storyboard pages (frame QC, axis, per-panel state laws). Checklist:

1. **Requested changes landed** — every item of the edit brief, verified visually one by one.
2. **Nothing else changed** — walk every region/panel NOT named in the brief against the source; any unrequested change (a prop appearing, a goggle state flipping, a pose shift) is a FAIL even if the requested edit succeeded.
3. **State laws re-checked** on the whole image (goggles/wet-dry/bracelet/prop timeline per `outfit_by_scene`; d-047 no-pop rule between panels).
4. **On-image text survived** — grid panel numbers, labels, hexes, spelled correctly.
5. On FAIL: one retry conditioned on the ORIGINAL (not the failed edit) with the failure named explicitly; after two failed attempts STOP, disclose to the Director with cost options — never loop silently.

## The elicitation protocol (BINDING — this is the skill's core)

On any edit request, ask BEFORE generating — batch the questions in ONE message, skip only what the request already answered explicitly:

1. **Target** — which image (path / media_id)? If ambiguous between files, list candidates.
2. **The change** — add / remove / move / resize / recolor / restyle / repair? Describe the desired end state in one sentence.
3. **Placement** — WHERE, in relative-position language ("on the table's center, left of the bowl", "upper-right corner, two object-widths from the edge"). Vague placement = model's guess = wrong result.
4. **Scale & style of the new/changed element** — how big relative to neighbors; match the image's existing style/palette, or deliberately different?
5. **The preserve list** — what must NOT change (faces, layout, lighting, background, other objects, text). Default assumption: EVERYTHING not named in the change is preserved — state that back explicitly.
6. **On-image text check** — does the image carry labels/typography that must survive? If yes → gpt_image_2 regen route (see boundary above); tell the user why.
7. **References** — is there an image showing the desired object/style to condition on?
8. **Output** — aspect/resolution requirements; same as source unless stated.
9. **Downstream use** — is this a production asset (locked? canonical?)? See production rules below.

Then present the **EDIT BRIEF**: one short block restating target, change, placement, preserve list, model, and the preflighted cost (`get_cost:true`). Get an explicit yes. Only then generate.

## Mechanics

- Preflight cost and announce; generate; poll `job_display`; download the result; record model, full prompt, job_id (= the new media_id), cost.
- Offer ONE refinement round by default ("what should be adjusted?") — further rounds are new briefs.
- Iterating on an edit: condition the next attempt on the ORIGINAL image plus corrections, not on the failed edit (compounding edits drift).

## Production-asset edits (this repo's projects/)

- A `locked: true` asset may not be edited without the Director's explicit unlock (consistency contract §1).
- Archive the original to `history/superseded/` with a reason-suffixed filename BEFORE replacing; update `asset_manifest` files[].media_id to the new job_id; validate; log the decision at the moment it's made.
- Edits to annotated sheets are ALWAYS full gpt_image_2 regens per the boundary above, and inherit the character-sheets skill's spatial contract + spelling guards.
