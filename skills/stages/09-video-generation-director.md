# Video Generation Director — stage 9

> STATUS: stub — full version lands at M6.

## IO contract (from pipeline.yaml)
- Consumes: `shot_selection`, `storyboard_set`, `lock_descriptors`, `asset_manifest`, `scene_list`, `scene_direction`.
- Produces: `artifacts/generation_manifest.json` + `artifacts/clip_qc_report.json`.
- QA loop: `qc-critic` per clip (identity/continuity/lipsync), regen ≤3 attempts with fix_directive. Gate: Director approves per scene batch. Resume unit: clip.

## Shape of the full skill (M6)
Director picks the project model from `config/model_capabilities.yaml` (log model_selection). HARD RULE: dialogue scenes only on models satisfying `policy.dialogue_scene_requires`. Per clip (`prompt-smith` subagent): 5-aspect prompt (Subject/Motion/Scene/Spatial/Camera), 200–400 words for Seedance, identity anchors VERBATIM, dialogue as quoted lines, references threaded (locked sheets/plates ≤9 images, start/end frames from shot_selection, locked voice `reference_audio` for every speaker). Generate via higgsfield MCP → `qc-critic` scores → regen with fix_directive or pass → batch gate per scene.
