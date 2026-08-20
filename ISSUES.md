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

**STAGE-9 RESOLUTION (d-137, 2026-07-29):** solved for stage 9 with a one-reader-per-document contract — main agent reads only the stage-9 skill/pipeline/checkpoints/reports; clip-producer alone reads the tech skills + per-scene python slices; evaluator receives laws in its brief. The stage-9 skill and clip-producer.md were deduplicated so no rule text exists in both. Pattern is the candidate template for stage 10.

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

**M6 STATUS (d-137, 2026-07-29):** stage-9 role files delivered current: clip-producer (new, end-to-end), prompt-smith (updated d-106/d-111/d-120/d-124/d-127, now the producer's contract), clip-evaluator (new, wraps qc-critic thresholds), virality-checker (new). qc-critic remains authoritative for stage-10's watch-through — audit it at M7 kickoff.

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

## ISSUE-008 — Scene-to-scene transition naturalness: conditioning method unproven, no music/voice continuity plan

**STATUS UPDATE (2026-08-17, d-202): the VISUAL conditioning question was settled by Director order, not by A/B.** The chained-scene conditioning set is now: previous scene's last-3s tail as `video_references` slot 1 (≈ method (c), video-reference continuity) + the scene's own promoted Soul keyframe as `start_image` (d-200) + reference sheets + the picked storyboard page (keyframe-vs-page adherence is reported at every early E02 gate — the Director's ongoing check on whether the page stays attached). E01's method (b) (last-frame start) is superseded for chained scenes. The AUDIO continuity question below remains open (stage-10 sneak-in/dovetail laws d-161 partially address score; voice drift across cuts still unmeasured).

**Problem:** Stage 9's stub currently conditions each clip on (a) its own promoted start frame, (b) locked sheets/plates, (c) the picked storyboard PAGE as an `image_references` entry, (d) the speaker's locked voice sample. None of this has been tested end-to-end, and it does not yet address two separate risks the Director raised: (1) whether the *visual* cut between consecutive clips reads as one continuous scene rather than a stitched sequence of independent generations; (2) whether the *audio* — score and character voice — carries across the cut without an audible seam, since each clip is currently an independent generation with its own audio pass.

**Candidate solutions for the VISUAL continuity question — five methods to A/B before committing stage 9's conditioning contract, small-scale (~1 scene each, 3-6 clips total) at the top of M6 before any real clip work:**
- (a) *Baseline, as currently stubbed:* promoted start frame + picked page as `image_references` + prompt text carries the ending. Risk: passing a numbered, gutter-lined storyboard grid as an `image_references` entry is unproven and may bleed grid seams or the panel-number text into the generated video (the same class of failure that motivated the stage-7/8 no-text-in-frame rule, d-023) — or may simply be ignored by the model with no effect either way.
- (b) *Director proposal 1:* pass the PREVIOUS scene's actual LAST FRAME (not the current scene's own promoted start) as the new clip's `start_image`, instead of a freshly-promoted image of the new scene's opening beat. Tests whether conditioning literally on the prior clip's endpoint increases transition naturalness versus the current chain-by-reference method (which only threads the previous PICKED PAGE into the storyboard generation step, not into video generation itself).
- (c) *Director proposal 2:* pass the previous scene's rendered CLIP as a `video_references` entry (Seedance's capability, confirmed in `config/model_capabilities.yaml`, unused so far) when generating the next scene, instead of only an image reference. Tests whether motion/style continuity from an actual video reference beats any image-only method.
- (d) Page-reference test as originally scoped (isolate whether (a)'s page reference helps, hurts, or does nothing) — folds into the same small-scale comparison now that (b) and (c) are also being tested.
- (e) *No cross-scene image/video reference at all* — chained continuity carried by the prompt text and the storyboard's own state-transition law (d-047) only, as a control condition to measure against (a)-(d).

Compare on: does the cut read as one continuous scene or as two separate clips stitched together; does any method introduce a visible seam, grid artifact, or drift; does (c)'s video reference cost noticeably more or take longer than image-only methods.

**Candidate solutions for the AUDIO continuity question (music + character voice across a cut) — genuinely open, no candidate yet tested:**
- Character voice: `audio_references` (verified capability) conditions each clip's native voice generation per-clip, per speaker — but two consecutive clips are still two independent generations, so voice timbre/pacing could drift clip-to-clip even with the same reference sample. Untested whether this reads as consistent to a listener across a cut.
- Score/music continuity is entirely unaddressed by anything in stages 8-9; stage 10 (integration) is where music/SFX get composited per `pipeline.yaml`, but the current stage-10 skill is also a stub (ISSUE-005) and has no documented method for score continuity across clip boundaries (crossfade at the cut point? one continuous score track laid under all clips independently of per-clip generation? per-scene score cues stitched together?). This needs a decision before M7, not just before M6's video tests.

**Evidence:** Director request 2026-07-21, in response to the storyboard-set stage-8 completion summary raising the page-reference risk unprompted.

**Priority:** run the visual A/B (a)-(e) at the TOP of M6, before any of the 17 scenes' real clips are generated — cheap now (a handful of test clips), expensive to discover after 17 scenes are already produced under an unvalidated method. The audio question (music/voice continuity) should be scoped and decided no later than the M6→M7 boundary, since it governs stage 10's design, not just stage 9's.

**Director decision 2026-07-22 (deferred, not skipped):** proposed test scope (S14→S15 kitchen pair, 5 clips, seedance_2_0_mini/720p/5s, ~70cr) presented and costed live; Director deferred execution — **run this test after scene 4's real clips are done**, not before scene 1. Production therefore starts on the current stub's baseline method (method (a): promoted start frame + picked page as image_references, no cross-scene image/video link) for scenes 1-4, then pauses for the A/B before continuing — so scenes 1-4 may need re-conditioning (not full regen; likely just a start_image/reference swap) if the test picks a different method. Duration ceiling verified live in the same exchange: `seedance_2_0` at 15s/1080p = 135cr; `seedance_2_0_mini` at 15s/720p = 37.5cr — both accepted 15s with no downgrade, so the config's `duration_seconds: {min:4, max:15}` claim is confirmed correct for both models, not just documented.

**Budget math surfaced in the same exchange (important, unresolved):** 17 scenes / 170s total, ~10s average. One full generation pass at mini/720p ≈ 425cr; at full-model/1080p ≈ 1,530cr. Remaining budget at the time of this note: 282cr (of 1200 total; ~848 already spent through stage 8). Even the cheap model's single-pass estimate exceeds what's left once any regens are counted (pipeline allows ≤3 attempts/clip). This is a Director-facing budget decision to make explicit before scaling past the first few scenes — model choice (mini vs full), resolution, and/or a possible additional-budget conversation all bear on it.

---

## Resolved / mitigated

**ISSUE-002/003 (partial) — 2026-07-20, d-073.** Agents were hand-computing crop pixel math in ad-hoc Bash per scene (confirmed from a real transcript: `crop=672:380:0:380` typed from scratch) and stalling on unlimited `Read`s of large artifact JSONs (confirmed exact culprit: an unlimited Read of `lock_descriptors.json`). Fixed by `scripts/storyboard_qc.py split-panels` (deterministic, zero-arithmetic panel extraction via ffmpeg/ffprobe, no Pillow dependency needed) + a documented slice-extraction pattern in the new `storyboard-qc` skill. Token cost per artist run should drop (fewer/no full-page re-reads after a regen — only the changed panel needs re-checking) but this has not yet been measured against a real scene; re-verify at the next few scenes' `subagent_tokens` figures. ISSUE-002's broader question (brief-inlined slices vs full-read subagents) is still open — this only fixes the mechanical waste, not the architectural question.

---

*Maintenance: append new issues with the next number; when an issue is resolved, note the decision id and move the entry to a "Resolved" section at the bottom.*
