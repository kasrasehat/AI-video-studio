---
name: sjinn
description: "SJinn MCP contract for stage 12 (character-spotlight): generate talking-character videos (Seedance-backed) and audio from public reference URLs. Use when: authoring or executing a spotlight video's generation payload, choosing an SJinn model, checking membership/credits, or polling SJinn tasks. Replaces HeyGen as the stage-12 backend (d-182)."
---

# SJinn (MCP)

SJinn is the stage-12 generation backend (Director order d-182, 2026-08-09 — replaced HeyGen). It fronts the SAME model family as the film (Seedance) plus alternatives, taking **public HTTPS URLs** as references — no upload ceremony for assets that already live on a CDN.

## Account gates (check FIRST, every session)

`whoami` → membership must be `active` (credits alone are NOT enough — an inactive membership blocks generation with `membership_required`; burned lesson from stage 10). Also returns the credit balance and live model lists.

## Models (audited 2026-08-09)

| Model | Duration | Resolution | Assets | Notes |
|---|---|---|---|---|
| `seedance2` (default) | 4–15s int | 480/720/1080p | ≤9 total image+video+audio URLs | THE film engine; `mode: quality` for finals |
| `seedance2.5` | 4–30s | 480/720p (no 1080p!) | ≤30 img, ≤10 vid, ≤10 aud | longer takes; resolution capped at 720p |
| `minimax-h3` | 5–15s int | 2K only | ≤9 img, ≤3 vid/aud (≤15s combined) | 2K alternative |
| `kling3` | 3–15s int | — | ≤2 img, NO audio refs | no voice lock → not for dialogue |
| `gemini-omni-video` | 4/6/8/10s | — | ≤7 img, ≤1 vid, no audio | not for dialogue |

Dialogue policy unchanged: talking segments need audio references (voice lock) → `seedance2` (1080p ceiling) or `seedance2.5` (720p ceiling, ≥16s takes). Audio: `create_audio_task` (seed-audio-1-0, mp3; ≤3 reference audios cited as @Audio1..3 OR 1 reference image — mutually exclusive; NO preset voice library — Higgsfield keeps the preset-voice role, d-147 lives on there).

## Call shape (spotlight talking segment — the d-181 method)

`create_video_task`: model seedance2, mode quality, resolution per Director ruling, duration = audio length + ~1s (int, ≥4), aspect_ratio 16:9, `image_urls` = [locked character sheet URL, locked location plate URL], `audio_urls` = [locked voice sample URL]. Route the prompt by the source brief: live_action/hybrid → `seedance-clean`; animation → `seedance-prompting`. Adapt the @-map to SJinn naming: **@Image1/@Image2/@Audio1 in URL order** (every attached URL cited with a content description). All other film laws apply: anchors word-for-word, state restatement, and one deliberately static direct-address take unless the Director approves another format.

Reference URLs: Higgsfield media/results CloudFront URLs are public and stable — pass them directly. Local-only files: `upload_asset` first (or host via Higgsfield `media_upload`, which returns a permanent public URL).

## Tasks & results

- Creation returns `task_id` + a live interactive component; `get_task(task_id)` fetches state on demand (statuses pending → running → completed/failed; completed carries `output_urls`).
- Download outputs IMMEDIATELY to `assets/spotlights/` and record the local path — never store only the URL.
- `create_compose_task` concatenates ≥2 video URLs in order — bare cuts only (no audio mixing, no transitions). Our local ffmpeg assembly is richer (loudnorm, VO mix, captions); use compose only for quick previews.

## Costs (LAW — no preflight exists)

SJinn exposes **no cost-preflight tool**. d-114 adaptation, Director-endorsed: (1) `whoami` balance BEFORE a gated call, (2) run the single Director-approved probe, (3) `whoami` after → the delta is the unit price; RECORD it here and in the artifact, then state batch costs from measured units. Never launch a batch whose unit price hasn't been measured by a probe.

- Measured 2026-08-09: **seedance2 quality 720p = 263 credits/s** (probe e6906c01: 4s = 1,052; batch of 11/97s = 25,511 — rate holds). **minimax-h3 2K = 150 credits/s** (probe 37e79285: 5s = 750; charged at task CREATION, before rendering). minimax-h3 is cheaper and sharper but drifted off-model on the film's characters in the A/B (rounder, younger face vs the locked sheet) — seedance2 holds identity; pick minimax only with Director-approved identity tolerance.
- Measured 2026-08-10: **gpt-image-2 image, 2K, with reference image_urls = 100 credits/image** (probe 9e11de82, 1:1 avatar; balance 308,566 → 308,466). Image tasks take public HTTPS reference URLs in `image_urls` exactly like video; reference-conditioned identity held well on locked sheets. **nano-banana-pro 2K = 150 credits/image** (measured in the same session's 450-credit batch: 3×gpt-image-2 + 1 nano). nano-banana-2 unmeasured — probe before any batch.
- **nano-banana-pro literalism gotcha (2026-08-10, task 1eb266b9):** given an explicit "center safe band = middle 60%×30%" composition law, nano-banana-pro rendered the safe band as a LITERAL visible horizontal strip with hard seams — content inside a band, plain gradient above/below. gpt-image-2 interpreted the same prompt correctly (full-bleed art, detail concentrated centrally). For nano models, phrase layout constraints implicitly ("keep key subjects near the vertical center, atmosphere toward edges"), never as measured zones.

## Gotchas

- **Concurrency cap: 5 concurrent Seedance tasks per account** (clean `task_creation_failed` error, measured 2026-08-09). Submit batches in waves of ≤5; poll and refill slots as tasks complete.

- `membership_required` even with a large credit balance = membership lapsed; the Director renews in the SJinn app.
- Unsupported params return `unsupported_parameter` — check the per-model matrix above before calling.
- seedance2.5's 1080p gap: for >15s single takes you trade resolution; prefer splitting into ≤15s seedance2 segments and cutting (film house style anyway).
- kling3 with image refs: omit aspect_ratio (the image decides it).
