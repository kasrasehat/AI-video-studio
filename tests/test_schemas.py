"""Every schema parses as Draft 2020-12; every fixture validates; broken fixtures fail."""
import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

import favs_lib as lib

ALL_SCHEMAS = sorted(lib.SCHEMAS_DIR.rglob("*.schema.json"))
FIXTURE_ARTIFACTS = sorted((Path(__file__).parent / "fixtures" / "sample-project" / "artifacts").glob("*.json"))


def test_schemas_exist():
    assert len(ALL_SCHEMAS) == 22, f"expected 22 schemas, found {len(ALL_SCHEMAS)}"
    assert len(list(lib.ARTIFACT_SCHEMAS_DIR.glob("*.schema.json"))) == 20


@pytest.mark.parametrize("schema_path", ALL_SCHEMAS, ids=lambda p: p.stem)
def test_schema_is_valid_draft_2020_12(schema_path):
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)


def test_every_artifact_schema_has_a_fixture():
    fixture_names = {p.stem for p in FIXTURE_ARTIFACTS}
    schema_names = set(lib.artifact_schema_names())
    assert schema_names == fixture_names, (
        f"missing fixtures: {schema_names - fixture_names}; orphan fixtures: {fixture_names - schema_names}"
    )


@pytest.mark.parametrize("fixture_path", FIXTURE_ARTIFACTS, ids=lambda p: p.stem)
def test_fixture_validates(fixture_path):
    instance = json.loads(fixture_path.read_text(encoding="utf-8"))
    errors = lib.validation_errors(instance, fixture_path.stem)
    assert not errors, "\n".join(errors)


@pytest.mark.parametrize("fixture_path", FIXTURE_ARTIFACTS, ids=lambda p: p.stem)
def test_mutated_fixture_fails(fixture_path):
    """Dropping any top-level required field must be caught."""
    schema = json.loads(lib.schema_path(fixture_path.stem).read_text(encoding="utf-8"))
    instance = json.loads(fixture_path.read_text(encoding="utf-8"))
    for required_key in schema.get("required", []):
        mutated = copy.deepcopy(instance)
        mutated.pop(required_key, None)
        errors = lib.validation_errors(mutated, fixture_path.stem)
        assert errors, f"removing required {required_key!r} was not caught"


def test_qa_review_critical_requires_proposed_fix():
    instance = json.loads((Path(__file__).parent / "fixtures" / "sample-project" / "artifacts" / "qa_review.json").read_text(encoding="utf-8"))
    bad = copy.deepcopy(instance)
    bad["findings"][0].pop("proposed_fix")  # findings[0] is the critical one
    assert lib.validation_errors(bad, "qa_review"), "critical finding without proposed_fix must fail"


def test_clip_qc_regen_requires_fix_directive():
    path = Path(__file__).parent / "fixtures" / "sample-project" / "artifacts" / "clip_qc_report.json"
    instance = json.loads(path.read_text(encoding="utf-8"))
    bad = copy.deepcopy(instance)
    assert bad["clips"][0]["verdict"] == "regen"
    bad["clips"][0].pop("fix_directive")
    assert lib.validation_errors(bad, "clip_qc_report"), "regen verdict without fix_directive must fail"


def test_scene_duration_cap_enforced():
    path = Path(__file__).parent / "fixtures" / "sample-project" / "artifacts" / "scene_list.json"
    instance = json.loads(path.read_text(encoding="utf-8"))
    bad = copy.deepcopy(instance)
    bad["scenes"][0]["est_duration_seconds"] = 31  # over the 30s absolute cap (Seedance 2.5, d-204)
    assert lib.validation_errors(bad, "scene_list"), "scene over 30s must fail"
    ok = copy.deepcopy(instance)
    ok["scenes"][0]["est_duration_seconds"] = 22  # legal only for a 2.5-assigned scene (stage 3 enforces per-model)
    assert not lib.validation_errors(ok, "scene_list"), "a <=30s scene must pass the schema (d-204)"


def test_reference_images_capped_at_nine():
    path = Path(__file__).parent / "fixtures" / "sample-project" / "artifacts" / "generation_manifest.json"
    instance = json.loads(path.read_text(encoding="utf-8"))
    bad = copy.deepcopy(instance)
    bad["clips"][0]["references"]["images"] = [f"img{i}.png" for i in range(10)]
    assert lib.validation_errors(bad, "generation_manifest"), ">9 reference images must fail"
