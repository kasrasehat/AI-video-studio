# ISSUES — architecture & process backlog

Deferred problems noted during production. Each entry: the problem, the evidence, candidate solutions. Nothing here is implemented without a Director decision. (Opened 2026-07-19 at the Director's order during M5 stage-8; production continues under the current d-061 architecture meanwhile.)

---

## ISSUE-001 — Stage-8 knowledge is duplicated across four surfaces (sync hazard)

**Problem:** The storyboard method currently lives in FOUR places that must agree: `skills/stages/08-storyboard-director.md` (stage method), `skills/tech/storyboard-design/SKILL.md` (frame craft — grid table, chaining, state-transition and variant rules restated), `.claude/agents/storyboard-artist.md` (role contract restating the same rules), and each per-scene brief in `projects/<slug>/reports/`. Every new Director rule requires 3–4 coordinated edits; any missed file silently drifts.

**Evidence:** `storyboard-artist.md` stayed on the retired per-frame/3-variant method until the Director's audit caught it (d-059) — rules d-043/d-044/d-047/d-054/d-057 had each been applied to the skills but not the role file. Same class of drift can recur for every stage's role files (writer, refiner, director, prompt-smith, qc-critic…).

**Candidate solutions:**
- (a) EP proposal (2026-07-19, deferred): single canonical rulebook per stage — merge the tech skill into the stage skill, shrink the role file to a thin contract (identity + read order + output format, zero restated rules), briefs data-only. One edit per rule change.
- (b) Director's direction (preferred candidate, quoted): "storyboard director calls related subagent. subagent reads all related files, skills, guidance, data created previously like scene-direction and …" — keep full-read subagents; then de-duplication must happen by DELETING overlapping content so the files the subagent reads never disagree (role file and brief must carry no rules at all).
- Both variants agree on the core fix: **rules must exist in exactly one file**; the disagreement is only about who reads what. Decide at the next architecture window (post-M5 or before M6).

## ISSUE-002 — Double-read token cost (EP and every artist read the same material)

**Problem:** The EP reads skills + artifacts to orchestrate; each artist subagent then re-reads the same skills and the same large artifact JSONs per scene. Token cost scales as ~2×(files) per scene × 2 variants, and most of it is redundant.

**Evidence:** S07 artists consumed ~143k and ~173k tokens each, dominated by file reading; image credits were unaffected (7 cr/page) but context cost and latency roughly doubled vs inline.

**Candidate solutions:** (a) briefs carry verbatim EP-extracted slices of the scene's entries so artists read only brief + rulebook; (b) keep full-read subagents (Director's lean, ISSUE-001b) and accept token cost as the price of independence/accuracy; (c) split canonical artifacts into per-scene files so a full read is naturally small. Note (a) trades a little independence for cost; (c) preserves disk-authority with small reads but changes artifact layout + schemas.

## ISSUE-003 — Subagents stall on whole-file reads of large JSON artifacts

**Problem:** Both S07 artists stalled (600s stream-watchdog, "no progress") while Reading `scene_list.json` / `lock_descriptors.json` whole, and had to be resumed manually.

**Evidence:** Task failures on 2026-07-19 for both artist agents at exactly the artifact-reading step; both recovered immediately when resumed with instructions to extract entries via `.venv/Scripts/python -c "import json; …"` slices instead of full Reads.

**Candidate solutions:** (a) bake the slice-extraction pattern into the artist protocol (cheap, done informally via resume messages — not yet codified anywhere); (b) per-scene artifact files (see ISSUE-002c); (c) treat as harness-transient and just document the resume procedure. Until decided, every artist brief should carry the slice-extraction commands.

## ISSUE-004 — cost bookkeeping: `cost_usd` fields carry CREDITS, and no credit→USD anchor

**Problem:** Schema field names (`cost_usd`, `--cost` "USD") predate the credits audit; all production records store Higgsfield credits in USD-named fields, documented only via metadata notes. The credit→USD conversion has never been verified (transactions/plan page), so real spend in currency is unknown.

**Evidence:** asset_manifest metadata note (stage 7); storyboard_set metadata note; S07 artist B explicitly flagged the ambiguity and booked 0.0 with credits in prose (EP normalized to credits-in-field per production convention).

**Candidate solutions:** (a) schema v1.1 rename to `cost_credits` + migration of existing artifacts; (b) keep field names, promote the metadata note into the schemas' field descriptions; plus a one-time `transactions` audit to establish the credit→USD anchor for reporting.

## ISSUE-005 — Role-file freshness debt for the remaining pipeline stages

**Problem:** All nine `.claude/agents/*.md` role files were written at M2 against the original method designs. As stage methods evolve at runtime (like stage 8 did), the not-yet-used role files (prompt-smith, qc-critic, director, etc.) will be stale by the time their stages run — the storyboard-artist case proves the pattern.

**Evidence:** d-059 (storyboard-artist rewritten v2 only after the Director noticed); stages 9–10 skills are still stubs whose completion at M6/M7 will change what prompt-smith/qc-critic must do.

