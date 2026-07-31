---
name: youtube-publishing
description: "Write click-optimized YouTube titles, descriptions, hashtags, tags, and channel-growth metadata for a finished film. Use when: authoring the publishing_kit metadata in stage 11, picking title/hashtag strategy, writing the description hook, or setting platform flags like made_for_kids."
---

# YouTube Publishing Metadata

Metadata is discovery: the algorithm reads it, search indexes it, and the viewer decides on ~2 seconds of it. Title + thumbnail are ONE unit — they are designed together (see `skills/tech/thumbnail-design`), each carrying half of the same curiosity gap.

> **In this pipeline:** Used by stage 11 (publishing). The `youtube-strategist` subagent reads brief, story, scene_list and the final cut's facts, then authors every field of `publishing_kit.metadata`. All copy is Director-gated before anything is posted. Claude never uploads or posts — the kit is handed to the Director.

## The expert-persona method (Director-supplied pattern, 2026-07-31)

Frame every metadata task as a role-primed expert brief — the Director's sample pattern, adapted per deliverable:

> "Act as a top YouTube growth expert and money-making coach. Help me build a full plan to grow my YouTube channel… Look at my topic, viewers, other channels, tools, and targets. Give me my channel focus, content themes, posting plan, video types, growth steps, watch-time tips, income plan, and a clear weekly action schedule."

> "Act as a YouTube numbers expert. Build a full system to improve my channel using data. Look at the key stats like views, click rate, how long people watch, retention graphs, new subscribers, where traffic comes from, likes and comments, and income…"

The working recipe distilled from these samples: **(1) claim the expert role, (2) enumerate the exact inputs to look at, (3) enumerate the exact outputs to deliver.** When authoring any metadata piece, write the internal brief in this three-part shape first (e.g. "Act as a top YouTube title strategist. Look at: the film's story, its funniest beat, the target audience from the brief, and the thumbnail's on-image text. Deliver: 4 title options under 60 characters, each with a different psychological angle, none repeating the thumbnail text."), then execute it. This forces completeness and keeps every field grounded in the film's actual artifacts instead of generic advice.

## Title (options go in `title_options[]`, Director picks)

- **≤ 60 characters** for the option you expect to win (YouTube truncates ~70; search results earlier). Schema allows 100 for experimental angles.
- Front-load the hook words — the first 3–4 words do the work on mobile.
- One curiosity gap, opened not closed: "Grandma Shrunk the Kids — Then Lost Them" beats "A Fun Family Shrinking Adventure".
- Never repeat the thumbnail's on-image text; the pair must ADD UP, not echo.
- Provide 3–4 options with genuinely different psychological angles (curiosity / emotion / stakes / keyword-search), each with its `angle` stated — same variant discipline as sheets and boards: different interpretations, not rerolls.
- Honest: the title must be paid off inside the film (retention collapse from clickbait outweighs any CTR gain).

## Description

- **`hook_first_125`:** the only part shown before "…more". A second sales pitch, not a summary — restate the curiosity gap in new words, no links, no hashtag spam here.
- **`full_text`:** 150–300 words. Natural-language keywords in the first two sentences (search reads them); then the film's premise WITHOUT spoiling the resolution; chapters if ≥3 distinct segments (`0:00` first, ascending); one CTA line (subscribe + what the next video gives them); credits/tools line if the Director wants the AI-made provenance stated.
- Hashtags live at the END of the description; the first 3 render above the title — order them so the best 3 lead.

## Hashtags & tags

- **Hashtags (visible):** 3–15 total (YouTube HARD-caps at 15 — one over and ALL are ignored). Mix: 1–2 broad-reach (#animation #shortfilm), 2–3 niche-exact (#pixarstyle #aifilm #familycomedy), 1 branded/series tag for channel continuity. No spaces, no punctuation beyond the #.
- **Tags (backend, `tags[]`):** ~500-char budget. Order: exact expected search phrase first ("grandma shrinks kids animation"), then title keywords, genre terms, style terms, misspelling variants. Tags are weak signal in 2026 — spend 10 minutes, not an hour.

## Platform flags (Director decisions, surfaced not assumed)

- **`made_for_kids`:** a family film is NOT automatically "made for kids" (COPPA flag kills comments, end screens, personalized ads). Present the tradeoff; the Director rules; record it in the artifact.
- **Category:** usually "Film & Animation" for this pipeline's output.
- **`pinned_comment`:** a question that invites replies ("Which room would YOU explore at 3 inches tall?") — comments in hour one are the strongest early-ranking signal you can influence for free.

## QC before the gate

Every claim in title/description exists in the film · title ≤ limits and not echoing thumbnail text · hashtag count ≤ 15 and formats valid · hook_first_125 stands alone · chapters' timecodes match the actual cut · options genuinely differ in angle.
