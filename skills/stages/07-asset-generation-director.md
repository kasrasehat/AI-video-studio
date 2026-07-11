# Asset Generation Director — stage 7

> STATUS: stub — full version lands at M4.

## IO contract (from pipeline.yaml)
- Consumes: `lock_descriptors`.
- Produces: `artifacts/asset_manifest.json`. Gate: Director PICKS one variant per element → `locked: true`. Resume unit: element.

## Shape of the full skill (M4)
Per character: 2 sheet variants, each multi-view (front → three-quarter/profile chained i2i from the front view — see `skills/tech/character-sheets`), anchors verbatim in prompts. Per location: 2 environment plates. Per speaking character: 2 voice samples auditioning voice_spec (neutral + emotional line — `skills/tech/elevenlabs`). Build the compare gallery (`python scripts/review_gallery.py <slug> assets`), gate, then mark picks locked + log variant_selection decisions.
