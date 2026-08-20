# Video Generation Director — stage 9 (MAIN AGENT doc)

Turn each scene's picked storyboard into a real ≤15s clip. This stage is the pipeline's most expensive per-unit spend by far (10–140 credits/clip) — cost discipline and the regen gate matter more here than anywhere upstream.

**This file is the MAIN AGENT's operating doc (d-137).** Per-clip mechanics live in the producer's chain — `.claude/agents/clip-producer.md` → `prompt-smith.md` → `skills/tech/seedance-prompting` + `skills/tech/higgsfield-mcp` + `skills/meta/consistency-guard.md` — and are deliberately NOT duplicated here. If you are the main agent, do not read those files; if you are the producer, do not read this one.

**Consumes:** `shot_selection`, `storyboard_set`, `lock_descriptors`, `asset_manifest`, `scene_list`, `scene_direction` (all read by the PRODUCER as per-scene slices — never by the main agent).
**Produces:** `artifacts/generation_manifest.json` (producer-written, main flips final status) + `artifacts/clip_qc_report.json` (evaluator, optional).
**Gate:** per clip, Director-personal (d-114). **Resume unit:** `clip` (`clip_id` = `S{nn}[A-Z]?_C{nn}`, attempts in `generation_manifest`).

## Orchestration (Director order d-137 — the four-part split)

