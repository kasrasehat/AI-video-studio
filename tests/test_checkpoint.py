"""checkpoint.py behavior: init layout, gate enforcement, archiving, progression, resume, decisions."""
import json
import shutil

import checkpoint as cp
import favs_lib as lib

SLUG = "sample-project"  # matches fixture project_id so artifact validation stays warning-free


def run(argv) -> int:
    return cp.main(argv)


def init_project(tmp_projects) -> None:
    assert run(["init", SLUG, "--title", "The Lantern Fox", "--dry-run"]) == 0


def copy_fixture(fixtures_dir, name: str) -> str:
    src = fixtures_dir / "artifacts" / f"{name}.json"
    dst = lib.project_dir(SLUG) / "artifacts" / f"{name}.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, dst)
    return f"artifacts/{name}.json"


def test_init_creates_layout(tmp_projects):
    init_project(tmp_projects)
    pdir = lib.project_dir(SLUG)
    for sub in ["artifacts", "history", "gallery", "renders"]:
        assert (pdir / sub).is_dir()
    for sub in cp.ASSET_SUBDIRS:
        assert (pdir / "assets" / sub).is_dir()
    project = json.loads((pdir / "project.json").read_text(encoding="utf-8"))
    assert project["dry_run"] is True and project["pipeline"] == "film"
    assert json.loads((pdir / "decision_log.json").read_text(encoding="utf-8"))["decisions"] == []


def test_init_twice_fails(tmp_projects):
    init_project(tmp_projects)
    assert run(["init", SLUG]) == 1


def test_gate_violation_blocks_unapproved_completion(tmp_projects, fixtures_dir):
    init_project(tmp_projects)
    copy_fixture(fixtures_dir, "brief")
    # intake is gated: completed without --approved must exit 2 and write nothing.
    assert run(["write", SLUG, "intake", "--status", "completed",
                "--artifact", "brief=artifacts/brief.json"]) == 2
    assert lib.read_checkpoint(SLUG, "intake") is None


def test_gated_flow_and_archiving(tmp_projects, fixtures_dir):
    init_project(tmp_projects)
    rel = copy_fixture(fixtures_dir, "brief")
    assert run(["write", SLUG, "intake", "--status", "in_progress"]) == 0
    assert run(["write", SLUG, "intake", "--status", "awaiting_human", "--artifact", f"brief={rel}"]) == 0
    assert run(["write", SLUG, "intake", "--status", "completed", "--approved"]) == 0

    final = lib.read_checkpoint(SLUG, "intake")
    assert final["status"] == "completed" and final["human_approved"] is True
    assert final["artifacts"]["brief"] == rel          # carried forward from the awaiting_human write
    assert len(final["artifact_hashes"]["brief"]) == 64
    archives = list((lib.project_dir(SLUG) / "history").glob("checkpoint_intake_*.json"))
    assert len(archives) == 2  # in_progress and awaiting_human versions both archived


def test_invalid_artifact_rejected(tmp_projects, fixtures_dir):
    init_project(tmp_projects)
    rel = copy_fixture(fixtures_dir, "brief")
    broken = json.loads((lib.project_dir(SLUG) / rel).read_text(encoding="utf-8"))
    del broken["logline"]
    (lib.project_dir(SLUG) / rel).write_text(json.dumps(broken), encoding="utf-8")
    assert run(["write", SLUG, "intake", "--status", "awaiting_human", "--artifact", f"brief={rel}"]) == 1
    assert lib.read_checkpoint(SLUG, "intake") is None


def test_unknown_stage_and_artifact_rejected(tmp_projects, fixtures_dir):
    init_project(tmp_projects)
    assert run(["write", SLUG, "post-credits", "--status", "in_progress"]) == 1
    rel = copy_fixture(fixtures_dir, "brief")
    assert run(["write", SLUG, "intake", "--status", "in_progress", "--artifact", f"mystery={rel}"]) == 1


