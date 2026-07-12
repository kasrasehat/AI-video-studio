---
name: video-understand
description: "Inspect video content locally using ffmpeg frame extraction and Whisper transcription — fully offline, no API keys. Use when: (1) Checking what a generated clip actually contains, (2) Sampling frames for visual/identity/continuity review, (3) Transcribing a clip's audio locally, (4) Verifying dialogue audio against the script."
---

# Video Understand

> **In this pipeline:** the qc-critic uses this to sample frames from generated clips for identity/continuity checks and to inspect dialogue audio for lipsync verification.

Understand video content locally: ffmpeg extracts representative frames, Whisper transcribes the audio. Fully offline, no API keys required. Read the extracted frame images with the Read tool to inspect them visually.

## Prerequisites

- `ffmpeg` + `ffprobe` (required) on PATH
- `openai-whisper` (optional, for transcription): `pip install openai-whisper`

## Workflow

### 1. Probe the clip

```bash
ffprobe -v quiet -print_format json -show_format -show_streams clip.mp4
```

Gives duration, resolution, codecs — sanity-check against the shot spec before sampling frames.

### 2. Extract frames

Three extraction modes; pick per the table below. All write JPEG frames (`-q:v 2` = high quality).

```bash
# scene mode (default): frames at detected scene changes
ffmpeg -y -i clip.mp4 -vf "select='gt(scene,0.3)',showinfo" -vsync vfr -q:v 2 frames/frame_%04d.jpg

# keyframe mode: codec I-frames
ffmpeg -y -i clip.mp4 -vf "select='eq(pict_type,I)'" -vsync vfr -q:v 2 frames/frame_%04d.jpg

# interval mode: one frame every N seconds (here: every 2s)
ffmpeg -y -i clip.mp4 -vf "fps=1/2" -q:v 2 frames/frame_%04d.jpg
```

| Mode | How it works | Best for |
|------|-------------|----------|
| `scene` | Detects scene changes via ffmpeg `select='gt(scene,0.3)'` | Most videos, varied content |
| `keyframe` | Extracts I-frames (codec keyframes) | Encoded video with natural keyframe placement |
| `interval` | Evenly spaced frames based on duration and frame budget | Fixed sampling, predictable output |

- If `scene` mode yields no frames (single continuous shot — common for generated clips), fall back to `interval` mode.
- For interval mode, choose the interval as `duration / max_frames` (the source tool defaults to a 20-frame budget).
- Frame timestamps: the `showinfo` filter logs `pts_time:` values to stderr — parse those to map each extracted frame to its timestamp.

### 3. Inspect frames

Use the Read tool on the frame image paths for visual understanding — identity, wardrobe, set continuity, framing.

### 4. Transcribe audio locally (Whisper)

Extract a 16 kHz mono WAV, then transcribe:

```bash
ffmpeg -y -i clip.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav
```

```python
import whisper

model = whisper.load_model("base")  # tiny | base | small | medium | large
result = model.transcribe("audio.wav")
print(result["text"])
for seg in result["segments"]:
    print(seg["start"], seg["end"], seg["text"])
```

Or via CLI if the `whisper` binary is installed: `whisper audio.wav --model base`.

- Model size trades speed for accuracy: `tiny`/`base` for quick checks, `small`+ when dialogue wording must be verified precisely.
- If audio extraction fails, the clip likely has no audio track — that itself is a QC finding for dialogue shots.
- Segment `start`/`end` times let you line the spoken words up against extracted frame timestamps (lipsync spot-check: does the mouth move during the segment window?).

## QC usage pattern

1. Probe → confirm duration/resolution match the generation manifest.
2. Extract frames (scene mode, fallback interval) → Read frames → check character identity and continuity against locked reference sheets.
3. Transcribe → diff against the scripted dialogue line.
4. Compare transcript segment timing with frames around the same timestamps for lipsync verification.

<!-- adapted from OpenMontage (.agents/skills/video-understand/SKILL.md + scripts/understand_video.py) -->
