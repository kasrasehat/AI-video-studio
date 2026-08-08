# Stage 12 — Character Spotlight (OPTIONAL)

Direct-to-audience videos where the film's characters talk to the viewer — introduce themselves, talk about the movie, tease the next session, or any subject the Director orders — optionally intercut with b-roll from the approved film clips. Generated with **HeyGen** (`skills/tech/heygen/SKILL.md`, BINDING), scripted by the **spotlight-writer** subagent. Minimum **45 seconds** of content per video. The stage loops: one video at a time, each fully gated, until the Director closes the stage.

## Rule -1 — this stage is OPTIONAL

Never start it unprompted. After stage 11 closes (or on `/resume` when `next` reports it as optional-available), OFFER it in one short paragraph: what a spotlight video is, that it uses HeyGen, that each video is individually priced and gated. Then the Director decides:
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

### 3. Payload (spotlight-writer, task "payload")
The writer converts the approved script into the COMPLETE HeyGen request payload(s) per the chosen path (default `heygen_image_mode_plus_local_assembly`; `heygen_studio_one_shot` only when `heygen_avatar_id`s exist — see the tech skill). Save into `generation.payload` BEFORE anything is spent (d-114). State the cost estimate (HeyGen credits from the Director's account + any ElevenLabs voice audio, VPN law d-150).
**GATE (spend):** cost + payload summary. END TURN. On approval only: upload assets (record `asset_ids`), submit, poll, download to `assets/spotlights/`, ffprobe.

### 4. Assemble + QC
Image-mode path: assemble talking segments + b-roll locally (video-edit recipes; loudnorm to −14 LUFS like every deliverable; captions per-preset law — srt sidecar for youtube, burned for tiktok, none on master). Master to `renders/spotlights/SP<nn>_master.mp4`, versioned in `renders/attempts/` like stage 10 — never overwrite.
QC before presenting: ffprobe duration **≥45s** (record `measured_length_s`), lipsync watch-through, identity vs locked sheets, script spoken exactly, b-roll byte-familiar (approved clips only), muted test for vertical variants. QC is report-only — regeneration is the Director's call (d-114/d-159).

### 5. Video gate + delivery
**GATE:** master + platform variants (free ffmpeg vertical blur-pad per platform-publishing) presented with QC findings. END TURN. On approval: status `approved`, files copied to `delivery/<platform>/spotlights/`, caption text files per platform (link policy d-174 applies: spotlight posts MAY carry the film link — they are trailer-class, not teaser-class), `--unit-done SP<nn>`, log the decision.
Then ASK: **another video (different characters/subject welcome), or close the stage?**

## Closing
On "close": `checkpoint.py write <slug> character-spotlight --status completed --approved --artifact spotlight_kit=artifacts/spotlight_kit.json`, log the closing decision. Every video entry must be `approved` or `rejected` — nothing half-generated left unrecorded.

## Pitfalls
- Skipping intake and inventing a subject — the six questions are the Director's steering wheel; ask them every video.
- Letting HeyGen re-imagine the character (generic avatar look, regenerated portrait) — the animated image is a LOCKED asset, full stop.
- Scripts that sound like a marketer, not the character — the voice-study test in the spotlight-writer agent is binding.
- Counting on HeyGen for platform variants — the master is 16:9; verticals are OUR free ffmpeg work.
- Treating presigned download URLs as storage — they expire; the artifact is the downloaded file.
- Forgetting this stage exists on the NEXT production: it is offered after stage 11 there too.