**Part 1 — Main agent (you).** Reads THIS skill, `pipeline.yaml`, checkpoint state, and subagent reports — nothing else. Duties:
1. Resume via `checkpoint.py next`; sequence scenes from the previous producer report's NEXT SCENE RECOMMENDATION (chain vs hinge — chained scenes generate IN ORDER, each only after its predecessor is APPROVED; parallelism only across hard-hinge groups; if a predecessor's ending drifted from its board, the successor inherits it — catch that at the predecessor's gate, not the successor's).
2. Announce the estimated cost (duration × the model's per-second rate from the last preflight; never a remembered number as final — the producer re-preflights and aborts on mismatch) and obtain the Director's explicit go BEFORE invoking the producer. Budget arithmetic surfaces to the Director; never silently downgrade or overspend (d-095/d-096 pattern). Model choice is a Director decision — log overrides as `model_selection`.
3. Invoke `clip-producer` with the brief: scene_id, attempt, `chain:<path to the predecessor's APPROVED clip mp4>` (d-202 — the producer extracts and uploads its last-3s tail) or `hinge`, params, authorized_credits, any fix_directive (the Director's exact words).
   - If the producer stalls mid-poll (its wait timers can be blocked/detached by the harness), the main agent MAY check `job_display` itself and resume the producer with the confirmed status — a status read only, never the post-processing (that stays the producer's).
4. Forward the producer's report + stills to the Director at the gate and END TURN — **REGENERATION IS DIRECTOR-GATED (d-114, BINDING):** all findings (producer's, evaluator's, yours) are recommendations; only the Director's explicit instruction after personally checking the clip authorizes a regen, and they may equally approve a flagged clip — their call outranks every threshold, is recorded, and is never re-argued. The 3-attempt ceiling bounds Director-ORDERED regens; it is not a budget you may spend. One autonomous regen cost 99cr on S04 — that is the failure mode this rule kills.
5. On the verdict: flip the manifest status (`approved`/`qc_failed`, archive → edit → validate), `log-decision` category `gate_approval`, checkpoint `--unit-done` on approval.
6. Invoke `clip-evaluator` (part 3) and/or `virality-checker` (part 4) ONLY when the Director asks — both optional, both skipped by default.

**Part 2 — `clip-producer`** (one invocation = one attempt): end-to-end generation per its own file — slices the artifacts, builds the d-127 reference map, assembles the prompt (d-124 start-frame naming + bridge; d-112 last-frame chaining vs promoted-frame hinges), preflights against authorized cost, generates, records the manifest through `generated`, extracts chain frame + stills, verifies frame-0, reports. Never regenerates, never gates, never checkpoints.

**Part 3 — `clip-evaluator`** (OPTIONAL): deep QC per its file — laws arrive in its brief (reads no scene artifacts), native-resolution verification mandatory (the zoom-before-you-accuse law — three false alarms to date, one cost 99cr; the moving clip at full resolution outranks any still), writes `clip_qc_report`, recommendation-only. When skipped, the producer's stills + the Director's viewing ARE the QC.

**Part 4 — `virality-checker`** (OPTIONAL): informational score on a completed job_id, cost-delta verified, never gates. Virality is OUT of the standard pipeline (Director ruling 2026-07-27).

**Token-economy contract (binding):** each document has ONE reader — main: this file + pipeline + checkpoints + reports; producer: its chain + per-scene slices + `config/model_capabilities.yaml`; evaluator: `qc-critic.md` + its brief. Nobody reads whole artifact JSONs (python slices only). Data flows forward in briefs and reports, never by a second reader re-opening a source. Subagents are stateless — each spawn re-reads its instruction files (no cross-invocation cache; keep them tight); within one spawn nothing is read twice.

## Director-inserted scenes (mid-production; precedents S05A/S05B d-117/d-120, S09A d-130 — MAIN AGENT protocol)

The Director may insert new scenes at any point. Scene ids take a letter suffix (`S09A`; the `[A-Z]?` schema extension covers all artifact schemas). In order:
1. **Amend `scene_list.json` AND `scene_direction.json`** — archive both to `history/`, insert full entries at the correct position (same field-completeness standard as original scenes: dialogue with delivery, continuity_notes, negative_notes, transition hints — canon from that moment), bump `total_est_seconds`, validate both.
2. **Log the insertion** as its own decision id (`--decided-by` the Director) before generating anything.
3. **No storyboard page exists** — the scene skips stage 8; the producer builds its references per d-127 from what IS attached (chain frame, character sheets, location plate); never fabricate or borrow a page.
4. **Chain/hinge decision is explicit** in the brief: chain from the neighbor's approved last frame when location/moment continue (S05B, S09A); hinge only when location breaks. State the choice at the gate.
5. Check the FOLLOWING scene still cuts correctly from the new clip's ending; flag mismatches to the Director rather than silently regenerating.
5b. **Re-author BOTH boundary hints — hints are NEIGHBOR-BOUND (d-158, the S05A seam lesson).** Scene N's `transition_out_hint` was written against its ORIGINAL next scene; after an insertion that hint still describes a cut into a scene that is no longer adjacent (S05's "dip through dark and slam" described landing on S06's reveal — applied to the new S05→S05A boundary it punched a blink into a continuous fall). At insertion time, rewrite scene N's hint for the boundary N→inserted and give the inserted scene its own hint for inserted→N+1 (both archived in scene_list). Remember N's already-generated clip ENDS with motion designed for the old neighbor — the inserted scene's opening must absorb that inherited motion (chain from N's true last frame AND continue the motion in the first beat), or the seam will show no matter what the edit does.
5c. **Quality-first neighbor regeneration (d-159):** an insertion changes the CONTEXT of both neighbors — scene N's ending and scene N+1's opening were generated for the old order. Evaluate both seams honestly and PROPOSE regenerating any neighbor clip whose motion/composition no longer serves the new order. **Cost is never a veto when quality is at stake** (Director standing order 2026-07-31): the proposal states the expected quality gain and the price; the Director decides (d-114 unchanged). Silently keeping a degraded seam to save credits is the violation, not the spend.
6. Everything else unchanged: cost announcement + go, per-clip gate (d-114), manifest recording, effects budget (producer enforces — max one impact move, never repeating a neighbor's).

## Pitfalls (main-agent scope)

- Invoking the producer before the Director's explicit go on the cost — the go covers the authorized_credits number, nothing more.
- Sequencing a chained scene before its predecessor is APPROVED — the chain input doesn't exist until then.
- Scaling to many scenes before confirming batch cost against balance — video costs 5–10x storyboard cost per unit; surface the arithmetic.
- Treating a skipped evaluator as "no QC happened" — the producer's stills + the Director's personal check are the QC of record.
- Re-arguing a Director ruling recorded at a previous gate (accepted deviations are rulings, not defects to re-fix).
- Forgetting the d-202/d-203 chaining set on a chained scene: previous clip's last-3s tail as a video reference + the scene's Soul keyframe as a STYLE reference (never start_image, d-203) + reference sheets + storyboard page. Two open Director evaluations run at E02's first chained scenes: keyframe-vs-page adherence, and start_variant none vs last_frame (`start_variant:last_frame` in the brief attaches the predecessor's last frame as start_image) — both variants Director-gated and reported side by side; the Director picks the standing method.
