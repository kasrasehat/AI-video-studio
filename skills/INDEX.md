# Skill Index

Routing table for every skill in this repo. Read order: AGENT_GUIDE.md → pipeline.yaml → stage skill → tech skill (see Rule Zero).

## Stage directors (`skills/stages/`)

| Skill | Stage | Status |
|---|---|---|
| `executive-producer.md` | Orchestrates all 12 stages, resume, budget | **ready** |
| `01-intake-director.md` | 1 intake — conversational Q&A → brief | **ready** |
| `01b-trend-scan-director.md` | 1b trend-scan (OPTIONAL) — live social trends → Director picks → subtle integration plan | **ready** |
| `02-story-director.md` | 2 story — writer → refiner → Director loop | **ready** |
| `03-scene-division-director.md` | 3 scene-division — ≤15s units | **ready** |
| `04-scene-recheck-director.md` | 4 scene-recheck — dedupe/continuity | **ready** |
| `05-directing-director.md` | 5 directing — per-scene direction + QA loop | **ready** |
| `06-lock-descriptors-director.md` | 6 lock-descriptors — consistency backbone + QA loop | **ready** |
| `07-asset-generation-director.md` | 7 asset-generation — variants → Director locks | **ready** |
| `08-storyboard-director.md` | 8 storyboard — 3 variants/scene, cherry-pick | **ready** |
| `09-video-generation-director.md` | 9 video-generation — MAIN-AGENT doc: orchestration, per-clip Director gate (d-114), d-137 four-part split | **ready** |
| `10-integration-director.md` | 10 integration — assembly, sound, delivery | **ready** |
| `11-publishing-director.md` | 11 publishing — thumbnail, trailer, metadata, delivery tree | **ready** |
| `12-character-spotlight-director.md` | 12 character-spotlight (OPTIONAL) — SJinn talking characters + b-roll | **ready** |
| `13-dub-pass-director.md` | 13 dub-pass (OPTIONAL, repeatable) — per-language dubs as YouTube audio tracks (d-195/d-196) | **ready** |

## Meta (`skills/meta/`)

| Skill | Purpose | Status |
|---|---|---|
| `checkpoint-protocol.md` | Gates, checkpoints, resume, revisions — BINDING | **ready** |
| `qa-reviewer.md` | Severity-graded review protocol for QA loops — BINDING | **ready** |
| `consistency-guard.md` | Identity anchors, ref threading, chaining, drift checklist — BINDING | **ready** |
| `series-continuity.md` | Series bible, cross-episode canon import/promotion, delta intake — BINDING | **ready** |
| `taste-direction.md` | Taste profile: design read, dials, audience adaptation | **ready** |

## Tech (`skills/tech/` — canonical; mirrored to `.claude/skills/` by `scripts/sync_skills.py`)

| Skill | Purpose | Status |
|---|---|---|
| `higgsfield-mcp/SKILL.md` | The generation gateway: tools, media-id flow, cost preflight, verified model quick-ref | **ready** (audited 2026-07-11) |
| `seedance-prompting/SKILL.md` | Seedance 2.0 prompt contract, identity+voice lock, anti-drift ladder | **ready** |
| `character-sheets/SKILL.md` | 3-view chained character sheets, variants, self-QC | **ready** |
| `storyboard-design/SKILL.md` | Static-snapshot frames, variation taxonomy, 3-variant discipline | **ready** |
| `image-editor/SKILL.md` | Interactive image editing: elicit-first protocol, nano_banana_pro default, text-safety boundary | **ready** |
| `storyboard-qc/SKILL.md` | Mechanical stage-8 self-QC: panel-split + camera-lock diff tooling, defect taxonomy, exact MCP call shapes | **ready** |
| `elevenlabs/SKILL.md` | TTS + voice design for character voice samples (voice-design API: pull live docs at M4) | **ready** |
| `sjinn/SKILL.md` | SJinn MCP — stage-12 spotlight backend (Seedance via public URLs, balance-delta cost law) | **ready** |
| `heygen/SKILL.md` | HeyGen MCP (SUPERSEDED by sjinn, d-182 — kept for reference) | superseded |
| `music/SKILL.md` | Score generation (stage 10) | **ready** |
| `sound-effects/SKILL.md` | SFX generation (stage 10) | **ready** |
| `ffmpeg/SKILL.md` | Probing, conversion, concat, fades | **ready** |
| `video-edit/SKILL.md` | Trim/concat/resize/overlay recipes | **ready** |
| `video-understand/SKILL.md` | Frame sampling + local transcription (clip-evaluator/qc-critic's eyes) | **ready** |

## Stage-9 role chain (d-137 — read by SUBAGENTS, not the main agent)

| Role file (`.claude/agents/`) | Part | Reads |
|---|---|---|
| `clip-producer.md` | 2 — end-to-end clip generation (one invocation = one attempt) | seedance-prompting, higgsfield-mcp, prompt-smith, consistency-guard, per-scene slices, model_capabilities |
| `prompt-smith.md` | prompt-assembly contract consumed BY clip-producer (not invoked standalone in the d-137 flow) | — |
| `clip-evaluator.md` | 3 — OPTIONAL deep QC, report-only (d-114) | qc-critic.md + the brief's LAWS block |
| `virality-checker.md` | 4 — OPTIONAL, informational, out-of-pipeline | — |
| `ai-video-gen/SKILL.md` | Cross-model prompting deltas (Kling/Veo/Wan/…) | **ready** |
| `flux-bfl/SKILL.md` | FLUX prompting + BFL API (optional) | **ready** |
