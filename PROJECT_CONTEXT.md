# PROJECT_CONTEXT — architecture map

One-page orientation for agents and humans. The binding rules live in [`AGENT_GUIDE.md`](AGENT_GUIDE.md).

## Layers

```
┌─ Harness entry points ──────────────────────────────────────────────┐
│ CLAUDE.md · CURSOR.md · CODEX.md · AGENTS.md → all point to AGENT_GUIDE.md
├─ Contract ──────────────────────────────────────────────────────────┤
│ AGENT_GUIDE.md (rules) · pipeline.yaml (10-stage manifest)          │
├─ Intelligence (markdown, harness-agnostic) ─────────────────────────┤
│ skills/stages/  — one director skill per pipeline stage             │
│ skills/meta/    — checkpoint protocol, QA reviewer, consistency     │
│ skills/tech/    — provider skills (higgsfield, seedance, elevenlabs…)│
│ .claude/agents/ — subagent roles (parallel under Claude Code)       │
├─ Validation & persistence (all the Python there is) ────────────────┤
│ scripts/checkpoint.py · validate_artifact.py · review_gallery.py    │
│ scripts/assemble.py · sync_skills.py                                │
│ schemas/ — JSON Schema for every artifact + checkpoint + manifest   │
├─ Configuration ─────────────────────────────────────────────────────┤
│ config/model_capabilities.yaml · config/delivery_presets.yaml       │
│ .mcp.json · .env (from .env.template)                               │
└─ State (gitignored) ────────────────────────────────────────────────┘
  projects/<slug>/ — artifacts, checkpoints, assets, gallery, renders
```

## The 10 stages → artifacts

| # | Stage | Canonical artifact(s) |
|---|-------|----------------------|
| 1 | intake | `brief` |
| 2 | story | `story` |
| 3 | scene-division | `scene_list` |
| 4 | scene-recheck | `scene_list` (final) |
| 5 | directing | `scene_direction` (+ `qa_review`) |
| 6 | lock-descriptors | `lock_descriptors` (+ `qa_review`) |
| 7 | asset-generation | `asset_manifest` |
| 8 | storyboard | `storyboard_set`, `shot_selection` |
| 9 | video-generation | `generation_manifest`, `clip_qc_report` |
| 10 | integration | `edit_decisions`, `render_report` |

Cross-cutting: `decision_log` (append-only), `checkpoint_<stage>.json` per stage.

## Key conventions

- **Windows host.** Paths inside artifacts are relative to the project directory (`projects/<slug>/`), forward slashes.
- **IDs:** scenes `S01…`, characters `CH01…`, locations `LOC01…`, objects `OBJ01…`, clips `S01_C01` (scene, attempt-independent), frames `S01_A_F01` (scene, variant, frame), decisions `d-001…`.
- **Schema versioning:** every artifact carries `version` (schema const) — bump the const + schema together.
- **AGPL note:** OpenMontage (reference project) is AGPL; skills here are adapted patterns, and this repo is private/internal.

## Build status

Scaffolded milestone-by-milestone (M1 governance → M8 end-to-end). Stage skills marked `STATUS: stub` are not yet implemented — check `skills/INDEX.md`.