**Candidate solution:** when each stage's skill is completed (M6: 09 + prompt-smith + qc-critic; M7: 10), rewrite its role files in the same pass and adopt the ISSUE-001 principle (whatever variant is chosen) so the role file cannot drift again. Add a checklist item to the milestone kickoff: "audit role files touched by this stage."

## ISSUE-006 — Image-model compliance failures are the dominant regen cause (not prompts)

**Problem:** Most QC failures this stage were the model ignoring explicit prompt law, not missing/wrong prompt content: goggles rendered UP against explicit DOWN clauses (S06-B, S07-A attempt 1), duplicated characters (S04-B attempt 1, S07-A attempt 1 panel 16), spurious wrist props (S07-B), prop teleports (S04-B panel 5/7), text label typos at stage 7. Each costs a d-057 regen or a disclosed defect.

**Evidence:** decision log d-017, d-023, d-027, d-035, d-038, d-049, d-051, d-053, d-058, d-062.

**Candidate solutions:** (a) promotion-pass discipline (already planned): picked panels get re-rendered individually where laws are easier to enforce on a single composition; (b) collect a per-model "failure pattern → counter-phrase" appendix in the rulebook (some already exist: spelling guard, map orientation pin, identity law block); (c) evaluate nano_banana_pro or soul_2 for character-heavy panels at promotion time; (d) accept as stochastic floor and budget for it (current d-057 approach).

**Partial mitigation shipped 2026-07-20 (d-073):** `scripts/storyboard_qc.py` + `skills/tech/storyboard-qc/SKILL.md` give artists a mechanical `diff` check (camera-lock verification via an amplified pixel-diff triptych) instead of eyeballing two panels — this directly targets taxonomy class D (camera-continuity breaks), which caused d-070 and d-072. Does not address class H (regen not fixing its own named target) — that remains open, candidate (d) above.

## ISSUE-007 — Direction-level spatial/story-logic contradictions pass through every review layer

**Problem:** Stage 5 produced an internally unsatisfiable S14 direction — the comet's source (Rosa's sneeze) was hidden from frame with no stated reason, AND the geometry was impossible (source placed off frame-left, target pitcher pinned frame-left by LOC06, yet the blocking demanded a "left-to-right sail ACROSS the kitchen"). It then survived FOUR review layers: the stage-5 directing QA loop approved it; stage-6 lock QA didn't test trajectories; both stage-8 artists silently violated a different half of the contradiction instead of reporting it (A kept the crossing and landed the comet back at its origin; B reversed the comet and broke the S13 motion-match); EP verification judged each page against the direction's text rather than reconstructing its geometry. Only the Director caught it — after a full 28-credit boarding round.

**Evidence:** d-082 (direction amendment), d-083 (successful re-board proving the amended direction satisfiable), round-1 S14 pages in `history/superseded/`.

**Mitigation shipped 2026-07-20 (d-084)** — the lesson baked into every layer that missed it:
- `skills/stages/05-directing-director.md`: binding "spatial sanity audit" before QA dispatch (trajectory consistency, causal visibility, cross-boundary motion match) + a pitfalls entry.
- `skills/meta/qa-reviewer.md`: mandatory "trajectory audit" section — reviewers must DRAW each scene's stage diagram, not read motion prose; impossible trajectories and sourceless entrances are CRITICAL.
- `.claude/agents/qa-reviewer.md`: same audit added to the directing hunting grounds.
- `.claude/agents/director.md`: craft rule 9 — directors draw their own stage before returning; hidden causes require a stated reason.
- `skills/stages/08-storyboard-director.md` + `.claude/agents/storyboard-artist.md`: HALT-and-escalate rule — an artist who finds contradictory constraints stops free of charge instead of boarding a broken brief.

**Residual risk:** these are instructions, not mechanical enforcement. A scripted geometry linter over `scene_direction.json` (parse frame-left/right placements + trajectory verbs, assert endpoint/direction consistency) is the candidate hardening if the class recurs.

---

## Resolved / mitigated

**ISSUE-002/003 (partial) — 2026-07-20, d-073.** Agents were hand-computing crop pixel math in ad-hoc Bash per scene (confirmed from a real transcript: `crop=672:380:0:380` typed from scratch) and stalling on unlimited `Read`s of large artifact JSONs (confirmed exact culprit: an unlimited Read of `lock_descriptors.json`). Fixed by `scripts/storyboard_qc.py split-panels` (deterministic, zero-arithmetic panel extraction via ffmpeg/ffprobe, no Pillow dependency needed) + a documented slice-extraction pattern in the new `storyboard-qc` skill. Token cost per artist run should drop (fewer/no full-page re-reads after a regen — only the changed panel needs re-checking) but this has not yet been measured against a real scene; re-verify at the next few scenes' `subagent_tokens` figures. ISSUE-002's broader question (brief-inlined slices vs full-read subagents) is still open — this only fixes the mechanical waste, not the architectural question.

---

*Maintenance: append new issues with the next number; when an issue is resolved, note the decision id and move the entry to a "Resolved" section at the bottom.*
