# Stage 12 — Character Spotlight (OPTIONAL)

Direct-to-audience videos where the film's characters talk to the viewer — introduce themselves, talk about the movie, tease the next session, or any subject the Director orders — optionally intercut with b-roll from the approved film clips. Generated with **SJinn** (`skills/tech/sjinn/SKILL.md`, BINDING — replaced HeyGen by d-182), scripted by the **spotlight-writer** subagent. Minimum **45 seconds** of content per video. The stage loops: one video at a time, each fully gated, until the Director closes the stage.

## Rule -1 — this stage is OPTIONAL

Never start it unprompted. After stage 11 closes (or on `/resume` when `next` reports it as optional-available), OFFER it in one short paragraph: what a spotlight video is, that it generates talking-character shots via SJinn, that each video is individually priced and gated. Then the Director decides:
- **"yes / let's make one"** → enter the stage (`checkpoint.py write <slug> character-spotlight --status in_progress`) and run the per-video loop below.
- **"no / skip"** → `checkpoint.py write <slug> character-spotlight --status skipped --approved --note "Director declined stage 12"`, log the decision, done. `skipped` never blocks pipeline completion.
- Once ENTERED, the stage gates like any other — it can still end in `skipped` if the Director changes their mind before any video is approved, or `completed --approved` after the last one.

## Per-video loop (repeat until the Director says stop)

### 1. Intake — ASK, never assume (BINDING)
Before any authoring, ask the Director **in chat** for this video's:
1. **Subject** (introduce themselves / about the movie / next-session tease / anything else),
2. **Short description** in their own words,
3. **Target length** (floor is 45s; propose 60–90s if they have no preference),
4. **Which character(s)** speak,
5. **Platforms** (defaults to the film's set: youtube + tiktok + instagram),
6. **Tone + CTA** (optional — propose in-character defaults).
Record the answers verbatim in the new `spotlight_kit.videos[]` entry (`video_id` SP01, SP02, …; status `intake`). One question message, all six points, then WAIT.

### 2. Script (spotlight-writer, task "script")
Spawn `spotlight-writer` with: the intake answers verbatim + paths to `brief`, `story`, `scene_list`, `lock_descriptors`, `publishing_kit`, `generation_manifest`. It returns the `script[]` fragment (in-character talking segments + b-roll picks with real in/out times + per-segment directions, seconds budgeted to the target). Validate, merge into `spotlight_kit.json` (archive-before-edit), status `scripted`.
**GATE (paper, free):** present the script as readable dialogue with the timing budget. END TURN. Revise on feedback; on approval → status `approved_script`, log the decision.

### 3. Payload (spotlight-writer, task "payload") — the d-181 method
Talking segments are **full moving Seedance shots**: each segment is one `create_video_task` (seedance2, mode quality, resolution per Director ruling, ≤15s) staging the character in a LOCKED location — the film set becomes the series' "show set" (micro-explorers: LOC01 garage). Each prompt follows the integrated clean contract in canonical block order with `single_continuous` format, an occupied first frame, FOV optics, static operator behavior, visible performance and contact physics, sourced light, exact dialogue, and positive locks. SJinn's explicit `@Image1/@Image2/@Audio1` tags follow URL order; reference text stays minimal around the locked sheet and plate. The payload records `image_urls` = locked character sheet + locked location plate and `audio_urls` = the locked voice sample. Voice lines pre-generated for audition remain the b-roll VO source and a delivery reference; Seedance re-performs talking lines itself.
Save the COMPLETE payload into `spotlight_kit.json` BEFORE anything is spent (d-114). **Cost law (SJinn has no preflight): one Director-gated PROBE segment first; unit price = whoami balance delta; batch cost stated from measured units.**
**GATE (spend):** probe result + measured unit price + batch total. END TURN. On approval: submit the batch, poll, download to `assets/spotlights/`, ffprobe everything.

### 4. Assemble + QC
Assemble talking segments + b-roll locally (video-edit recipes; hard cuts in script order; mezzanine-conform first; b-roll clip audio muted where the script says so, with the pre-generated VO lines mixed over; two-pass linear loudnorm to −14 LUFS). Master to `renders/spotlights/SP<nn>_master.mp4`, versioned in `renders/attempts/` like stage 10 — never overwrite.
QC before presenting: ffprobe duration **≥45s** (record `measured_length_s`), lipsync + identity vs locked sheets (zoom before accusing), script spoken exactly (transcribe if in doubt — video-understand skill), b-roll from approved clips only, muted test for vertical variants, VO fits its b-roll window (judge by silencedetect content-end, d-161). QC is report-only — regeneration is the Director's call (d-114/d-159).

### 5. Video gate + delivery
**GATE:** master + platform variants (free ffmpeg vertical blur-pad per platform-publishing) presented with QC findings. END TURN. On approval: status `approved`, files copied to `delivery/<platform>/spotlights/`, caption text files per platform (link policy d-174: spotlight posts MAY carry the film link — trailer-class, not teaser-class), `--unit-done SP<nn>`, log the decision.
**Metadata is part of delivery (d-192, MANDATORY per video):** author the video's `metadata` block in spotlight_kit — title (click-worthy, in-voice), description (first line = hook), **YouTube `tags` list (≥5 entries, ≤500 chars total — the settings field, distinct from hashtags)**, and `hashtags_by_platform`. Write them into the delivered `metadata.txt` (youtube: TITLE/DESCRIPTION/TAGS/HASHTAGS/SETTINGS) and `caption.txt` files. If the production has an active `trend_kit` selection, apply its metadata placements here and record the ids in `metadata.trend_refs`.
Then ASK: **another video (different characters/subject welcome), or close the stage?**

## Closing
On "close": `checkpoint.py write <slug> character-spotlight --status completed --approved --artifact spotlight_kit=artifacts/spotlight_kit.json`, log the closing decision. Every video entry must be `approved` or `rejected` — nothing half-generated left unrecorded.

## Pitfalls
- Skipping intake and inventing a subject — the six questions are the Director's steering wheel; ask them every video.
- Mentioning the next episode/session in ANY script line without an explicit Director order (d-184) — teases are the Director's call, never the writer's.
- Voicing b-roll VO with raw TTS preset lines — clone from the character's actual in-video segment audio, or the voice audibly shifts at every b-roll cut (d-184).
- Treating a talking segment as a portrait animation — it is a FILM SHOT: locked set, locked sheet references, anchors verbatim, or identity drifts on first contact.
- Launching a batch without a measured unit price — SJinn has no cost preflight; the probe-then-delta law is binding.
- Forgetting `whoami` membership check — credits alone don't unlock SJinn generation.
- Scripts that sound like a marketer, not the character — the voice-study test in the spotlight-writer agent is binding.
- Treating provider result URLs as storage — download immediately; the artifact is the local file.
- Forgetting this stage exists on the NEXT production: it is offered after stage 11 there too.
