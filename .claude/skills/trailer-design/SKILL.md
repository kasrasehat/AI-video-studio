---
name: trailer-design
description: "Design and cut a short teaser trailer for a finished film from its APPROVED clips — hook structure, beat selection, spoiler protection, title card, platform variants. Use when: planning or assembling the trailer in stage 11, choosing which moments tease without spoiling, or cutting a vertical teaser variant."
---

# Trailer Design

A trailer is the thumbnail's moving sibling: **15–30 seconds that sell the click without giving away the film.** It is cut from the film's APPROVED clips with ffmpeg — a re-edit, not a new generation — so the base trailer costs zero credits. Only optional extras (a generated title card) are paid and therefore Director-gated (d-114).

> **In this pipeline:** Used by stage 11 (publishing). The `thumbnail-artist` subagent carries BOTH visual-marketing tasks — thumbnail and trailer — because they share one curiosity strategy: the trailer opens the same question the thumbnail plants, and still doesn't answer it.

## The spoiler law (BINDING)

The trailer may use any approved clip EXCEPT the resolution. Concretely: the final scene's payoff, the twist's landing, and any beat that answers the film's central question are FORBIDDEN in the trailer. The last trailer image before the title card is the film's most unresolved instant — mid-fall, mid-gasp, mid-door-opening. A trailer that resolves its own tension is a summary, and summaries don't get clicks.

## Structure (15–30s, three movements)

1. **Hook (0–3s):** the single most arresting image of the film, cold open, no logos, no build-up. The first 2 seconds decide whether a scroller stays.
2. **Escalation (3s–T-5s):** 4–8 fast beats that raise stakes and speed up — each cut shorter than the last (e.g. 2.5s → 2.0s → 1.5s → 1.0s). Pull the film's most kinetic, funniest, and strangest moments in an order that implies a story WITHOUT being the story's order (trailer order serves tension, not chronology).
3. **Cliffhanger + card (last ~5s):** the unresolved instant, hard cut to the title card (film title + "WATCH NOW" or release line), optional 1s button gag after the card (family-film convention — a wink beat that leaves them smiling).

## Beat selection method

- Score every approved clip's candidate moments on three axes: motion energy, emotional legibility at a glance, and question-raising power. Pick across the whole film — a trailer sampling only act one reads flat.
- Dialogue: at most ONE short spoken line, and only if it works context-free. Trailers travel muted on feeds — every beat must work silent.
- Continuity rules DON'T apply here (a trailer may jump-cut across wardrobe states) but identity rules DO — nothing off-model, this is a first impression.

## Assembly (ffmpeg, free)

- Cut list is authored as `publishing_kit.trailer.beats[]`: clip_ref, in_s, out_s, order, per-beat note. Assemble per `skills/tech/ffmpeg` / `video-edit` recipes: trim → concat → hard cuts only (trailer transitions are cuts; crossfades kill urgency) → loudness-normalize.
- **Title card:** simplest is a text card built in ffmpeg (drawtext) over a dark frame or a still pulled from an approved clip. A GENERATED card (gpt_image_2, film logo treatment) is a paid call — propose, preflight cost, Director gates (d-114).
- **Audio:** clips carry their own Seedance audio; a music bed is added when the film's music backend is live (the trailer cue can be a shortened edit of the film's main theme — one more reason the theme is auditioned first). Master to −14 LUFS like every deliverable.
- **Variants:** 16:9 master always; a 9:16 vertical crop (reframe the beats, not letterbox) when the Director wants Shorts/TikTok teaser distribution — same beats, tighter framing.

## QC before the gate

Watch it three ways: (1) full attention — does tension build and stay unresolved? (2) muted — does it still work? (3) first-3-seconds only — would you stop scrolling? Verify no forbidden resolution beat leaked in, the title card is spelled exactly, and total runtime is 15–30s.

## Vertical micro-teaser set (d-173 — virality feature #1)

Beyond the main trailer, every release cuts **2-3 vertical (9:16) micro-teasers, 4-15s each**, from approved clips — the Shorts/Reels/TikTok discovery engine. Rules:
1. **One gag per teaser.** A micro-teaser is a single joke or single wow-moment, not a mini-trailer (e.g. the whistle-bubble pop; the time-freeze orbit; the sneeze launch).
2. **Design the loop.** End state ≈ start state so autoplay replays feel seamless — replay rate is the strongest Shorts ranking signal. Prefer clips whose last frame naturally hands back to their first (a settled pose, a returning camera), or cut ON matching action.
3. **Silent-first, sound-rewarding:** must work muted (burned hook text card in the vertical pad), but keep the clip's baked audio — the gag's sound is the reward for sound-on viewers.
4. **Funnel line** burned or in caption: the platform-appropriate "Full film on YouTube" pointer.
5. Free ffmpeg work (blur-pad vertical per assemble.py's recipe); no generation. Director previews each teaser before posting.

## First-3-seconds law pointer (d-173 — virality feature #2)

The trailer already cold-opens; the FILM must too — see the story/scene-division skills: scene 1 front-loads the production's most arresting visual inside 3 seconds. (Law lives there; noted here because the trailer's hook and the film's hook should be DIFFERENT arresting moments — never spend the same image twice.)
