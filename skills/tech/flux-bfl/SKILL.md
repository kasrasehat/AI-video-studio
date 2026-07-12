---
name: flux-bfl
description: "Prompting and API guide for Black Forest Labs FLUX image models — T2I generation, I2I editing, multi-reference character consistency, typography, plus BFL API mechanics (endpoints, polling, pricing). Use when: generating or editing still images with FLUX, writing/refining a FLUX prompt, picking a FLUX model, or calling the BFL API."
---

# FLUX (BFL): Prompting + API

Requires `BFL_API_KEY` in `.env` (create at https://dashboard.bfl.ai/get-started). Prompting knowledge first; API mechanics second.

## Prompting

### Critical Rules

1. **NO negative prompts** - FLUX does not support negative prompts; describe what you want
2. **Be specific** - Vague prompts produce mediocre results
3. **Use natural language** - Prose/narrative style works best
4. **Specify lighting** - Lighting has the biggest impact on quality
5. **Quote text** - Use "quoted text" for typography rendering
6. **Hex colors** - Use #RRGGBB format with color description

### Prompt Structure Formula

```
[Subject] + [Action/Pose] + [Style/Medium] + [Context/Setting] + [Lighting] + [Camera/Technical]
```

### Core Principles

- **Positive descriptions only.** Wrong: "a portrait of a woman, no glasses, no hat, no makeup". Correct: "a portrait of a woman with natural skin, clear face, bare head, visible eyes".
- **Specificity matters.** "a cat sitting" → generic. "A fluffy orange tabby cat with bright green eyes sitting regally on a vintage velvet armchair, afternoon sunlight streaming through lace curtains, warm golden hour lighting, shallow depth of field, shot on medium format film" → excellent.
- **Prose beats keyword lists.** Write descriptive sentences, not "woman, portrait, beautiful, 8k, detailed".
- **Word order matters.** FLUX prioritizes elements appearing earlier — front-load the subject and key elements.
- **Medium length.** Optimal is ~30-80 words (up to 512 tokens supported). Too short lacks direction; too long becomes unfocused.
- **Iterate one element at a time:** core subject/action → style/medium → lighting/atmosphere → technical details.

### Lighting Vocabulary

- Natural: golden hour (warm, soft, directional) / blue hour / overcast (soft, diffused, even) / harsh midday (high contrast) / dappled forest light
- Studio: softbox / rim light (edge separation) / butterfly / Rembrandt (dramatic triangle) / split lighting
- Atmospheric: volumetric fog / god rays / neon glow / candlelight / practical lighting (visible sources in scene)
- Mood: high key (bright, airy) / low key (moody) / chiaroscuro / dramatic noir shadows

### Camera & Composition Vocabulary

- Camera/film: "shot on Hasselblad X2D" (medium format detail), "shot on Kodak Portra 400" (film grain, organic color), "early digital camera aesthetic" (2000s candid)
- Lenses: 85mm f/1.4 (portrait, creamy bokeh), 24mm f/2.8 (wide environmental), 50mm f/1.2 (natural perspective), 135mm f/2 (compressed), macro, tilt-shift
- Aperture: f/1.4 extremely shallow DOF, f/2.8 moderate blur, f/8 sharp throughout, f/16 maximum sharpness
- Framing: extreme close-up / close-up / medium shot / full shot / wide shot / establishing shot
- Angles: eye level, low angle (powerful), high angle (diminished), Dutch angle (tension), bird's eye, worm's eye
- Composition: rule of thirds, centered symmetry, leading lines, frame within frame, negative space

### Complete T2I Example

```
A weathered fisherman in his 70s with deep wrinkles and a salt-and-pepper beard,
wearing a navy cable-knit sweater, standing at the helm of his wooden boat.
Golden hour sunlight from the left creates dramatic rim lighting on his profile.
Shot on Hasselblad with 85mm lens at f/2.8, shallow depth of field with harbor
lights creating soft bokeh in the background. Kodak Portra 400 color science.
```

### Image-to-Image (I2I) Editing

All FLUX.2 models edit images natively — pass the source as `input_image` and describe the change. FLUX.2 beats the older FLUX.1 Kontext for editing.

- **Simple modifications:** "Change the car color to red", "Make the sky a dramatic sunset", "Add snow to the ground"
- **Explicit preservation** — state what must NOT change:
  ```
  Change the background to a beach scene while keeping the subject's
  pose, clothing, and expression exactly the same
  ```
- **Style preservation:** "...but maintain the photograph's realistic style and color grading"
- **Complex transformations:** break into sequential single-element edits (furniture → fireplace → lighting → aging) rather than one giant instruction.

Pitfalls:

```
Bad: Make it look better
Good: Increase contrast, add warm color grading, sharpen details

Bad: Change the background
Good: Replace the office background with a tropical beach at sunset,
      maintaining the subject's exact position and lighting direction
```

Best practices: start simple; be explicit about what changes AND what stays; reference existing elements; iterate small edits; always state style/composition preservation needs.

### Multi-Reference Editing (character consistency)

FLUX.2 accepts multiple input images (`input_image`, `input_image_2`, ... `input_image_8`). Reference them by number in the prompt:

- "The subject from image 1 in the environment from image 2"
- "Apply the style of image 2 to the scene in image 1"
- "The person from image 1 wearing the outfit from image 2, in the pose from image 3"

| Model | Max References |
|-------|----------------|
| FLUX.2 [klein] | 4 images |
| FLUX.2 [pro/max/flex] | 8 images |

Character-consistent series recipe: create the character reference with [max] → generate consistent variations with [max]/[pro] using reference images → quick iterations with [klein].

### Typography

Use FLUX.2 [flex] for best text rendering.

1. Quote the exact text: `A poster with "HELLO WORLD" in bold letters`
2. Specify font style: `"ADVENTURE" in bold sans-serif typography`, `"Welcome" in elegant cursive script`, `"CHAPTER ONE" in classic serif typeface`
3. Describe size hierarchy: `Large headline "BREAKING NEWS" above smaller subtext "Details inside"`
4. Indicate placement: `"OPEN" sign centered in storefront window`
5. Front-load the text early in the prompt for better accuracy.

### Model Selection

| Priority      | Recommended Model               |
| ------------- | ------------------------------- |
| Speed         | FLUX.2 [klein]                  |
| Quality       | FLUX.2 [max]                    |
| Balance       | FLUX.2 [pro]                    |
| Typography    | FLUX.2 [flex]                   |
| Image Editing | FLUX.2 [klein], [pro], or [max] |
| Local/Free    | FLUX.2 [dev]                    |
| Inpainting    | FLUX.1 Fill                     |

- Character consistency: FLUX.2 [max] or [pro] (multi-reference, maintains identity across scenes)
- Hero/premium images: [max] (also has grounding search for real-time info)
- FLUX.1 family only when explicitly required (Kontext editing, Fill inpainting)

```
Speed?      → FLUX.2 [klein]
Quality?    → FLUX.2 [max]
Balance?    → FLUX.2 [pro]
Text?       → FLUX.2 [flex]
Edit?       → FLUX.2 [klein/pro/max] with reference images
Free?       → FLUX.2 [dev]
```

## API Mechanics

### Authentication

Header on every request:

```bash
x-key: YOUR_API_KEY
```

Check the key is set first: `echo $BFL_API_KEY`. If empty or "Not authenticated": create a key at https://dashboard.bfl.ai/get-started and save `BFL_API_KEY=bfl_...` to `.env` (never commit it).

### Base Endpoints

| Region | Endpoint                | Use Case                    |
| ------ | ----------------------- | --------------------------- |
| Global | `https://api.bfl.ai`    | Default, automatic failover |
| EU     | `https://api.eu.bfl.ai` | GDPR compliance             |
| US     | `https://api.us.bfl.ai` | US data residency           |

### Model Endpoints & Pricing

1 credit = $0.01 USD. FLUX.2 pricing is megapixel-based: `(firstMP + (outputMP-1) * mpPrice) + (inputMP * mpPrice)` in cents.

| Model             | Path                  | 1st MP | +MP  | 1MP T2I | 1MP I2I | Best For                           |
| ----------------- | --------------------- | ------ | ---- | ------- | ------- | ---------------------------------- |
| FLUX.2 [klein] 4B | `/v1/flux-2-klein-4b` | 1.4c   | 0.1c | $0.014  | $0.015  | Real-time, high volume             |
| FLUX.2 [klein] 9B | `/v1/flux-2-klein-9b` | 1.5c   | 0.2c | $0.015  | $0.017  | Balanced quality/speed             |
| FLUX.2 [pro]      | `/v1/flux-2-pro`      | 3c     | 1.5c | $0.03   | $0.045  | Production, fast turnaround        |
| FLUX.2 [max]      | `/v1/flux-2-max`      | 7c     | 3c   | $0.07   | $0.10   | Maximum quality                    |
| FLUX.2 [flex]     | `/v1/flux-2-flex`     | 5c     | 5c   | $0.05   | $0.10   | Typography, adjustable controls    |

| FLUX.1 Model         | Path                     | Price/Image | Best For                      |
| -------------------- | ------------------------ | ----------- | ----------------------------- |
| FLUX.1 Kontext [pro] | `/v1/flux-kontext`       | $0.04       | Image editing with context    |
| FLUX.1 Kontext [max] | `/v1/flux-kontext-max`   | $0.08       | Max quality editing           |
| FLUX1.1 [pro]        | `/v1/flux-pro-1.1`       | $0.04       | Standard T2I, fast & reliable |
| FLUX1.1 [pro] Ultra  | `/v1/flux-pro-1.1-ultra` | $0.06       | Ultra high-resolution         |
| FLUX1.1 [pro] Raw    | `/v1/flux-pro-1.1-raw`   | $0.06       | Candid photography feel       |
| FLUX.1 Fill [pro]    | `/v1/flux-pro-1.0-fill`  | $0.05       | Inpainting                    |

### Request Flow

```
1. POST request to model endpoint
   └─> Response: { "polling_url": "..." }

2. GET polling_url (repeat until complete)
   └─> Response: { "status": "Pending" | "Ready" | "Error", ... }

3. When Ready, download result URL
   └─> URL expires in 10 minutes - download immediately
```

**Result URLs expire after 10 minutes** — download images immediately; never store the URLs.

### Quick Start

```bash
curl -s -X POST "https://api.bfl.ai/v1/flux-2-pro" \
  -H "x-key: $BFL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A serene mountain landscape at sunset", "width": 1024, "height": 1024}'
```

Response:

```json
{ "id": "abc123", "polling_url": "https://api.bfl.ai/v1/get_result?id=abc123" }
```

Poll (`curl -s "POLLING_URL" -H "x-key: $BFL_API_KEY"`) until:

```json
{ "status": "Ready", "result": { "sample": "https://...", "seed": 1234 } }
```

Then download: `curl -s -o output.png "IMAGE_URL"`.

### Image Input for Editing

Prefer URLs over base64 — the API fetches them automatically.

```bash
curl -X POST "https://api.bfl.ai/v1/flux-2-pro" \
  -H "x-key: $BFL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "The person from image 1 in the environment from image 2",
    "input_image": "https://example.com/person.jpg",
    "input_image_2": "https://example.com/background.jpg"
  }'
```

### Rate Limits & Integration Style

- Standard endpoints: **24 concurrent requests** (FLUX.1 Kontext Max: 6 — avoid when rate-limit sensitive).
- **Polling** for scripts/CLI/single requests (start here); **webhooks** (`webhook_url` param) for high-volume production.

<!-- adapted from OpenMontage (.agents/skills/flux-best-practices/SKILL.md + rules/, merged with .agents/skills/bfl-api/SKILL.md) -->
