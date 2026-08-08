"""Shared helpers for full-ai-video-system scripts.

Repo layout assumptions: this file lives in <root>/scripts/; schemas in <root>/schemas/;
the pipeline manifest at <root>/pipeline.yaml; productions under <root>/projects/
(overridable via env FAVS_PROJECTS_DIR — used by tests).
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = ROOT / "schemas"
ARTIFACT_SCHEMAS_DIR = SCHEMAS_DIR / "artifacts"
MANIFEST_PATH = ROOT / "pipeline.yaml"

CHECKPOINT_STATUSES = ("in_progress", "awaiting_human", "completed", "failed", "skipped")


class GateViolation(Exception):
    """Raised when a gated stage would be completed without human approval."""


class ValidationFailure(Exception):
    """Raised when an instance fails schema validation. .errors is a list of strings."""

    def __init__(self, message: str, errors: list[str]):
        super().__init__(message)
        self.errors = errors


def projects_dir() -> Path:
    override = os.environ.get("FAVS_PROJECTS_DIR")
    return Path(override) if override else ROOT / "projects"


def project_dir(slug: str) -> Path:
    return projects_dir() / slug


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def load_manifest() -> dict:
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def stage_names(manifest: dict | None = None) -> list[str]:
    manifest = manifest or load_manifest()
    return [s["name"] for s in manifest["stages"]]


def get_stage(name: str, manifest: dict | None = None) -> dict:
    manifest = manifest or load_manifest()
    for stage in manifest["stages"]:
        if stage["name"] == name:
            return stage
    raise KeyError(f"unknown stage: {name!r} (stages: {', '.join(stage_names(manifest))})")


def schema_path(name: str) -> Path:
    """Resolve a schema by name: artifacts first, then top-level (checkpoint, pipeline_manifest)."""
    candidate = ARTIFACT_SCHEMAS_DIR / f"{name}.schema.json"
    if candidate.exists():
        return candidate
    candidate = SCHEMAS_DIR / f"{name}.schema.json"
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"no schema named {name!r} under {SCHEMAS_DIR}")


def artifact_schema_names() -> list[str]:
    return sorted(p.name.replace(".schema.json", "") for p in ARTIFACT_SCHEMAS_DIR.glob("*.schema.json"))


def validation_errors(instance, schema_name: str) -> list[str]:
    schema = read_json(schema_path(schema_name))
    validator = Draft202012Validator(schema)
    errors = []
    for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path)):
        where = "/".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{where}: {err.message}")
    return errors


def validate_or_raise(instance, schema_name: str, label: str = "") -> None:
    errors = validation_errors(instance, schema_name)
    if errors:
        raise ValidationFailure(
            f"{label or schema_name} failed validation against {schema_name} ({len(errors)} error(s))",
            errors,
        )


def checkpoint_path(slug: str, stage: str) -> Path:
    return project_dir(slug) / "artifacts" / f"checkpoint_{stage}.json"


def read_checkpoint(slug: str, stage: str) -> dict | None:
    path = checkpoint_path(slug, stage)
    return read_json(path) if path.exists() else None


def archive_file(slug: str, path: Path) -> Path:
    """Copy a file into the project's history/ with a timestamp suffix. Returns the archive path."""
    history = project_dir(slug) / "history"
    history.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    target = history / f"{path.stem}_{stamp}{path.suffix}"
    target.write_bytes(path.read_bytes())
    return target
