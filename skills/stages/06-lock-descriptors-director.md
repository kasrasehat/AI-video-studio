# Lock Descriptors Director — stage 6

> STATUS: stub — full version lands at M3.

## IO contract (from pipeline.yaml)
- Consumes: `scene_direction`, `scene_list`, `story`.
- Produces: `artifacts/lock_descriptors.json` + `artifacts/qa_review_lock_descriptors.json`.
- QA loop: `qa-reviewer`, max 3 rounds, blocking. Gate: Director approves the descriptors.

## Shape of the full skill (M3)
Run `descriptor-extractor` subagent: every character (static face/body/age vs dynamic outfits per scene; 3–6 identity anchors usable VERBATIM in prompts; voice_spec matching role+style; forbidden_drift), every recurring object and location (anchors, lighting baseline, scene refs). QA checks: ambiguity, static/dynamic misfiling, anchor quality, every scene's characters_present resolvable, every speaker has a voice_spec. This artifact is the consistency backbone — precision here is cheaper than regens later.
