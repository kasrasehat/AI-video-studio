# Sound Direction Director — stage 5b

Design the film's SOUND before a single clip is generated, so that what the video model bakes and what post adds never collide. This stage exists because the video model mixes everything it generates — dialogue, foley, ambience and any music it invents — into ONE stereo track that post can never unmix (d-160). Episode 2 proved the cost: clips prompted before the "No music." clause (d-103) carry baked score under whispered dialogue, and every post cue laid over them collides with it (Director order 2026-09-15, d-164).

**Consumes:** `scene_direction`, `scene_list`, `brief` (+ `asset_manifest` when voices are already locked). **Produces:** `artifacts/sound_plan.json` (schema `sound_plan`). **QA loop:** `qa-reviewer`, max 2 rounds, BLOCKING. **Parallel:** `sound-director` per scene range, ≤3. **Gate:** Director approves. **Resume unit:** scene.

## The two halves (BINDING — d-164)

Every sound class lives in exactly ONE half:

| Half | Owner | Contents |
|---|---|---|
| **baked** | stage 9, the video model | dialogue (quoted lines + delivery), foley, room/world ambience, DIEGETIC motifs the world itself makes (a clock's tick, birdsong, a phone's hum), the incoming ambience a hinge J-cut needs in the previous clip's tail |
| **post** | stage 10 | score (every cue, bed, swell, theme, motif that is not made by an object on screen), protected silences, non-diegetic transitions, exception SFX (d-160: only sounds no clip can carry, or a locked asset laid by post) |

Consequences: every generation Audio block ends with the `global.no_music_clause` (`No music.`); scored intentions in `scene_direction.sound_direction` ("strings bloom", "the score stops dead") are TRANSLATED here, once, into the physical sound that makes them (a chime struck, a held string on an instrument present in the world, a hum from a named throat) and recorded in `baked.translations`; the intention itself moves to `post.cue_intent` so stage 10 delivers the swell. Nothing is translated ad hoc by a clip producer any more — stage 9 pastes `baked.audio_block` verbatim.

## Vocal integrity (the second job)

Voices are baked by the video model per clip, so consistency is won by planning, not mixing:

1. **Register map.** Divide the film into spans and assign one register per span (whisper / hushed / conversational / full_voice / shouted / wordless). Adjacent clips in the same span must share it; a register change is a directed event (E02: the whisper ceiling holds from S01 until Luna wakes at S65, and the lift is the design). Write it into every scene's `register` and into the audio block's delivery words.
2. **One voice reference per speaker, film-wide** (`global.voice_references`). Never two samples for one character across scenes; never a re-encoded trim (upload the lossless canon sample).
3. **Loudness discipline in the prompt.** Name the mix hierarchy per scene (dialogue forward, ambience under, foley whisper-scaled) so clips arrive at comparable internal balance; post only normalizes.
4. **Baked motifs are prompted identically wherever they recur** (the tick's description is a fixed string across S01–S20) so the world's sound holds across cuts.
5. **Dialogue windows** every post cue must respect are listed per scene in `post.duck_windows`.

## Seam integrity (the third job)

Per boundary, `boundary_out.treatment` from the scene_list's `boundary_class_out` and the stage-5 transition: `j_cut` on hinges (name `jcut_seed_in` on the incoming scene and the lead in frames), `cue_continuous` where the direction says the music does not acknowledge a cut, `transient_mask` where a sourced impact lands on the cut, `crossfade_bed` for ambience-only seams, `hard_cut` where silence or a directed exit IS the event. Stage 10 executes these literally; assemble.py's audio_treatment leads come from here.

## Process

1. Read the brief's `music_direction`, the stage-5 `global` block and every scene's `sound_direction`, `mood`, `transition_out`, plus the scene_list's dialogue, `boundary_class_out` and `transition_out_hint`.
2. Author `global` yourself: the register map, the two class lists, the voice references (from asset_manifest when locked, else the character ids to be locked at stage 7), the no-music clause, the integrity rules, and `score_intent` (themes and arc as one paragraph — stage 10's Phase 2 designs the cue sheet from it).
3. Dispatch `sound-director` per scene range (≤3 in parallel; give each its neighbours). Each returns `scenes[]` fragments: register, baked (the exact audio block, ≤120 words, ending with the clause; the translations), post (score mode, cue intent, duck windows, motif placements, exception sfx), boundary_out.
4. Assemble; reconcile: baked motifs identical across recurrences; registers contiguous; every J-cut seed present on both sides of its hinge; no scored noun survives in any audio block; every `post.score == protected_silence` is deliberate and stated.
5. **QA loop (blocking, max 2):** `qa-reviewer` with the plan + scene_direction + brief + this stage's `review_focus`. Apply criticals; record `qa.rounds`.
6. Validate, checkpoint, gate.

## Gate presentation

The register map as a table (span | register | why); the class split; then per scene: scene | register | baked one-liner | post score mode + intent | boundary treatment. QA verdict. Options: approve / notes on spans / notes on scenes / abort.

## Downstream contract

- **Stage 9 (clip-producer):** `sound_plan.scenes[sid].baked.audio_block` is the Audio block, verbatim, plus the quoted dialogue lines; the clause is present or the prompt is invalid. If `sound_plan.json` is absent, STOP and report — do not translate sound_direction yourself (the E02 lesson).
- **Stage 10 (integration):** Phase 2 derives `audio_direction` from `global.score_intent` + every scene's `post` half; protected silences come from `post.score == protected_silence`; `boundary_out` drives `audio_treatment`; cue timecodes come from the ASSEMBLED CUT (d-159), never from scene estimates.

## Retroactive use (existing productions)

Run the stage against the approved direction, then audit the approved clips: any clip whose prompt lacks the clause or names a scored noun is listed with a listen note (baked music audible or not) and a regeneration cost; the Director gates each regeneration (d-114). The audit report lives in `sound_plan.metadata.clip_audit`.

## Pitfalls

- Letting a motif drift between halves (a "swell" that is half diegetic chime, half post cue — pick one).
- Writing audio blocks longer than the picture prompt can afford (≤120 words; the block is one paragraph).
- Register changes that are not events (a whisper scene followed by a conversational one with no story reason).
- Treating a locked asset (an alarm melody) as baked: it is laid by post, and the clip carries only its physical placeholder (E02 S64: "a soft twangy hum from the phone's tiny speaker").

## Seam laws the plan must anticipate (d-168 … d-174)

Write `boundary_out` knowing how stage 10 executes it: post cues overlap ≥ 4 s of real music across every cue seam, centred after the picture cut (never on it); a directed in-cue transition is planned as ONE cue in `post.cue_intent`; a `protected_silence` after a cue means the cue's body must still reach the boundary (the generator's own fade is not the silence); the closing cue ends on the last picture frame; an unmatched hinge is noted so stage 10 can crossfade it; a diegetic asset (`exception_sfx`) is given the full span of its beat. Never write "near-silence" into a cue intent — write the quiet bed you actually want to hear.
