---
name: music
description: "Generate music using the ElevenLabs Music API — instrumental tracks, songs with lyrics, jingles, and score cues. Use when: generating the film score or any background music, building a composition plan for granular control over sections/styles, or debugging music-generation errors."
---

# ElevenLabs Music Generation

> **In this pipeline:** Used in stage 10 to generate the score — one or more cues per `brief.music_direction`, typically instrumental, timed to scene durations from the edit.

Generate music from text prompts — supports instrumental tracks, songs with lyrics, and fine-grained control via composition plans. Requires `ELEVENLABS_API_KEY` in `.env`. Length range: 10 seconds to 5 minutes (`music_length_ms` 10000-300000).

## Quick Start

### Python

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

audio = client.music.compose(
    prompt="A chill lo-fi hip hop beat with jazzy piano chords",
    music_length_ms=30000
)

with open("output.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

### cURL

```bash
curl -X POST "https://api.elevenlabs.io/v1/music" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"prompt": "A chill lo-fi beat", "music_length_ms": 30000}' --output output.mp3
```

Force background-score behavior with `force_instrumental=True` (or write "no vocals" into the prompt).

## Methods

| Method | Description |
|--------|-------------|
| `music.compose` | Generate audio from a prompt or composition plan |
| `music.composition_plan.create` | Generate a structured plan for fine-grained control |
| `music.compose_detailed` | Generate audio + composition plan + metadata |
| `music.upload` | Upload audio for later inpainting workflows (enterprise-only feature) |

Provide either `prompt` or `composition_plan` — not both.

## Composition Plans

For granular control, generate a composition plan first, modify it, then compose:

```python
plan = client.music.composition_plan.create(
    prompt="An epic orchestral piece building to a climax",
    music_length_ms=60000
)

# Inspect/modify styles and sections
print(plan.positiveGlobalStyles)  # e.g. ["orchestral", "epic", "cinematic"]

audio = client.music.compose(
    composition_plan=plan,
    music_length_ms=60000
)
```

## Prompting

Structure prompts as: genre/style, mood, instruments, tempo/energy, use case.

- Genre/Style: "indie rock", "lo-fi hip hop", "orchestral"
- Mood: "uplifting", "melancholic", "tense"
- Instruments: "acoustic guitar", "synth pads", "strings"
- Tempo/Energy: "slow", "upbeat", "driving"
- Context: "underscore for a quiet farewell scene"

## Content Restrictions

- Cannot reference specific artists, bands, or copyrighted lyrics
- `bad_prompt` errors include a `prompt_suggestion` with alternative phrasing
- `bad_composition_plan` errors include a `composition_plan_suggestion`

## Error Handling

```python
try:
    audio = client.music.compose(prompt="...", music_length_ms=30000)
except Exception as e:
    print(f"API error: {e}")
```

Common errors: 401 (invalid key), 422 (invalid params), 429 (rate limit).

<!-- adapted from OpenMontage (.agents/skills/music/SKILL.md) -->

## Cue-transition craft (BINDING — d-161, Director order 2026-07-31 + research)

Smoothness between cues, and between music and silence, is a first-class quality criterion — but a DIRECTED hard exit (a button on a zap, a stab on a dunk, a dead-stop on a valve, a suction into a sneeze) is a story event and is NEVER smoothed away. Everything else follows these rules:

1. **Sneak-in by default:** every cue entrance ramps (0.5–2s `fade_in_s` in the mix) unless the direction demands a cold hit. Creeping/tiptoe cues get the long ramps (1.5–2s); swells get short click-guards (0.3–0.6s) because the composition already ramps.
2. **Sneak-out or dovetail at cue→cue splices:** when one cue ends where another begins, the outgoing cue gets a 0.5–1.5s `fade_out_s` under the incoming entrance (a mixed-level dovetail — the film-editing "sound bridge"/crossfade family). Never butt-splice two cues at full level.
3. **Music→silence:** unless the silence IS the event (protected silences arrive via directed exits), leave silence via a relax written into the cue (ask the generator for "relaxing onto a single held note / soft tail") plus a mix-level fade-out. Silence→music re-entries always sneak in.
4. **Emotional gradation (the Director's law):** feeling changes SUBTLY. Adjacent cues must share at least TWO bridge parameters: overlapping instrumentation (one instrument carries across), related key (same family — relative/closely-related keys), or tempo stepped ≤ ~10–15%. After a tender/romantic scene the next cue OPENS in the inherited warmth (soft, sincere, same palette) and only then rotates toward its own character — a playful cue following a lullaby starts soft-and-warm and earns its mischief over its first bars. Write this gradient INTO the cue prompt ("open gently inheriting the previous lullaby's warmth, then...").
5. **Level-matched handoffs:** adjacent cues sit within ~2dB of each other at the splice (set per-cue `gain_db` accordingly); the master two-pass loudnorm is not a substitute for cue-level balance.

Mix-side ramps live in `edit_decisions.audio.music[].fade_in_s/fade_out_s` (assemble.py applies them); composition-side gradients live in the cue prompts. Both are used together.

## Cue fitting (BINDING — d-170/d-172, E02 seam review)

The Music API composes an ENDING on every file — a 3.5–8 s fade-out — and often a soft 1.5–4 s head, whatever the prompt says ("no fade-out", "excerpt from the middle", "hold full energy" were all ignored across two full regenerations). Therefore: generate every cue at slot + 3 s; never rely on the file's own edges; before mixing, MEASURE the usable body (level ≥ body − 6 dB) and FIT the cue — extend the body by repeating its last phrase under 1.0 s equal-power splices to reach slot_end + 4 s, start it `usable_start` early — and let the mix make every entrance and exit (equal-power 1.0 s in / 3.0 s out). Never ask a cue for "near-silence": the model renders true digital silence (E02 MC14 v3). A directed internal event ("the chase drops at nine seconds") is not reliably placed; splice the cue's own sections at the picture cut instead of paying for another take.
