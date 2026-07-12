---
name: sound-effects
description: "Generate sound effects from text descriptions using ElevenLabs — ambient beds, cinematic impacts, foley, loops. Use when: generating scene SFX or ambience in stage 10, creating looping background textures, or tuning duration/prompt-influence for a sound cue."
---

# ElevenLabs Sound Effects

> **In this pipeline:** Used in stage 10 to generate SFX and ambience per `scene_direction.sound_direction` — one file per cue, duration matched to the scene's edit timing.

Generate sound effects from text descriptions — supports looping, custom duration, and prompt adherence control. Requires `ELEVENLABS_API_KEY` in `.env`.

## Quick Start

### Python

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

audio = client.text_to_sound_effects.convert(
    text="Thunder rumbling in the distance with light rain",
)

with open("thunder.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

### cURL

```bash
curl -X POST "https://api.elevenlabs.io/v1/sound-generation" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"text": "Thunder rumbling in the distance with light rain"}' \
  --output thunder.mp3
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | string (required) | — | Description of the desired sound effect |
| `model_id` | string | `eleven_text_to_sound_v2` | Model to use |
| `duration_seconds` | number \| null | null (auto) | Duration 0.5–30s; auto-calculated if null |
| `prompt_influence` | number \| null | 0.3 | How closely to follow the prompt (0–1) |
| `loop` | boolean | false | Generate a seamlessly looping sound (v2 model only) |

Billing: 100 chars/generation (auto duration) or 25 chars/second (fixed duration).

## Examples with Parameters

```python
# Looping ambient sound, 10 seconds
audio = client.text_to_sound_effects.convert(
    text="Gentle forest ambiance with birds chirping",
    duration_seconds=10.0,
    prompt_influence=0.5,
    loop=True,
)

# Short UI sound, high prompt adherence
audio = client.text_to_sound_effects.convert(
    text="Soft notification chime",
    duration_seconds=1.0,
    prompt_influence=0.8,
)
```

## Output Formats

Pass `output_format` as a query parameter (cURL) or SDK parameter:

| Format | Description |
|--------|-------------|
| `mp3_44100_128` | MP3 44.1kHz 128kbps (default) |
| `pcm_44100` | Raw uncompressed CD quality |
| `opus_48000_128` | Opus 48kHz 128kbps — efficient compressed |
| `ulaw_8000` | μ-law 8kHz — telephony |

Other supported rates: `mp3_22050_32` through `mp3_44100_192`, `pcm_8000` through `pcm_48000`, `alaw_8000`, `opus_48000_32` through `opus_48000_192`.

## Prompt Tips

- Be specific: "Heavy rain on a tin roof" > "Rain"
- Combine elements: "Footsteps on gravel with distant traffic"
- Specify style: "Cinematic braam, horror" or "8-bit retro jump sound"
- Mention mood/context: "Eerie wind howling through an abandoned building"

More example shapes: environmental ("Rain on a tin roof, steady and rhythmic"), action ("Sword being drawn from sheath, metallic ring"), mechanical ("Old car engine struggling to start then roaring to life").

## Error Handling

```python
try:
    audio = client.text_to_sound_effects.convert(text="Explosion")
except Exception as e:
    print(f"API error: {e}")
```

Common errors:
- **401**: Invalid API key
- **422**: Invalid parameters (check duration range, prompt_influence range)
- **429**: Rate limit exceeded

<!-- adapted from OpenMontage (.agents/skills/sound-effects/SKILL.md) -->
