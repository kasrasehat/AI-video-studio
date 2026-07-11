"""validate_artifact.py — validate one artifact JSON against its schema.

Usage:
  python scripts/validate_artifact.py <path/to/artifact.json> [--schema NAME]

Schema name is inferred from the filename stem (e.g. brief.json -> brief;
qa_review_directing.json -> qa_review via longest-prefix match). Pass --schema to override.
Exit codes: 0 valid · 1 invalid or error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import favs_lib as lib  # noqa: E402


def infer_schema_name(path: Path) -> str | None:
    stem = path.stem
    names = lib.artifact_schema_names()
    if stem in names:
        return stem
    matches = [n for n in names if stem.startswith(n + "_") or stem.startswith(n + "-")]
    if matches:
        return max(matches, key=len)
    return None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--schema", help="schema name override (see schemas/artifacts/)")
    args = parser.parse_args(argv)

    if not args.artifact.exists():
        print(f"[ERROR] file not found: {args.artifact}")
        return 1
    schema_name = args.schema or infer_schema_name(args.artifact)
    if not schema_name:
        print(f"[ERROR] cannot infer schema from {args.artifact.name!r}; pass --schema NAME")
        print(f"  known schemas: {', '.join(lib.artifact_schema_names())}")
        return 1
    try:
        instance = lib.read_json(args.artifact)
    except json.JSONDecodeError as e:
        print(f"[ERROR] not valid JSON: {e}")
        return 1
    errors = lib.validation_errors(instance, schema_name)
    if errors:
        print(f"[INVALID] {args.artifact} vs {schema_name} ({len(errors)} error(s)):")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"[VALID] {args.artifact} vs {schema_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
