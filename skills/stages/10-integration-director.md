# Integration Director — stage 10

> STATUS: stub — full version lands at M7.

## IO contract (from pipeline.yaml)
- Consumes: `generation_manifest`, `clip_qc_report`, `scene_direction`, `scene_list`, `brief`.
- Produces: `artifacts/edit_decisions.json` + `artifacts/render_report.json`.
- QA loop: `qc-critic` watch-through of the assembled cut, max 2 rounds. Gate: Director approves the final cut. Resume unit: deliverable preset.

## Shape of the full skill (M7)
Build the timeline from approved clips in scene order; transitions come FROM `scene_direction.scenes[].transition_out` (never uniform crossfades). Generate music to `brief.music_direction` + SFX where the director specified sound (`skills/tech/music`, `sound-effects`); mix with sidechain ducking under dialogue to target LUFS. Captions per brief language. Assemble via `python scripts/assemble.py <slug>` per preset in `config/delivery_presets.yaml`; ffprobe-verify each output into `render_report`; run the watch-through QC; gate; render/copy final deliverables.
