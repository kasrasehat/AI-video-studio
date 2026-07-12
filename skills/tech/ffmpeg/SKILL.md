---
name: ffmpeg
description: "Video and audio processing recipes with FFmpeg — conversion, probing, trimming, concat, speed, fades, compression. Use when: probing clip metadata, converting formats, trimming/joining generated clips, adjusting speed or volume, compressing deliverables, or fixing codec/dimension errors."
---

# FFmpeg for Video Production

Core recipes for probing and transforming media in the pipeline. Commands are shell-neutral (work in bash and PowerShell) unless noted; this repo runs on Windows, so watch the concat-list encoding gotcha below.

## Get Video Info

```bash
# Duration only
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.mp4

# Full info
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4
```

## Convert GIF to MP4 (web/codec-safe)

```bash
ffmpeg -i input.gif -movflags faststart -pix_fmt yuv420p \
  -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" output.mp4
```

**Why these flags:**
- `-movflags faststart` - Moves metadata to start for web streaming
- `-pix_fmt yuv420p` - Ensures compatibility with most players
- `scale=trunc(...)` - Forces even dimensions (required by most codecs)

## Resize Video

```bash
# To 1920x1080 (maintain aspect ratio, add black bars)
ffmpeg -i input.mp4 -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" output.mp4

# To 1920x1080 (crop to fill)
ffmpeg -i input.mp4 -vf "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080" output.mp4

# Scale to width, auto height
ffmpeg -i input.mp4 -vf "scale=1280:-2" output.mp4
```

## Compress Video

```bash
# Good quality, smaller file (CRF 23 is default, lower = better quality)
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k output.mp4

# Aggressive compression for web preview
ffmpeg -i input.mp4 -c:v libx264 -crf 28 -preset fast -c:a aac -b:a 96k output.mp4

# Target file size (e.g., ~10MB for 60s video = ~1.3Mbps)
ffmpeg -i input.mp4 -c:v libx264 -b:v 1300k -c:a aac -b:a 128k output.mp4
```

## Extract Audio

```bash
# Extract to MP3
ffmpeg -i input.mp4 -vn -acodec libmp3lame -q:a 2 output.mp3

# Extract to AAC
ffmpeg -i input.mp4 -vn -acodec aac -b:a 192k output.m4a

# Extract to WAV (uncompressed)
ffmpeg -i input.mp4 -vn output.wav
```

## Convert Audio Formats

```bash
# M4A to MP3 (for ElevenLabs voice samples)
ffmpeg -i input.m4a -codec:a libmp3lame -qscale:a 2 output.mp3

# WAV to MP3
ffmpeg -i input.wav -codec:a libmp3lame -b:a 192k output.mp3

# Adjust volume
ffmpeg -i input.mp3 -filter:a "volume=1.5" output.mp3
```

## Trim/Cut Video

```bash
# Cut from timestamp to duration (recommended - reliable)
ffmpeg -i input.mp4 -ss 00:00:30 -t 00:00:15 -c:v libx264 -c:a aac output.mp4

# Cut from timestamp to timestamp
ffmpeg -i input.mp4 -ss 00:00:30 -to 00:00:45 -c:v libx264 -c:a aac output.mp4

# Stream copy (faster but may lose frames at cut points)
# Only use when source has frequent keyframes
ffmpeg -i input.mp4 -ss 00:00:30 -t 00:00:15 -c copy output.mp4
```

**Note:** Re-encoding is recommended for trimming. Stream copy (`-c copy`) can silently drop video if the seek point doesn't align with a keyframe.

## Speed Up / Slow Down

```bash
# 2x speed (video and audio)
ffmpeg -i input.mp4 -filter_complex "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2.0[a]" -map "[v]" -map "[a]" output.mp4

# 0.5x speed (slow motion)
ffmpeg -i input.mp4 -filter_complex "[0:v]setpts=2.0*PTS[v];[0:a]atempo=0.5[a]" -map "[v]" -map "[a]" output.mp4

# Video only (no audio)
ffmpeg -i input.mp4 -filter:v "setpts=0.5*PTS" -an output.mp4
```

**Calculate speed factor:**
- To fit X seconds of video into Y seconds: `speed = X / Y`
- setpts multiplier = `1 / speed` (e.g., 3x speed = setpts=0.333*PTS)
- atempo value = `speed` (e.g., 3x speed = atempo=3.0)

**Extreme speed (>2x audio):** Chain atempo filters (each limited to 0.5-2.0 range):
```bash
# 4x speed audio
-filter_complex "[0:a]atempo=2.0,atempo=2.0[a]"

# 8x speed audio
-filter_complex "[0:a]atempo=2.0,atempo=2.0,atempo=2.0[a]"
```

## Concatenate Videos

Create `list.txt` containing one `file 'clipN.mp4'` line per clip, then:

```bash
# Concatenate (same codec/resolution)
ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4

# Concatenate with re-encoding (different sources)
ffmpeg -f concat -safe 0 -i list.txt -c:v libx264 -c:a aac output.mp4
```

**Windows gotcha:** the list file must be plain ASCII/UTF-8. PowerShell's `>` redirection writes UTF-16 and breaks the concat demuxer — use `Set-Content list.txt -Encoding ascii` (or write the file with a text tool) instead of `echo ... > list.txt`.

## Add Fade In/Out

```bash
# Fade in first 1 second, fade out last 1 second (30fps video)
ffmpeg -i input.mp4 -vf "fade=t=in:st=0:d=1,fade=t=out:st=9:d=1" -c:a copy output.mp4

# Audio fade
ffmpeg -i input.mp4 -af "afade=t=in:st=0:d=1,afade=t=out:st=9:d=1" -c:v copy output.mp4
```

(`st` for the fade-out = clip duration minus fade duration.)

## Common Issues

### "Height not divisible by 2"
Add scale filter: `-vf "scale=trunc(iw/2)*2:trunc(ih/2)*2"`

### Video won't play in browser
Use: `-movflags faststart -pix_fmt yuv420p -c:v libx264`

### Audio out of sync after speed change
Use filter_complex with atempo: `-filter_complex "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2.0[a]"`

### File too large
Increase CRF (23→28) or reduce resolution

## Quality Guidelines

| Use Case | CRF | Preset | Notes |
|----------|-----|--------|-------|
| Archive/Master | 18 | slow | Best quality, large files |
| Production | 20-22 | medium | Good balance |
| Web/Preview | 23-25 | fast | Smaller files |
| Draft/Quick | 28+ | veryfast | Fast encoding |

## Validating Outputs

```bash
# Validate output file is playable (prints codec name if a video stream decodes)
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of csv=p=0 output.mp4
```

| Error | Cause | Fix |
|-------|-------|-----|
| "No such file" | Input path wrong | Check path, use quotes for spaces |
| "Invalid data" | Corrupted input | Re-download or re-record source |
| "height not divisible by 2" | Odd dimensions | Add scale filter with trunc |
| "encoder not found" | Missing codec | Install FFmpeg with full codecs |
| Output 0 bytes | Silent failure | Check full ffmpeg output for errors |

<!-- adapted from OpenMontage (.agents/skills/ffmpeg/SKILL.md) -->
