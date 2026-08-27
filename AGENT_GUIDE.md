# AGENT_GUIDE — full-ai-video-system

The complete operating contract for any AI agent working in this repository. Every rule here is binding regardless of which harness (Claude Code, Cursor, Codex) you run under.

**What this system does:** turns a user's story idea into a coherent multi-minute film with on-screen speaking characters, assembled from AI-generated clips — ≤15s on Seedance 2.0 (the default) or ≤30s on Seedance 2.5 (parallel flow, Director-ordered only, d-204) — via Higgsfield MCP, plus Kling/Veo for non-dialogue scenes. The user is the Director: every creative stage ends at a human approval gate.

---

## Rule Zero — reading order

Before doing pipeline work, read in this order. Never skip a layer.

1. **This file** — the contract.
2. **`pipeline.yaml`** — the 12-stage manifest: stage order, artifacts, gates, QA loops, parallelism.
3. **The stage-director skill** for the current stage (`skills/stages/NN-<stage>-director.md`) — how to execute the stage.
4. **The tech skill** for any generation tool you are about to use (`skills/tech/<name>/SKILL.md`) — provider-specific prompting and API contracts. The intelligence is in the skills; do not improvise prompts or parameters.

`skills/INDEX.md` is the routing table when you are unsure which skill applies.

## Harness matrix

| Capability | Claude Code (Fable) | Cursor / Codex / other |
|---|---|---|
| Entry point | `CLAUDE.md` → this file | `CURSOR.md` / `CODEX.md` / `AGENTS.md` → this file |
| Subagents (`.claude/agents/*.md`) | Run via the Agent/Task tool; parallel allowed (e.g. 3 storyboard variants concurrently). Stage 9 runs the d-137 four-part split (main agent + clip-producer + optional clip-evaluator/virality-checker) — sequential within chain groups (d-112), per-clip Director gate (d-114) | **Not available.** Read the same agent file as a role instruction and perform it yourself, sequentially, one role at a time |
| Commands (`/new-film`, `/new-series`, `/new-episode`, `/resume`, `/status`, `/gallery`) | `.claude/commands/` | `.cursor/commands/` mirrors; else follow the command file manually |
| MCP (higgsfield) | `.mcp.json` | Use your harness's MCP support; if absent, stop and tell the user which call you needed |

Artifacts and gates are identical across harnesses — only wall-clock parallelism differs. When acting out a subagent role sequentially, still honor its input/output contract exactly.

## The pipeline at a glance

```
1 intake → [1b trend-scan — OPTIONAL] → 2 story → 3 scene-division → 4 scene-recheck →
5 directing → 6 lock-descriptors → 7 asset-generation → 8 storyboard →
9 video-generation → 10 integration → 11 publishing → [12 character-spotlight — OPTIONAL] →
[13 dub-pass — OPTIONAL, repeatable]
```

`pipeline.yaml` is the single source of truth for what each stage requires, produces, and gates. Do not restructure the pipeline; the stage list is a user decision. Stage 12 is `optional: true`: it is OFFERED to the Director after publishing, never assumed — the Director may run it (per-video gates) or decline it (checkpoint status `skipped`, which requires `--approved` and never blocks pipeline completion).

**Films vs series:** `/new-film` produces a standalone production at `projects/<slug>/`. A SERIES is one directory — `projects/_series/<series_id>/` — holding the bible (`series_bible.json`, schema `series_bible`), series-level channel assets/delivery, and each episode as an ordinary full-pipeline production under `episodes/<slug>/` (the CLI resolves bare slugs from both layouts). `/new-series` founds the bible (or adopts a finished film as episode 1); `/new-episode` starts the next episode — inheriting format via delta-only intake and importing canon assets pre-locked at stages 6–7, per `skills/meta/series-continuity.md` (BINDING).

## Gate protocol (BINDING)

Stages with `human_approval_default: true` in `pipeline.yaml` gate on the Director. The manifest value is binding — there is no "this case is different."

1. Finish the stage's work (including any mandatory QA loop) and write its artifacts to `projects/<slug>/artifacts/`.
2. Write the checkpoint with `status="awaiting_human"` via `scripts/checkpoint.py`.
3. Present a concise summary: what was produced, key decisions, QA findings, cost so far, and exactly what the Director should review (file paths / gallery link).
4. **END YOUR TURN.** Doing any further pipeline work in the same response is a gate violation.
5. On the Director's reply:
   - **Approve** → re-write the checkpoint `--status completed --approved`, proceed to the next stage.
   - **Feedback** → return to the stage-director skill, revise, re-run QA, re-checkpoint `awaiting_human`. Loop until approved. Never carry unapproved changes forward.
   - **Abort** → write `--status failed --note <reason>`, stop.

