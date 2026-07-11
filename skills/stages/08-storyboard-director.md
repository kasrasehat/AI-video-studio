# Storyboard Director — stage 8

> STATUS: stub — full version lands at M5.

## IO contract (from pipeline.yaml)
- Consumes: `asset_manifest` (locked elements only), `scene_direction`, `lock_descriptors`, `scene_list`.
- Produces: `artifacts/storyboard_set.json` + `artifacts/shot_selection.json`. Gate: Director cherry-picks shots ACROSS variants (e.g. cuts 1–2 from A, 3–4 from C). Resume unit: scene×variant.
- Parallel: `storyboard-artist` subagent per variant (max 3) under Claude Code.

## Shape of the full skill (M5)
Three genuinely different approaches per scene (framing/energy/coverage — not rerolls), every frame conditioned on locked refs (`refs_used` recorded), start/end-frame candidates flagged with scene-chaining in mind (this scene's end ≈ next scene's start where the director specified continuity). Gallery → gate → shot_selection with roles (start_frame/end_frame/mid_reference) + rationale.
