---
description: Safely compact context mid-production — land in-flight work, checkpoint truthfully, commit, verify, then emit a filled /compact prompt for the Director to run
argument-hint: [slug]
---

Compact the context window SAFELY mid-production. Compaction loses everything not written down — this command makes the write-down mechanical: **nothing in-flight, everything on disk, one copyable /compact command.** `/compact` itself is user-side — you prepare; the Director fires.

If `$ARGUMENTS` is empty, infer the active production slug from the current session (the one with an open checkpoint / most recent activity); if ambiguous, ask.

## PRE-COMPACT (do ALL of this before emitting the prompt — skip nothing)

1. **Land in-flight work.** Any generated-but-unrecorded clip goes into `generation_manifest.json` NOW (archive → append → validate). Any un-QC'd download gets at least a one-line status. A call that isn't recorded didn't happen.
2. **Log unlogged decisions.** Sweep the conversation since the last `log-decision` for Director rulings not yet in the log — method changes, picks, accepted deviations. Log each at its own id, `--decided-by user` where the Director spoke.
3. **Checkpoint truthfully.** `checkpoint.py write <slug> <stage> --status <TRUE status>` with a `--note` that names: the exact resume point (next scene/clip), the last APPROVED clip and its job_id, and any open Director question. Never upgrade a status to look finished.
4. **Commit the repo.** All skills/schemas/scripts changes, descriptive message. Remember `projects/` is gitignored by design — artifacts persist as files + their `history/` archives, not in git, so step 1's validation is their only safety net.
5. **Verify, mechanically:** `sync_skills.py --check` clean · `pytest -q` green · `validate_artifact.py` on every artifact touched this session · `checkpoint.py status <slug>` table matches reality.
6. **Update memory** (the auto-memory file for this project): current milestone position, resume point, any new standing rules by decision id.

## THE COMPACT PROMPT (fill live from disk, never from memory — emit as ONE copyable `/compact <text>` block)

Structure, in order — every section filled from disk at compaction time:

- **SOURCE-OF-TRUTH PRECEDENCE:** (1) files under `projects/<slug>/` (artifacts/, assets/, history/, decision_log.json); (2) `checkpoint.py next`/`status`; (3) decision_log through its latest id; (4) approved/locked artifact fields; (5) the summary itself; (6) recollection. Report conflicts, never silently prefer memory.
- **PROJECT IDENTITY:** repo root, venv path, git HEAD, slug, film title, mode, brief essentials.
- **PIPELINE POSITION:** per-stage status table; the resume unit ("next: generate SNN, chained from SNN-1's approved clip, last frame at <path>").
- **STANDING RULES IN FORCE, BY DECISION ID** — the section a fresh model most needs. Currently: d-114 (NO regeneration without explicit Director permission after they personally check the clip; QC is report-only; per-clip gate), d-112 (last-frame chaining via `scripts/extract_last_frame.py` → media_upload; promoted frames only at hard hinges), d-113/d-116 (resolution history), d-106 (@-mention every reference; numbering = medias order), d-120 (named @asset handles; impact-move vocabulary, max one per scene, never repeat a neighbor's), d-118 (emotional beats earn a directed camera drift), d-098/d-108/d-119 (derived state sheets fix reference conflicts — bare-wrist, both goggles-down sheets with their media_ids), d-099 (negatives unreliable — positive phrasing; camera negatives the exception), metaphors literalize (planets, cathedral), zoom-before-you-accuse (S02/S04 false alarms), per-beat state restatement (goggles/props at 0s/3s/6s/…), get_cost doesn't validate combos, end_image steers-not-locks (S05B), preset interceptions → retry with declined_preset_id.
- **CLIP LEDGER:** per scene — approved clip file, job_id, attempts/costs, disclosed-and-accepted deviations (these are Director rulings, not defects to "fix").
- **ASSET REGISTRY:** locked sheet/voice/plate media_ids PLUS derived sheets and uploaded chain-frame media_ids still in use.
- **COSTS:** manifest total, last known balance, per-second rates in effect.
- **FAILURES / DO-NOT-REPEAT:** this production's burned lessons, one line each.
- **POST-COMPACT BOOTSTRAP** (the prompt's closing section — instructions to the fresh model): (1) read `AGENT_GUIDE.md`; (2) `checkpoint.py next` + `status` and TRUST them over the summary; (3) read the manifest's last entries + decision log tail; (4) verify the last approved clip and its extracted last frame exist on disk; (5) report state + any discrepancy to the Director; (6) **generate NOTHING and regenerate NOTHING without the Director's explicit go (d-114)** — the first post-compaction act is a report, never a spend.

## POST-COMPACT (fresh session, after the Director runs the command)

Execute the bootstrap exactly as written in the summary. The bar: the fresh model should resume mid-scene without repeating work, re-arguing settled rulings, or spending a credit before the Director says go.

## Pitfalls

- Emitting the prompt with stale values instead of re-reading disk (balances, ids and statuses drift within a session).
- Compacting with an unrecorded generation in flight — the clip survives on disk but its provenance dies with the context.
- Writing the checkpoint note as aspiration ("stage nearly done") instead of fact ("S07 not started; S06 awaiting Director listen").
- Forgetting that the Director runs /compact themselves — end by handing them the block, not by waiting.