`scripts/checkpoint.py` refuses (`GATE VIOLATION`, exit 2) to write `completed` on a gated stage without `--approved`. Do not work around it.

## State, checkpoints & the CLI

Each production lives in `projects/<slug>/`:

```
projects/<slug>/
├── project.json          # identity: title, pipeline, created_at, dry_run
├── decision_log.json     # append-only; latest entry per (category, subject) is current
├── artifacts/            # canonical artifacts (<name>.json) + checkpoint_<stage>.json
├── history/              # superseded checkpoints/artifacts — never deleted
├── assets/               # characters/ environments/ voices/ storyboards/ clips/ music/ sfx/
├── gallery/              # generated HTML review galleries
└── renders/              # final deliverables
```

CLI (`python scripts/checkpoint.py …` — on this machine always use the repo venv interpreter, `.venv/Scripts/python`; the system Python is broken for jsonschema):

| Command | Purpose |
|---|---|
| `init <slug> [--title T] [--dry-run]` | Create the workspace |
| `write <slug> <stage> --status S [--approved] [--artifact name=path]… [--unit-done ID]… [--note TEXT]` | Write/refresh a checkpoint; validates every referenced artifact against its schema; archives the superseded checkpoint to `history/` |
| `read <slug> [stage]` | Print checkpoint(s) |
| `next <slug>` | Report the next stage to work on + resume info |
| `log-decision <slug> --stage S --category C --subject SUBJ --selected SEL --reason R [--option "label::reason"]…` | Append to the decision log |
| `status <slug>` | One-line-per-stage progress table |

Rules:
- **Enter a stage → immediately write `--status in_progress`.** Long stages (assets, storyboards, clips) record each finished unit with `--unit-done <id>` so a crash resumes at the exact unit, not from scratch.
- **Resume protocol:** on `/resume` or any restart, run `next <slug>` first and trust it over your memory of the conversation.
- **Decisions:** every meaningful choice (model pick, variant pick, shot cherry-pick, gate approval, regen) goes in the decision log at the moment it is made.

## Consistency contract (BINDING)

This is how 25–80 independent stochastic clips become one film. Full details: `skills/meta/consistency-guard.md`.

1. **Locked assets only.** After stage 7, every generation call may reference only files whose `asset_manifest` element is `locked: true` (the Director's picks). Never regenerate or "improve" a locked asset without a Director-approved unlock.
2. **Identity anchors verbatim.** Every image/video prompt that includes a character MUST embed that character's `identity_anchors` (3–6 attributes from `lock_descriptors`) word-for-word, plus the scene's outfit from `dynamic_features`.
3. **Reference threading.** Every clip generation passes: locked character sheet views + locked environment plate (≤9 images total), the storyboard start/end frames, and — for every speaking character — their locked voice sample as `reference_audio`.
4. **Voice lock = Seedance-native.** Dialogue is delivered as quoted lines inside the video prompt; the character's locked voice reference sample conditions the native voice. There is NO external TTS/lipsync path. Dialogue scenes may only run on models whose `config/model_capabilities.yaml` entry satisfies `policy.dialogue_scene_requires`.
5. **Continuity fields are law.** `scene_list.continuity_notes`, `time_of_day`, and `outfit_by_scene` override anything a prompt would otherwise improvise.

## Cost announcements

Before any paid generation call, state the estimated cost (from `config/model_capabilities.yaml` unit costs × quantity) in your message and record actuals in the producing artifact's `cost_usd` fields. Batch estimates are fine ("12 storyboard frames ≈ $X"). The Director decides tradeoffs — never silently downgrade quality to save money, and never silently overspend.

## Dry-run mode

If `project.json` has `dry_run: true`: every generation call is replaced by copying a placeholder from `tests/fixtures/sample-project/` into the target asset path, all `cost_usd` are 0, and MCP must not be touched. Everything else — artifacts, schemas, QA loops, gates, checkpoints — behaves exactly as in a real production. Dry-run exists to prove the governance layer at $0.

## Where do I look

| Question | Answer |
|---|---|
| Stage order, gates, QA loops | `pipeline.yaml` |
| How to run the current stage | `skills/stages/NN-<stage>-director.md` |
| Artifact shape | `schemas/artifacts/<name>.schema.json` |
| Gate/checkpoint mechanics | `skills/meta/checkpoint-protocol.md` + `scripts/checkpoint.py --help` |
| QA severities & review rules | `skills/meta/qa-reviewer.md` |
| Identity/consistency rules | `skills/meta/consistency-guard.md` |
| Series bible / cross-episode canon | `skills/meta/series-continuity.md` |
| Which model can do what | `config/model_capabilities.yaml` |
| Export formats | `config/delivery_presets.yaml` |
| Provider prompting | `skills/tech/<provider>/SKILL.md` |
| Architecture map | `PROJECT_CONTEXT.md` |
