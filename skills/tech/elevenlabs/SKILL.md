---
name: elevenlabs
description: "Generate speech and design/clone character voices with the ElevenLabs API. Use when: designing or auditioning candidate character voices in stage 7, rendering dialogue or narration lines (TTS), cloning a voice from a reference recording, or debugging pronunciation/pacing in generated speech."
---

# ElevenLabs Audio Generation

> **In this pipeline:** Used in stage 7 to design ~2 candidate voices per character from `lock_descriptors.voice_spec` and render two audition lines per candidate (a neutral line + an emotional line) to `assets/voices/<char_id>_<variant_id>.mp3`. The Director's pick becomes the locked `reference_audio` passed to Seedance for every clip where that character speaks.

Requires `ELEVENLABS_API_KEY` in `.env`.

## Text-to-Speech

```python
from elevenlabs.client import ElevenLabs
from elevenlabs import save, VoiceSettings
import os

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

audio = client.text_to_speech.convert(
    text="Welcome to my video!",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_multilingual_v2",
    voice_settings=VoiceSettings(
        stability=0.5,
        similarity_boost=0.75,
        style=0.5,
        speed=1.0
    )
)
save(audio, "voiceover.mp3")
```

### Models

| Model | Quality | SSML Support | Notes |
|-------|---------|--------------|-------|
| `eleven_multilingual_v2` | Highest consistency | None | Stable, production-ready, 29 languages |
| `eleven_flash_v2_5` | Good | `<break>`, `<phoneme>` | Fast, supports pause/pronunciation tags |
| `eleven_turbo_v2_5` | Good | `<break>`, `<phoneme>` | Fastest latency |
| `eleven_v3` | Most expressive | None | Alpha — unreliable, needs prompt engineering |

**Choose:** multilingual_v2 for reliability, flash/turbo for SSML control, v3 for maximum expressiveness (expect retakes).

### Voice Settings

| Parameter | Range | Default | Effect |
|-----------|-------|---------|--------|
| `stability` | 0.0-1.0 | 0.5 | Lower = more expressive/variable |
| `similarity_boost` | 0.0-1.0 | 0.75 | Higher = closer to original voice |
| `style` | 0.0-1.0 | 0.0 | Style exaggeration (v2 models) |
| `speed` | 0.5-2.0 | 1.0 | Playback speed multiplier |

Presets by delivery style:

| Style | stability | similarity | style | speed |
|-------|-----------|------------|-------|-------|
| Natural/professional | 0.75-0.85 | 0.9 | 0.0-0.1 | 1.0 |
| Conversational | 0.5-0.6 | 0.85 | 0.3-0.4 | 0.9-1.0 |
| Energetic/YouTuber | 0.3-0.5 | 0.75 | 0.5-0.7 | 1.0-1.1 |

### Pauses Between Sections

**With flash/turbo models:** SSML break tags inline (max 3s per break; excessive breaks can cause speed artifacts):
```
...end of section. <break time="1.5s" /> Start of next...
```

**With multilingual_v2 / v3:** No SSML. Use paragraph breaks (blank lines, ~0.3-0.5s natural pause) or insert silence in post with ffmpeg.

**WARNING:** `...` (ellipsis) is NOT a reliable pause — it can be vocalized. Do not use ellipsis as a pause mechanism.

### Pronunciation Control

- **Phonetic spelling (any model):** write words as pronounced — `Janus` → `Jan-us`, `nginx` → `engine-x`. Dashes, capitals, apostrophes guide pronunciation.
- **SSML phoneme tags (flash/turbo only):** `<phoneme alphabet="ipa" ph="ˈdʒeɪnəs">Janus</phoneme>`

### Long-form Continuity (Stitching)

For consistent delivery across consecutive generations (multi-line dialogue), chain request ids:

```python
result1 = client.text_to_speech.convert_with_timestamps(
    text="First paragraph...",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_multilingual_v2"
)
request_id_1 = result1.request_id

result2 = client.text_to_speech.convert(
    text="Second paragraph...",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_multilingual_v2",
    previous_request_ids=[request_id_1]
)
```

### Iterative Workflow

1. Generate → listen → identify pronunciation/pacing issues
2. Adjust: phonetic spellings, break tags, voice settings
3. Regenerate. If pauses aren't precise enough, add silence in post with ffmpeg rather than fighting the TTS engine.

## Voice Design (new voices from text descriptions)

**Source gap — verify against live API before building stage 7.** The vendored OpenMontage reference does not document ElevenLabs' Voice Design (text-to-voice) endpoints, so no parameter shapes are recorded here; pull the current `text-to-voice` API from the official ElevenLabs docs rather than guessing. Candidate-voice approaches that ARE documented and work today:

1. **Audition library voices:** `client.voices.get_all()` lists voices with names/ids; pick candidates matching `voice_spec`, render the two audition lines per candidate.
2. **Differentiate candidates** with `VoiceSettings` sweeps (see presets table above) — the same voice at different stability/style/speed reads as distinct deliveries.
3. **Clone from a reference recording** when one exists (below), then audition the clone.

## Voice Cloning

### Instant Voice Clone

```python
with open("sample.mp3", "rb") as f:
    voice = client.voices.ivc.create(
        name="My Voice",
        files=[f],
        remove_background_noise=True
    )
print(f"Voice ID: {voice.voice_id}")
```

- Use `client.voices.ivc.create()` (not `client.voices.clone()`)
- Pass file handles in binary mode (`"rb"`), not paths
- Convert m4a first: `ffmpeg -i input.m4a -codec:a libmp3lame -qscale:a 2 output.mp3`
- Multiple samples (2-3 clips) improve accuracy
- Save voice ID for reuse

**Professional Voice Clone:** requires Creator plan+, 30+ min of clean audio, captcha verification, then 3-6 h training (`client.voices.create_professional_voice_clone`, `get_pvc_verification_captcha`, `verify_pvc`, `start_pvc_training`).

## Voice Management

```python
voices = client.voices.get_all()
for voice in voices.voices:
    print(f"{voice.name}: {voice.voice_id}")

client.voices.delete(voice_id="your_voice_id")
```

Known-good library voices: George `JBFqnCBsd6RMkjVDRZzb` (warm narrator), Rachel `21m00Tcm4TlvDq8ikWAM` (clear female), Adam `pNInz6obpgDQGcFmaJgB` (professional male).

## Sound Effects & Music

ElevenLabs also generates SFX (`client.text_to_sound_effects.convert`) and music (`client.music.compose` — not `.generate()`). Use the dedicated skills: `skills/tech/sound-effects` and `skills/tech/music`.

## Errors & Rate Limits

```python
from elevenlabs.core.api_error import ApiError

try:
    audio = client.text_to_speech.convert(...)
except ApiError as e:
    if e.status_code == 429:
        print("Rate limited - wait and retry")
    elif e.status_code == 401:
        print("Invalid API key")
```

| Code | Meaning | Action |
|------|---------|--------|
| 401 | Invalid API key | Check API key |
| 403 | Feature not available | Upgrade tier |
| 422 | Invalid parameters | Check request body |
| 429 | Rate limited | Wait and retry |

Concurrency by tier (TTS): Free 2, Starter 3, Creator 5, Pro 10, Scale 15.

<!-- adapted from OpenMontage (.agents/skills/elevenlabs/SKILL.md + reference.md) -->
