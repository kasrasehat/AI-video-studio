# Intake Director — stage 1

> STATUS: stub — full version lands at M3.

## IO contract (from pipeline.yaml)
- Consumes: the user's story idea (conversation).
- Produces: `artifacts/brief.json` (schema `brief`). Gate: Director confirms the brief.

## Shape of the full skill (M3)
Conversational Q&A, ONE question at a time, in the user's language: story idea (capture verbatim) → audience → duration → language → style → tone → genre → platform/aspect → content boundaries → music direction → references. Never assume; unresolved items go to `open_questions`. Then draft the brief, present it, gate.
