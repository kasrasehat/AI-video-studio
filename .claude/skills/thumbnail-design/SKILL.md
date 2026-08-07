---
name: thumbnail-design
description: "Design and generate click-driving video thumbnails with gpt_image_2, conditioned on the film's locked assets. Use when: writing a thumbnail concept or prompt in stage 11, choosing the curiosity strategy for a thumbnail, adding on-image text, or QC-ing a generated thumbnail at real display size."
---

# Thumbnail Design

A thumbnail is not a poster and not a frame grab — it is a **3-second sales pitch rendered as one image**. Its only job: make a scrolling viewer curious enough to click. Everything below serves that job.

> **In this pipeline:** Used by stage 11 (publishing). The `thumbnail-artist` subagent reads the film's artifacts, designs 2–3 concepts, writes each concept's COMPLETE `gpt_image_2` prompt, and SAVES the prompt into `publishing_kit.json` BEFORE any generation. Generation itself is Director-gated (d-114 extends to all paid calls). Higgsfield-first (d-147): `gpt_image_2` on the Higgsfield MCP is the generator.

## The curiosity law (BINDING)

Every concept must answer, in writing, one question before its prompt is written: **"What question does this image plant that only watching the video answers?"** That answer goes in the concept's `curiosity_hook` field. An image that merely *depicts* the film fails; an image that makes the viewer *need to know what happens next* passes. Honest curiosity only — the image must show something actually in the film (clickbait that the video doesn't pay off destroys retention and channel trust).

Proven curiosity strategies (pick ONE per concept; concepts must use different ones):
- **Emotion close-up** — one face, huge in frame, mid-peak-emotion (shock, delight, terror). Faces are the single highest-CTR element on YouTube.
- **Scale contrast** — two things that should not be the same size in one frame (a tiny person beside a giant cookie). Instantly legible, instantly strange.
- **Mid-action freeze** — the most dangerous/funny instant of the film frozen a beat BEFORE resolution (falling, about-to-be-caught, mid-leap). The viewer clicks to see the landing.
- **Impossible tableau** — a composition that visibly cannot be real, staged from actual film elements.
- **Confrontation** — two characters locked in opposition, stakes readable from body language alone.

## Composition rules

1. **One idea per image.** A thumbnail with two ideas has zero. Max 1–2 characters, one prop, one readable situation.
2. **Design for 168×94 pixels.** That is the size most viewers first see it. Big shapes, hard silhouettes, extreme expressions. If the emotion isn't readable at stamp size, the concept fails QC.
3. **Rule of thirds + face right.** Faces read best right-of-center (thumbnails render left-under the duration badge on some surfaces); keep the bottom-right corner clear of critical content (timestamp overlay).
4. **Color against the platform.** YouTube is white/dark grey. High-saturation warm subjects on cool or dark backgrounds pop hardest. Use the film's palette but push contrast 20% beyond the film's grade — thumbnails compete, films don't.
5. **Rim-light the subject.** A bright edge separating character from background is the cheapest legibility win at small sizes.

## On-image text (allowed — Director order 2026-07-31)

- **Max ~4 words**, one phrase, never a sentence. The title does the talking; the image text is a gasp: "SHE SHRUNK THEM?", "3 INCHES TALL".
- Huge, thick, high-contrast type with an outline or drop shadow; never over a face; never in the bottom-right.
- The text must NOT repeat the title verbatim — image text and title are two halves of one curiosity gap.
- Spell it in the prompt EXACTLY, in quotes, with placement and style: `bold yellow block letters with black outline, upper left: "SHE SHRUNK THEM?"` — gpt_image_2 renders quoted text reliably; unquoted text instructions drift.

## Prompt construction (gpt_image_2)

Order the prompt: (1) format declaration — "YouTube thumbnail, 16:9, designed to read at small size"; (2) the ONE idea, staged concretely; (3) characters via locked-sheet reference bindings + identity anchors VERBATIM (never from text alone — same law as every other generation, `skills/meta/consistency-guard.md`); (4) expression/pose at maximum legible intensity; (5) background (simplified, de-cluttered — a thumbnail background is a color field with a hint of place, not a set); (6) lighting (rim light + strong key); (7) on-image text spec in quotes; (8) style line (the film's look, contrast-boosted); (9) negative guardrails phrased positively where possible (d-099 still applies — camera negatives OK).

Params: `quality: "high"` (NEVER default — it silently drops to low), `resolution: 2k`, 16:9. Reference discipline d-106/d-124/d-127 applies unchanged: every attached media @-named in the prompt with a content description, map rebuilt from the actual medias array.

## QC (before presenting to the Director)

1. Downscale the generated image to **168×94** and look at it AT THAT SIZE: is the emotion readable? Is the text legible? Is the silhouette clean? (Zoom-to-native-res afterward for defect checks — both sizes, always.)
2. Identity check against locked sheets — a thumbnail is many viewers' FIRST contact with the characters; drift here is worse than drift in a clip.
3. Text spelled exactly as specified (generated text loves to mutate letters — check every character).
4. The curiosity_hook still holds: would a stranger ask the question? If the image answers its own question, it failed.

## Costs

`gpt_image_2` at quality high ≈ 4cr per image. Concepts are cheap; the discipline is writing the prompt and getting the Director's go BEFORE spending (d-114) — never batch-generate all concepts unprompted.

## A/B policy (d-173 — virality feature #4, standing)

Every release ships **2-3 APPROVED thumbnails** (distinct strategies, as always), and the upload always uses YouTube's built-in Test & Compare so real traffic picks the CTR winner. Refresh policy: if CTR disappoints ~48h after publish, swap to the approved alternate manually and note the change in the publishing kit. The pipeline's job is to guarantee the alternates EXIST and are upload-ready (1280x720 exports for each approved concept).
