# Story Director — stage 2

Run the writers' room: Writer drafts → Refiner re-reads and repairs → the Director (user) accepts or gives notes, looping until accepted.

**Consumes:** `brief`. **Produces:** `artifacts/story.json` (schema `story`).
**QA loop:** `refiner`, min 1 round, blocking. **Gate:** Director accept/comment loop.

## Process

1. **Dispatch `writer`** with the project dir + path to `artifacts/brief.json`. If `artifacts/trend_kit.json` exists with a non-empty selection (optional stage 1b, d-192), include its `integration.story_plan` verbatim in the writer's brief — the weave follows THAT plan, and the subtlety contract governs (story must fully work for a trend-blind viewer; QA treats a bolted-on trend as CRITICAL). It returns a draft story JSON (`revision.round=1, changed_by=writer`) + one paragraph of intent.
2. **Dispatch `refiner`** with the brief path + the draft (write the draft to `artifacts/story.json` first so the refiner reads the real file). This round is MANDATORY even if the draft looks perfect — fresh eyes are the point. It returns the revised story (`round=2, changed_by=refiner`, honest `change_notes`) + `remaining_risks`.
3. **Sanity-check before the gate** (you, not the agents):
   - `estimated_runtime_seconds` within the brief's duration target ±10%; beats sum to it.
   - Every beat has a real `emotional_note`; the emotional arc actually progresses.
   - Cast size filmable (≤4 named characters for a 2–3 min film; be skeptical above that).
   - `content_boundaries` respected; language matches the brief.
   - **Causal chain audit (d-191)** — run the checks in the section below; a story failing them goes back to the refiner BEFORE the gate.
   - **Conversation density (d-191)** — every beat where 2+ characters are present carries a real multi-turn exchange (each speaker ≥2 turns) or names its silence as a choice; flag any stretch of consecutive beats carried by single lines or narration-with-visuals.
   - Schema-valid (`validate_artifact.py artifacts/story.json`). Fix or re-dispatch on failure.
4. **Gate.** Present: title + genre, the synopsis, the beat map (one line per beat: summary → emotion → seconds), the full story text, WHAT THE REFINER CHANGED (from change_notes — the Director should see the room's work), and `remaining_risks`. Options: accept / give notes / abort.
5. **On Director notes:** route them through `refiner` (notes verbatim in the prompt; `changed_by` stays `refiner`, round increments, change_notes describe the response to each note). Archive the prior `story.json` to `history/` first. Re-run step 3, re-gate. Log each revision round as a decision (`--decided-by user`, their note as the reason). Cap: `max_revisions_per_stage` (3) — then present the impasse honestly.

## Judgment calls that are yours (not the agents')

- If writer and refiner disagree structurally (refiner's remaining_risks contradicts the draft's core), surface BOTH views at the gate rather than silently picking.
- If the Director's note would break the brief (e.g. doubles the runtime), say so before executing — propose honoring the note AND amending the brief, their call. An amended brief = re-approve the brief (stage 1 checkpoint superseded) before continuing.

## Pitfalls

- Skipping the refiner because the draft "reads well" — the mandate exists for the failure you can't see.
- Presenting only a summary at the gate: the Director must be able to read the ACTUAL story text.
- Letting change_notes say "improved flow" — they must name concrete changes or the audit trail is theater.

## The room's laws (CANONICAL — d-194)

The three law sections below are the SINGLE home of these rules. The `writer` and `refiner` read them directly (their role files point here and restate nothing); the qa-reviewer detects against them. Any future amendment happens HERE and only here.

## Causal clarity law (d-191, audience feedback — BINDING)

Episode 1 shipped with a comprehension bug: real viewers could not say HOW the heroes ended up inside Grandma — the mechanism (shrunk duo on the cookie → cookie dunked in lemonade → Grandma drinks) was distributed across cuts and inference. Audiences do not infer load-bearing plot mechanics; they experience a gap and disengage. Three rules:

1. **Every world/location entry and exit is a MECHANISM BEAT** — its own beat (or an explicitly named portion of one) that shows cause → effect on screen, in order, uninterrupted: the audience must SEE the thing that moves the heroes from world A to world B, not deduce it. "How did they get there?" must be answerable by pointing at the screen.
2. **The naive retell test:** after drafting, retell the whole story using ONLY what a first-time viewer sees and hears — no author knowledge. Every location change, every character appearance, every plot-critical object must survive the retell. Any step that needs "well, obviously..." is a defect; name it and fix it in the story, not in a caption.
3. **Mechanism beats are never trimmed for time.** When runtime pressure comes, cut a joke, a lingering shot, a b-plot — never the 3 seconds that make the plot legible. A confused viewer is a lost subscriber; no gag out-earns comprehension.

The qa-reviewer runs the retell test independently (comprehension audit); it reaching QA is already a miss — the writers' room owns clarity first.

## Conversation density law (d-191, audience feedback — BINDING)

The Director's standing order: dialogue like professional animation. Films in this genre are carried by talk — characterful, overlapping, reactive. Concretely:

- **Default texture = exchange, not statement.** Wherever two characters share a beat, write a real back-and-forth (≥2 turns EACH, short lines) that plays through the action. One character saying one line while things happen around them is a storyboard note, not a scene.
- **Reactions are lines too.** The listener answers — with words, an interjection, a comeback. Alternating monologues are not conversation.
- **Talk reveals, never narrates.** Every line carries want/worry/joke/character; exposition is smuggled inside attitude ("Rule one of introductions: name first"), never delivered as information.
- **Silence stays legal but must be BOUGHT:** a named dramatic reason recorded in the beat's `emotional_note` (awe, held breath, suspense) — same standard as d-111, now with the density bar raised: a story averaging under ~2 exchanges per dialogue-capable beat is flat by definition and goes back to the room.

## First-3-seconds law (d-173, virality — BINDING for future productions)

The story's OPENING BEAT must put the production's most arresting visual on screen within the first 3 seconds of the film — a cold open, never an establishing preamble. YouTube's promotion decision is dominated by the opening retention cliff; a slow first shot taxes every later view. When writing beats, B01 is authored hook-first: name the exact image that stops a scroll and put it before any setup. (Existing productions are NOT regenerated for this — it applies from the next film onward.)
