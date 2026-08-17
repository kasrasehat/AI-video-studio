# Dub Pass Director — stage 13 (OPTIONAL, repeatable — d-196)

Localize a FINISHED production: per-language dubs layered on the master, shipped per the d-195 platform policy. Like stage 12, this stage is OFFERED, never assumed; it can run any time after publishing (even weeks later), and re-enter for more languages.

**Consumes:** `render_report` (the finished master). **Produces:** `artifacts/dub_kit.json` (schema `dub_kit`).
**Gate:** per language (d-114 — cost stated first). **Resume unit:** language. **Optional:** `skipped --approved` never blocks.

## Backend law (d-195/d-196)

- **YouTube = ElevenLabs automatic dubbing → AUDIO TRACKS** on the one existing upload (multi-language audio, ≤6 tracks/video). Dubbing v2, 90+ languages, preserves voice character and background audio. Reachable ONLY with the Director's VPN on (d-150 — edge 403 otherwise; a 403 means VPN, not a broken key).
- **Higgsfield `dubbing` = lip-synced dubbed VIDEO** (18 languages, no Persian/Dutch). NEVER uploaded to YouTube (separate re-upload = d-195 violation). Legal use: TikTok/Instagram verticals, where per-language posts are platform-native. Higgsfield-first (d-147) does not apply here for YouTube because Higgsfield's output shape is unusable for MLA — decided d-196.
- **YouTube auto-dub** = zero-cost baseline where the channel offers it; replaced by our tracks as they're approved.

## Pricing anchors (verify at run time — probe law applies)

ElevenLabs automatic dubbing ≈ **2,000 credits/minute** of source (≈ $0.33/min watermarked, $0.50/min clean via API). The FIRST language of any session is the probe: record the actual credit burn from the subscription usage delta, then state the batch from measured units. Account tier quota is the real constraint — check remaining monthly credits BEFORE proposing a batch; overage/upgrade is a Director decision, never silent.

## Process (per session)

1. Offer + Director picks languages (record accent requests, e.g. Istanbul Turkish — Dubbing v2 supports locale variants). `checkpoint.py write <slug> dub-pass --status in_progress`.
2. **Verify language availability live** (VPN on): the languages resource/a dry call. A language the backend lacks is recorded `unavailable` in dub_kit — surfaced, never silently dropped.
3. Author `dub_kit.json` (source block + planned languages), validate. State per-language cost + quota headroom. **GATE per d-114.** END TURN.
4. On go: probe language first (create dubbing → poll → download `.mp3`/`.m4a` track + translated transcript), measure real credit burn, then run remaining approved languages.
5. **QC per language (report-only, d-114):** duration matches master ±1s; dialogue timing vs picture at 3 spot-points; music/SFX bed preserved under the new voices; transcribe a sample line back (video-understand) to sanity-check translation register (family tone, character names NEVER translated — Milo is Milo everywhere). The Director's listen decides.
6. On approval per language: `status approved`, deliver to `delivery/youtube/audio_tracks/<lang>/` (track + `.srt` + `localized_metadata.txt` with translated title/description — YouTube metadata localization), `--unit-done <lang>`, log.
7. Close (`completed --approved`) or stay open for more languages — Director's call. Upload day: YouTube Studio → the EXISTING video → Audio tracks (+ captions + localized metadata). Claude packages; the Director uploads.

## Pitfalls

- Uploading a dubbed COPY of the film to YouTube — the exact d-195 violation this stage exists to prevent.
- Trusting a remembered price — quota and per-minute rates drift; probe and read the account's real usage delta.
- ElevenLabs 403 → VPN off (d-150). Stop and tell the Director; do not rotate keys or retry blindly.
- Character names, catchphrases ("rule one"), and on-screen-text references translated away — spot-check them; the catchphrase must survive recognizably in every language.
- Dubbing the tiktok/instagram VERTICALS with ElevenLabs audio-only output — those platforms get either the original with translated burned captions, or (Turkish/Japanese/Chinese etc.) the Higgsfield lip-synced variant if the Director orders it.
- Forgetting this stage on the NEXT production — it is offered after stage 11/12 there too.
