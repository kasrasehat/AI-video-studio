---
name: platform-publishing
description: "Multi-platform release packaging and per-platform enrichment — YouTube (primary), TikTok, Instagram. Use when: building the per-platform delivery tree in stage 11, adapting captions/hashtags/formats per platform, planning teaser cadence, dubbing passes, or pre-post virality checks on marketing assets."
---

# Platform Publishing

One film, many storefronts. **YouTube is the flagship** — the full film lives there and every other platform funnels to it. TikTok and Instagram are discovery engines fed with vertical assets. Claude PACKAGES everything; the Director posts (Claude never uploads or publishes).

## The delivery tree (standard, built by stage 11)

```
projects/<slug>/delivery/
  youtube/     main_video/  trailer/  thumbnail/  metadata/  teasers/
  tiktok/      main_video/  trailer/  teasers/  metadata/
  instagram/   trailer/  teasers/  cover/  metadata/
```
Every folder is upload-ready: correct format, correct captions mode, and a `metadata/` folder of plain-text files (title.txt, description/caption.txt, hashtags.txt, tags.txt, pinned_comment.txt, chapters.txt, settings.txt) the Director can copy-paste at upload time. Assets are COPIES — the canonical files stay in renders/ and assets/.

## YouTube (PRIMARY — the film's home)

- **main_video/**: the youtube preset render + .srt sidecar. Upload settings in settings.txt: made_for_kids per the kit, category, altered-content (AI) disclosure checkbox reminder, monetization once eligible.
- **thumbnail/**: ALL approved thumbnail exports (1280x720) — upload 2-3 via Test & Compare (A/B policy, thumbnail-design skill); 48h refresh rule noted in settings.txt.
- **trailer/**: the 16:9 trailer — set as the CHANNEL TRAILER for non-subscribers, and premiere-tease it as a community post ~48h before the film.
- **teasers/**: the vertical micro-teasers posted as SHORTS from the same channel, each with the film linked via the Shorts "related video" feature — Shorts are the subscriber engine; the film is the payoff.
- **metadata/**: title, description (chapters included), tags, hashtags, pinned_comment (post within the first hour — early replies are the strongest free ranking signal).
- **Cadence**: teaser Shorts start 3-4 days before premiere (one per day), trailer as community post + channel trailer at T-48h, film as a PREMIERE (creates a live moment + chat), pinned comment immediately after, first 24h: reply to every comment.

## TikTok

- **main_video/**: the tiktok 9:16 render (burned captions) — TikTok accepts long video; post the FULL film there too (native uploads outperform links; the funnel is the profile link + comment).
- **trailer/**: 9:16 blur-pad version of the trailer.
- **teasers/**: the micro-teaser loops are the PRIMARY TikTok content — native, loopable, one gag each.
- **Trending audio (d-173 feature #5)**: before posting a teaser, check `tiktok_music_trending` on the Higgsfield MCP; when a trending sound fits, cut ONE extra teaser variant to that sound's rhythm (keep the original too). Trending-sound variants ride the sound's discovery page.
- **metadata/**: caption.txt (first line = hook, 1-2 sentences max), 3-5 hashtags (broad #animation + niche + branded), funnel line "full film on YouTube - link in bio".
- **Cadence**: teasers first (they scout the audience), film after the best teaser peaks.

## Instagram (Reels + profile)

- Reels cap length — the FILM does not go here; the **trailer/** (9:16) and **teasers/** are the content, with **cover/** (9:16-cropped thumbnail export) as each Reel's cover so the profile grid looks designed.
- **metadata/**: caption.txt per Reel (hook first line, funnel line "full film on YouTube - link in bio"), 3-5 hashtags visible (more adds noise, not reach).
- Stories: repost each Reel to Stories with a link sticker to the YouTube film (the only place Instagram allows a direct link).

## Multi-language dub pass (d-173 feature #3 — instructions for future products / on Director order)

Family animation is the most language-portable genre, and YouTube serves MULTI-AUDIO TRACKS on one video. When the Director orders a dub pass for a release: (1) priority languages by kids-animation audience size — Spanish, Portuguese, Hindi first; (2) generate dubs via ElevenLabs dubbing (or the Higgsfield dubbing tool — check Higgsfield first per d-147) from the master's dialogue; (3) deliver as separate audio tracks uploaded in YouTube Studio (one video, multi-audio) — never as separate re-uploads; (4) per-language metadata translations go in delivery/youtube/metadata/<lang>/; (5) each language's dub is Director-gated like any cue (d-114 — per-language cost stated first). NO regeneration of existing film content — the dub layers ON the finished master.

## Virality predictor — marketing assets only (d-173 feature #6)

The Higgsfield `virality_predictor` stays OUT of the film pipeline (Director ruling) but MAY be run on MARKETING assets (trailer, micro-teasers) before posting: preflight its cost, run once per asset, report the score as one more signal at the Director's gate. Never gate the film itself on it; never re-edit art to chase the score without a Director order.

## Laws

- Claude packages; the Director posts. No tool ever publishes directly, even where publish tools exist (tiktok_publish etc.) — those run only on an explicit per-post Director order.
- Every platform's caption/metadata is WRITTEN FOR that platform (never paste YouTube descriptions into TikTok).
- The film's canonical home is YouTube; every other asset carries the funnel line.
- All packaging is free ffmpeg/file work from approved assets; anything needing GENERATION is per-item Director-gated as always.
