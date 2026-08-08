---
name: heygen
description: "HeyGen MCP contract for stage 12 (character-spotlight): make film characters talk directly to the audience with lipsync, optionally intercut with b-roll. Use when: authoring or executing a spotlight video's generation payload, uploading assets to HeyGen, choosing between image-mode / studio / avatar paths, or polling HeyGen job status."
---

# HeyGen (MCP)

HeyGen animates a character image (or avatar) speaking a script with lipsync. In this pipeline it exists for ONE job: **stage 12 spotlight videos** — the film's characters talking to the audience. It is NOT part of the film itself (the film's dialogue is Seedance-native, d-160/consistency contract — that law is untouched).

## What this MCP can and cannot do (audited 2026-08-08)

CAN: create videos from an **arbitrary image** (`type: "image"` — animate a character portrait with lipsync), from an existing **avatar look** (`type: "avatar"`), from a **prompt + avatar references** (`type: "cinematic_avatar"`, Seedance-backed), and compose multi-scene videos server-side (`create_video_from_studio` / `type: "studio"`: 1–50 whole-frame scenes mixing avatar_video / narrated-or-silent image / video clips with optional voiceover). Also: direct-to-S3 asset uploads, lipsync-replace on existing video, video translation (dub), filler-word removal, AI clipping, templates.

CANNOT: create avatars or photo-avatar looks, list avatars, or list voices — those live in the HeyGen **web app**. Any `avatar_id` or `voice_id` must come from the Director's HeyGen account. Plan around this.

## The three generation paths (pick per video, record in `spotlight_kit.generation.path`)

1. **`heygen_image_mode_plus_local_assembly` (DEFAULT — no app setup needed).** For each talking segment: one `image`-mode request animating the character's locked portrait / clean film frame, speaking that segment's text. Download the talking clips, then assemble talking + b-roll + platform variants locally with the proven ffmpeg recipes (video-edit / platform-publishing skills). Most control, provable loudness/captions, b-roll stays byte-identical to the approved clips.
2. **`heygen_studio_one_shot`.** One `create_video_from_studio` call: `avatar_video` scenes (requires a HeyGen avatar/photo-avatar look id) interleaved with `video` scenes (our uploaded b-roll asset_ids; optional voiceover with playback mode freeze/loop/fit_to_scene) — a single rendered video_id, global aspect/resolution, optional burned captions + always an .srt sidecar. Use when the Director has created photo-avatar looks in the HeyGen app from our locked character images (one-time per character; record ids in `spotlight_kit.characters[].heygen_avatar_id`).
3. **`heygen_avatar_mode`.** Single-scene `avatar` request against an existing look; `engine: {type: "avatar_v"}` where the look supports it (check `supported_api_engines`) unlocks `motion_prompt` gesture control.

## Voice

- **Script + `voice_id`** (TTS): needs a voice from the HeyGen account (ElevenLabs-backed voices accept `voice_settings.engine_settings` — model, stability, style). Captions follow the script text.
- **Uploaded audio** (`audio_asset_id`): generate the line OURSELVES (ElevenLabs, VPN law d-150 applies) matched to the film's locked voice sample, upload, and let HeyGen lipsync to it. Best character-voice fidelity; bypasses TTS voice availability entirely. Preferred when voice match matters (it usually does).
- Never mix both in one scene (mutually exclusive by schema).

## Asset upload flow (images, b-roll clips, audio)

1. `create_asset_upload_batch` with `files[]` ({filename, content_type, size_bytes}) → returns batch_id + per-file `asset_id` + presigned `upload_url` + required headers.
2. HTTP **PUT** each file's bytes to its upload_url (curl/python — no bytes flow through the MCP).
3. `complete_asset_batch(batchId)` → 202; poll `get_asset_batch` until every item `completed`.
4. Record every asset_id in `spotlight_kit.generation.asset_ids` keyed by local path.

## Submit → poll → download

- Single studio video: `create_video_from_studio`. Anything else (including several image-mode segments at once): `create_video_batch` — one entry per segment, returns batch_id immediately.
- Poll `get_video_batch` / `bulk_video_statuses` (statuses: queued → processing → completed | failed). Completed items expose a **presigned, expiring download URL** — download to `assets/spotlights/` IMMEDIATELY and record the local path; never store the URL as the artifact.
- ffprobe every download (duration, streams) before presenting anything to the Director.

## Laws (stage-12 bindings)

- **d-114 unchanged**: the COMPLETE payload is saved into `spotlight_kit.json` BEFORE any call; cost/credits are announced (HeyGen bills credits per rendered minute by plan — read the number from the Director's HeyGen account and state it; filler-word removal is $0.60/source-minute, min 1 min); the Director gates every submission per video.
- **≥45 seconds of content** per spotlight video (stage law, Director order 2026-08-08). Budget the script at ~140 wpm + real b-roll durations; ffprobe-verify the master.
- **B-roll = approved film clips only**, uploaded as-is; spoiler law (trailer-design) applies to any next-episode tease.
- **Character fidelity**: the animated source image is a LOCKED asset (sheet view or approved clip frame) — never a regenerated likeness. Identity drift in a talking video is first-contact damage, same as thumbnails.
- Publish tools do not exist here and would not be used anyway: Claude packages; the Director posts.
- `enable_watermark` stays false; captions: request the .srt sidecar always (`caption: {file_format: "srt"}`), burn only for the tiktok variant (per-preset caption law from stage 10).

## Gotchas

- `image`-mode `motion_prompt` / `expressiveness` are documented for photo avatars — treat them as best-effort on raw images; put the performance in the audio and keep framing simple.
- Idempotency: pass an Idempotency-Key where supported (upload/lipsync/translation batches) so retries don't double-spend.
- `list_assets` requires the workspace `username` while in beta (it is the `owner` value on asset items).
- Studio composition is all-or-nothing (one render, one video_id) — QC the script and per-scene inputs on paper before spending; there is no partial retry.
- Statuses read model returns per-item ids as `video_id` even for assets/lipsyncs — do not be confused by the field name.
