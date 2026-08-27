# Consistency Guard

The cross-stage identity contract — how 25–80 independently-generated clips stay one film. AGENT_GUIDE.md states the five rules; this skill is the working detail. Applies to stages 6–10 and to every QA pass.

## 1. Authoring identity anchors (stage 6)

An anchor is a 2–7 word visual fact an image model renders reliably and a QC critic can verify frame-by-frame.

| Bad (unpromptable) | Good (promptable) | Why |
|---|---|---|
| kind, weary eyes | large dark-brown eyes | render-checkable |
| a memorable red coat | knee-length crimson duffle coat with wooden toggles | survives the two-character test |
| young | 10 years old, child proportions | models age-drift without numbers |
| distinctive scar | thin white scar through left eyebrow | side matters — QC needs to check a side |

Rules: 3–6 per character; together they must uniquely identify the character (two-character test each anchor, uniqueness test the set); at least one facial, one hair, and one permanent mark/body-geometry anchor where available; never emotions, personality, or relations. Clothing remains dynamic and rides separately as the scene outfit. Animation may use a Director-approved iconic default costume phrase as a design anchor, but live-action/hybrid identity anchors describe the person, not replaceable wardrobe.

## 2. Reference threading (what conditions what)

| Generation | Must condition on | Prompt must contain |
|---|---|---|
| Character sheet view 2/3 | that variant's FRONT view | "same character as reference, exact same appearance and outfit" |
| Environment plate | (text + location anchors) | location identity_anchors verbatim |
| Storyboard frame | locked sheet views (facing-matched) + locked plate | all present characters' anchors + scene outfit + direction framing |
| Clip | start/end frames + 2–3 locked sheet views per character + plate (≤9 images) + locked voice per speaker (audio_references) | medium-routed prompt profile + anchors verbatim + exact quoted dialogue; live action keeps surrounding appearance text minimal |
| Regen (any) | SAME references as the failed attempt unless the fix_directive changes them | fix_directive applied FIRST |

Locked assets only — a generation referencing an unlocked variant is invalid regardless of how good it looks.

## 3. Scene chaining (stages 8–10)

Where scene N's `transition_out` is `cut`-on-continuity or `match_cut`: N's end frame and N+1's start frame are designed as a PAIR — same 180° axis, compatible composition, light continuous unless time jumped. Chain check at storyboard QA: lay final selected frames in sequence and read them as a silent comic — any spatial jump the transition doesn't justify is a critical.

## 4. Drift checklist (qc-critic, per clip and per assembled cut)

Face structure · hair length+color+style · outfit category+primary color · marks (mole/scar side!) · character height ratios · palette vs global grade · prop presence+hand · screen direction vs axis · location fixtures · time-of-day light. Check each present character against their LOCKED SHEET side-by-side, not against memory, and explicitly against their `forbidden_drift` list.

## 5. forbidden_drift → prompt constraints (stages 8–9)

Every present character's `forbidden_drift` entries remain mandatory QC targets, but their prompt form follows the approved medium:

- **Live action/hybrid (`seedance-clean`):** translate each risk into one desired visible state in `POSITIVE LOCKS` (for example `shoulder-length black hair retains the same cut`, `facial age and bone structure match @image1`, `the coat remains knee-length crimson wool`). Never paste a negative list into the prompt.
- **Animation (`seedance-prompting`):** follow that skill's empirically tested anti-drift ladder and positive-rewrite policy.

In both profiles, the locked reference remains primary and each critical identity fact is stated once clearly rather than repeated as competing prose.

## Escalation rule

Two consecutive regens failing on the SAME anchor = stop generating; the problem is upstream (weak anchor, bad sheet, or contradictory direction). Name the suspected artifact and take it to the Director — burning credits on attempt #3 with unchanged inputs is the one move this skill forbids.
