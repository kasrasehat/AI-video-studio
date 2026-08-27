---
name: ai-video-gen
description: "Cross-model knowledge for AI video generation — model comparison, strengths, and prompting guidance for Seedance, Veo, Kling, Sora, Runway, MiniMax, LTX. Use when: choosing a video model for a shot, writing or adapting a generation prompt for a specific model, or setting aspect/duration/reference-image options."
---

# AI Video Generation (Cross-Model Knowledge)

> **Model access in this repo goes through the Higgsfield MCP (see `skills/tech/higgsfield-mcp`). This skill carries cross-model prompting knowledge; per-model routing/capabilities live in `config/model_capabilities.yaml`.**

## Model landscape

| Model | Notes / strengths |
|-------|-------------------|
| **Seedance 2.0** | Preferred default for cinematic, trailer, and high-fidelity clip work. Only model in the fleet with single-pass native synchronized audio, multi-shot generation, director-level camera control, and lip-sync from quoted dialogue. Ranks #1 on Artificial Analysis Elo as of early 2026. Standard + fast variants. |
| Seedance Pro / Lite (1.x) | Lighter earlier-generation Seedance tiers |
| VEO 3.1 | Google; highest quality among the non-Seedance options; strong for photoreal landscape. `veo_3_1_fast` / `veo3_fast` variants trade quality for speed |
| VEO 3 / VEO 2 | Earlier Google generations |
| Kling (v3 / v2.1 / Pro) | Stylistic fit for specific anime looks |
| Sora V2 / V2 Pro | OpenAI; pick when the OpenAI motion character is specifically wanted |
| Runway Gen-4 | Runway's premium generation model |
| MiniMax | Additional provider option |
| LTX Distilled | Fastest; use only when speed is the hard constraint |

Switch off the Seedance 2.0 default only for a specific reason: budget, provider preference, or stylistic fit (VEO for photoreal landscape, Kling for a specific anime look). In this repo, model choice must additionally satisfy `config/model_capabilities.yaml` policy (e.g. dialogue scenes only on models meeting `policy.dialogue_scene_requires`) — and swapping models is a Director decision.

For Seedance-specific prompting and parameters, route by the approved brief: `live_action`/`hybrid` → `skills/tech/seedance-clean`; `animation` → `skills/tech/seedance-prompting`. Older briefs use seedance-clean's backward-compatible router and stop on ambiguity.

## Generation options (common across providers)

- **Aspect ratio:** `16:9` (landscape, our film default), `9:16` (vertical), `1:1` (square).
- **Image-to-video:** pass a reference image for the starting frame — the standard way to lock composition/identity from an approved still.
- **Tail image / last-frame guidance:** some providers accept a tail image to steer the final frame — useful for clip-to-clip chaining.
- **Provider config overrides:** providers expose model-specific config objects; route those through the capability matrix rather than hardcoding.

## Prompting guidance

1. **Be descriptive** — include camera movement, lighting, style, and mood details, not just subject/action.
   - Example shape: "A drone shot flying over a coastal city at golden hour, cinematic lighting."
2. **Use reference images** for image-to-video — the most reliable way to animate an approved still while keeping identity.
3. **Quoted dialogue** in the prompt drives lip-sync on models that support it (Seedance 2.0).
4. **Aspect ratio is part of the creative spec** — set it explicitly per shot; don't rely on provider defaults.

## Operational expectations

- **Video generation is the slowest step** — allow up to ~5 minutes per clip; poll job status roughly every 10 seconds (Higgsfield MCP jobs are async — record `job_id` per the higgsfield-mcp skill rules).
- **Output URLs are temporary** — download generated videos promptly into the project's asset tree.
- **Record provenance** for every call (model, full prompt, references, params, seed, cost) in the generation manifest.

<!-- adapted from OpenMontage (.agents/skills/ai-video-gen/SKILL.md) -->