def test_next_progression(tmp_projects, fixtures_dir, capsys):
    init_project(tmp_projects)
    run(["next", SLUG])
    assert "next stage: intake [not_started]" in capsys.readouterr().out
    rel = copy_fixture(fixtures_dir, "brief")
    run(["write", SLUG, "intake", "--status", "awaiting_human", "--artifact", f"brief={rel}"])
    run(["next", SLUG])
    out = capsys.readouterr().out
    assert "next stage: intake [awaiting_human]" in out and "do NOT proceed" in out
    run(["write", SLUG, "intake", "--status", "completed", "--approved"])
    run(["next", SLUG])
    assert "next stage: story" in capsys.readouterr().out


def complete_stages_through_scene_recheck(fixtures_dir):
    """Drive the pipeline to the point where directing is the next stage."""
    brief = copy_fixture(fixtures_dir, "brief")
    story = copy_fixture(fixtures_dir, "story")
    scene_list = copy_fixture(fixtures_dir, "scene_list")
    assert run(["write", SLUG, "intake", "--status", "completed", "--approved",
                "--artifact", f"brief={brief}"]) == 0
    assert run(["write", SLUG, "story", "--status", "completed", "--approved",
                "--artifact", f"story={story}"]) == 0
    assert run(["write", SLUG, "scene-division", "--status", "completed",
                "--artifact", f"scene_list={scene_list}"]) == 0   # ungated stage
    assert run(["write", SLUG, "scene-recheck", "--status", "completed", "--approved",
                "--artifact", f"scene_list={scene_list}"]) == 0


def test_partial_progress_roundtrip(tmp_projects, fixtures_dir, capsys):
    init_project(tmp_projects)
    complete_stages_through_scene_recheck(fixtures_dir)
    capsys.readouterr()  # drain setup output
    assert run(["write", SLUG, "directing", "--status", "in_progress",
                "--unit-done", "S01", "--total-units", "2"]) == 0
    assert run(["write", SLUG, "directing", "--status", "in_progress", "--unit-done", "S02"]) == 0
    assert run(["write", SLUG, "directing", "--status", "in_progress", "--unit-done", "S02"]) == 0  # idempotent
    saved = lib.read_checkpoint(SLUG, "directing")
    pp = saved["metadata"]["partial_progress"]
    assert pp["completed_unit_ids"] == ["S01", "S02"]
    assert pp["unit"] == "scene"        # defaulted from the stage's resume_unit
    assert pp["total_units"] == 2
    run(["next", SLUG])
    out = capsys.readouterr().out
    assert "next stage: directing [in_progress]" in out
    assert "2/2 scene" in out
    assert "S01, S02" in out


def test_decision_log_append_and_revision(tmp_projects):
    init_project(tmp_projects)
    base = ["log-decision", SLUG, "--stage", "video-generation",
            "--category", "model_selection", "--subject", "Project default video model"]
    assert run(base + ["--selected", "seedance-2.0", "--reason", "dialogue policy",
                       "--option", "seedance-2.0::native voice", "--option", "kling-2.5::no voice",
                       "--decided-by", "user"]) == 0
    assert run(base + ["--selected", "seedance-2.0-fast", "--reason", "draft pass first",
                       "--decided-by", "user"]) == 0
    log = json.loads((lib.project_dir(SLUG) / "decision_log.json").read_text(encoding="utf-8"))
    assert [d["decision_id"] for d in log["decisions"]] == ["d-001", "d-002"]
    assert not lib.validation_errors(log, "decision_log")
    # Latest entry per (category, subject) is current.
    current = {}
    for d in log["decisions"]:
        current[(d["category"], d["subject"])] = d["selected"]
    assert current[("model_selection", "Project default video model")] == "seedance-2.0-fast"


def test_status_table(tmp_projects, fixtures_dir, capsys):
    init_project(tmp_projects)
    rel = copy_fixture(fixtures_dir, "brief")
    run(["write", SLUG, "intake", "--status", "awaiting_human", "--artifact", f"brief={rel}"])
    run(["status", SLUG])
    out = capsys.readouterr().out
    assert "[DRY-RUN]" in out
    assert "intake" in out and "awaiting_human" in out
    assert "integration" in out and "not_started" in out
