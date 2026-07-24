---
name: higgsfield-mcp
description: Using the Higgsfield MCP server — our gateway to Seedance 2.0, Kling, Veo, Wan, Higgsfield image models, voices, and post tools. Use when making any video/image/voice generation call in stages 7–10, uploading reference media, preflighting cost, or checking model availability.
---

# Higgsfield MCP

> AUDITED 2026-07-11 against the live server (models_explore + tool schemas). Remaining
> unverified items are marked. Tools surface as `mcp__<server>__<tool>`; if they are deferred,
> load them in bulk via ToolSearch before calling.

Higgsfield Cloud is our generation gateway. Account: Ultimate plan, credits-based (check with `balance`). Auth for the underlying account: `HIGGSFIELD_API_KEY` + `HIGGSFIELD_API_SECRET` (https://cloud.higgsfield.ai/api-keys); in Claude Code the server is user-connected (remote MCP connector) — under other harnesses connect their MCP support to the same server, or STOP and tell the Director which call you needed.

## Core tools (verified)

| Tool | Use |
|---|---|
| `models_explore` | `action=list/search/get/recommend` — THE source of truth for model ids, params, media roles, aspects, durations. Reconcile `config/model_capabilities.yaml` against it when in doubt. |
| `generate_video` | All clip generation. `model` required; `params.prompt`, `params.duration`, `params.aspect_ratio`, `params.medias[]` (role + value), model-specific params (mode/genre/…). **`params.get_cost: true` preflights credits without generating — use before every batch.** |
| `generate_image` | Character sheets, environment plates, storyboard frames. Same shape as generate_video. |
| `media_upload` / `media_upload_widget` / `media_import_url` | Get local/remote files into Higgsfield → returns `media_id`. **`medias[].value` must be a media_id or a prior generation's job_id — NEVER a URL or local path.** |
| `job_display` / `show_generations` | Poll async jobs; retrieve outputs. Record `job_id` in the producing artifact. |
| `balance` / `transactions` | Credits + plan; spend history. |
| `create_voice` / `create_voice_from_confirmed_audio` / `list_voices` | Higgsfield-native voice entities (alternative voice-sample path — evaluate at M4). |
| `generate_audio` / `voice_change` / `dubbing` | Audio generation/transform (unverified params). |
| `upscale_video` / `topaz_video` / `bytedance_video_upscale` / `video_deflicker` (via generate_video model ids) | Stage-10 polish: upscale to 1080p/2K/4K (aigc preset exists), deflicker. |
| `show_characters` | Higgsfield "Soul" trained characters (5–20 photos, ~10 min) — candidate v2 character lock. |
| `show_reference_elements`, `presets_show` | Reference element registry; image-to-video presets (avoid presets for film work — our prompts are authored). |

## The reference-media flow (BINDING for stages 7–9)

1. Generate or obtain the asset locally (or via a Higgsfield generation → it already has a job_id).
2. Upload local files with `media_upload` (Apps UI: `media_upload_widget`) or `media_import_url` for URLs → `media_id`.
3. Record the `media_id` in `asset_manifest` (`files[].media_id`) / `storyboard_set` (`frames[].media_id`) next to the local path.
4. Pass ids in `generate_video.params.medias[]` with the model's declared roles. Seedance 2.0 roles:
   - `start_image` / `end_image` — the shot_selection frames
   - `image_references` — locked character sheet views + environment plate (≤9 total images incl. start/end)
   - `audio_references` — **the locked voice sample of every speaker (the voice lock — never omit on dialogue clips)**
   - `video_references` — optional motion/continuity refs (≤3)

## Workflow rules (binding)

1. **Route by `config/model_capabilities.yaml`.** Dialogue scenes ONLY on models satisfying `policy.dialogue_scene_requires` (today: `seedance_2_0`, `seedance_2_0_mini`; `wan2_7` pending M6 lipsync verification). Model choice is a Director decision — log it.
2. **Prompt per the model's skill** (`skill:` field — Seedance → `skills/tech/seedance-prompting`).
3. **Preflight cost** (`get_cost: true`) and announce before every batch; record actual credits in the artifact's cost fields. **CAVEAT (confirmed 2026-07-24): `get_cost` does NOT validate param combinations** — it happily priced `mode: fast` + `1080p` (35cr) that the real generation endpoint then rejected with a 422 ("mode 'fast' supports only 480p/720p"). A preflight price is only proof of cost, not of validity; the capability limits in `config/model_capabilities.yaml` (e.g. "1080p/4k require mode std", mini caps at 720p) remain authoritative, and an unsupported resolution may also be SILENTLY clamped rather than rejected (mini at "1080p" quietly became 720p in the adjustments echo — check `adjustments` on every response).
4. **Async jobs:** poll via `job_display`; record job_id + params + prompt in the producing artifact. A call that isn't recorded didn't happen.
5. **Dry-run projects never touch this MCP.**
6. **Failures:** transient → retry once; content-policy rejection → rephrase per model skill + decision-log it; `recovery_tool` in a response → call it immediately; repeated failure → surface to the Director. Never silently swap models.
7. Prefer `count: 2` on image generations where the stage wants 2 variants (one call, two candidates).

## Verified model quick-reference (details in config/model_capabilities.yaml)

- **seedance_2_0** — dialogue default. 4–15s, up to 4K (mode std), all aspect ratios, genre hint, native audio independent of audio refs.
- **seedance_2_0_mini** — same roles (incl. audio_references!), 480/720p — drafts + QC retries.
- **wan2_7** — start/end + audio_references, 2–15s — dialogue candidate pending lipsync test.
- **kling3_0 / kling3_0_turbo, veo3_1 / veo3_1_lite, cinematic_studio_3_0, minimax_hailuo** — non-dialogue roster.
- **Sora: NOT in the catalog** (2026-07-11).
- Images: **nano_banana_pro** (4K, text, refs), **soul_2** (portraits/character), higgsfield presets. 

## Still to verify (M4/M6, cheap calls)

- [ ] Image-model catalog details: `models_explore action=list type=image` → exact ids/params for soul_2, nano_banana_pro; seed support + where seeds are returned.
- [ ] `generate_audio` params; whether a Higgsfield voice can render our two audition lines (vs ElevenLabs path).
- [ ] Wan 2.7 quoted-dialogue lipsync quality (one 5s test clip).
- [ ] Seedance audio_references in practice: one dialogue test clip with a reference voice — confirm the output voice matches the sample (THE voice-lock proof, M6's first task).
- [ ] Credit→USD anchor for reporting (plan pricing page or transactions).
