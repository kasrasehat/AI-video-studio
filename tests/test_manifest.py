"""pipeline.yaml is schema-valid, internally consistent, and its references resolve."""
import json

import yaml

import favs_lib as lib

MANIFEST = lib.load_manifest()
STAGES = MANIFEST["stages"]


def test_manifest_validates_against_schema():
    errors = lib.validation_errors(MANIFEST, "pipeline_manifest")
    assert not errors, "\n".join(errors)


def test_ten_stages_in_locked_order():
    expected = ["intake", "story", "scene-division", "scene-recheck", "directing",
                "lock-descriptors", "asset-generation", "storyboard", "video-generation", "integration"]
    assert [s["name"] for s in STAGES] == expected


def test_orchestration_skill_exists():
    assert (lib.ROOT / MANIFEST["orchestration"]["skill"]).exists()


def test_every_stage_skill_exists():
    missing = [s["skill"] for s in STAGES if not (lib.ROOT / s["skill"]).exists()]
    assert not missing, f"missing stage skills: {missing}"


def test_every_produced_artifact_has_a_schema():
    known = set(lib.artifact_schema_names())
    for stage in STAGES:
        unknown = set(stage["produces"]) - known
        assert not unknown, f"stage {stage['name']} produces unknown artifacts: {unknown}"


def test_required_inputs_are_produced_upstream():
    produced = set()
    for stage in STAGES:
        missing = set(stage["required_artifacts_in"]) - produced
        assert not missing, f"stage {stage['name']} requires {missing} which no earlier stage produces"
        produced |= set(stage["produces"])


def test_gates_match_locked_design():
    gated = {s["name"] for s in STAGES if s["human_approval_default"]}
    assert gated == {"intake", "story", "scene-recheck", "directing", "lock-descriptors",
                     "asset-generation", "storyboard", "video-generation", "integration"}
    ungated = {s["name"] for s in STAGES if not s["human_approval_default"]}
    assert ungated == {"scene-division"}


def test_mandatory_qa_loops_present():
    by_name = {s["name"]: s for s in STAGES}
    for stage_name in ["story", "directing", "lock-descriptors", "integration"]:
        assert "qa_loop" in by_name[stage_name], f"{stage_name} must declare its QA loop"
        assert by_name[stage_name]["qa_loop"]["blocking"] is True
    # d-137 + d-114: stage 9's loop is the OPTIONAL, NON-blocking clip-evaluator —
    # nothing loops autonomously; every regen is Director-authorized after they check the clip.
    vg = by_name["video-generation"]["qa_loop"]
    assert vg["agent"] == "clip-evaluator"
    assert vg["blocking"] is False
    assert vg["optional"] is True


def test_model_capabilities_config():
    with open(lib.ROOT / "config" / "model_capabilities.yaml", encoding="utf-8") as f:
        caps = yaml.safe_load(f)
    policy = caps["policy"]
    assert policy["no_external_tts_lipsync"] is True
    required = policy["dialogue_scene_requires"]
    assert set(required) == {"native_voice", "quoted_dialogue_lipsync", "reference_audio"}
    # At least one video model must satisfy the dialogue policy, else dialogue scenes are unroutable.
    satisfying = [name for name, m in caps["video_models"].items()
                  if all(m.get(cap) is True for cap in required)]
    assert satisfying, "no video model satisfies the dialogue policy"
    assert "seedance_2_0" in satisfying
    # Every video model must fit the <=15s scene unit contract.
    for name, m in caps["video_models"].items():
        dur = m["duration_seconds"]
        max_s = dur["max"] if "max" in dur else max(dur["options"])
        assert 0 < max_s <= 15, f"{name} duration exceeds the 15s scene unit"


def test_delivery_presets_config():
    with open(lib.ROOT / "config" / "delivery_presets.yaml", encoding="utf-8") as f:
        presets = yaml.safe_load(f)["presets"]
    for pid, p in presets.items():
        for key in ["resolution", "aspect", "fps", "video_codec", "audio_codec", "target_lufs", "captions"]:
            assert key in p, f"preset {pid} missing {key}"
        assert p["captions"] in ("none", "srt", "burn")
    # The fixture's deliverables must reference real presets.
    fixture = json.loads((lib.ROOT / "tests" / "fixtures" / "sample-project" / "artifacts" / "edit_decisions.json").read_text(encoding="utf-8"))
    for d in fixture["deliverables"]:
        assert d["preset_id"] in presets, f"fixture references unknown preset {d['preset_id']}"


def test_skill_index_references_exist():
    """Every path-like reference in skills/INDEX.md tables must exist on disk."""
    index = (lib.ROOT / "skills" / "INDEX.md").read_text(encoding="utf-8")
    bases = [lib.ROOT / "skills" / "stages", lib.ROOT / "skills" / "meta", lib.ROOT / "skills" / "tech",
             lib.ROOT / ".claude" / "agents"]  # d-137: INDEX also routes the stage-9 role chain
    for line in index.splitlines():
        if line.startswith("| `") and ".md" in line:
            rel = line.split("`")[1]
            if not any((base / rel).exists() for base in bases):
                raise AssertionError(f"INDEX.md references missing skill file: {rel}")
