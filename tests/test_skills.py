"""Skill and harness-overlay integrity: frontmatter, naming, sync parity, command mirrors."""
from pathlib import Path

import pytest
import yaml

import favs_lib as lib
import sync_skills

TECH_DIR = lib.ROOT / "skills" / "tech"
AGENTS_DIR = lib.ROOT / ".claude" / "agents"

EXPECTED_AGENTS = {
    "writer", "refiner", "scene-splitter", "director", "qa-reviewer",
    "descriptor-extractor", "storyboard-artist", "prompt-smith", "qc-critic",
    "thumbnail-artist", "youtube-strategist",
}
EXPECTED_COMMANDS = {"new-film.md", "resume.md", "status.md"}


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path} missing frontmatter"
    block = text.split("---\n", 2)[1]
    data = yaml.safe_load(block)
    assert isinstance(data, dict), f"{path} frontmatter is not a mapping"
    return data


def tech_skill_files():
    if not TECH_DIR.exists():
        return []
    return sorted(TECH_DIR.glob("*/SKILL.md"))


@pytest.mark.parametrize("skill_md", tech_skill_files(), ids=lambda p: p.parent.name)
def test_tech_skill_frontmatter(skill_md):
    fm = parse_frontmatter(skill_md)
    assert fm.get("name") == skill_md.parent.name, f"{skill_md}: frontmatter name != directory name"
    assert isinstance(fm.get("description"), str) and len(fm["description"]) > 20


def test_sync_parity():
    problems = sync_skills.out_of_sync()
    assert not problems, "run: python scripts/sync_skills.py\n" + "\n".join(problems)


def test_agents_present_and_well_formed():
    found = {p.stem for p in AGENTS_DIR.glob("*.md")}
    assert found == EXPECTED_AGENTS, f"missing: {EXPECTED_AGENTS - found}; unexpected: {found - EXPECTED_AGENTS}"
    for p in AGENTS_DIR.glob("*.md"):
        fm = parse_frontmatter(p)
        assert fm.get("name") == p.stem, f"{p}: frontmatter name != file stem"
        assert isinstance(fm.get("description"), str) and len(fm["description"]) > 30


def test_manifest_agent_references_exist():
    """Every qa_loop.agent and parallel.claude_subagent in pipeline.yaml is a defined agent (or 'refiner')."""
    manifest = lib.load_manifest()
    agents = {p.stem for p in AGENTS_DIR.glob("*.md")}
    for stage in manifest["stages"]:
        qa = stage.get("qa_loop")
        if qa:
            assert qa["agent"] in agents, f"stage {stage['name']} qa_loop agent {qa['agent']!r} undefined"
        par = stage.get("parallel")
        if par:
            assert par["claude_subagent"] in agents, f"stage {stage['name']} parallel agent undefined"


def test_command_mirrors():
    for base in [lib.ROOT / ".claude" / "commands", lib.ROOT / ".cursor" / "commands", lib.ROOT / ".codex" / "prompts"]:
        found = {p.name for p in base.glob("*.md")} - {"README.md"}
        assert EXPECTED_COMMANDS <= found, f"{base} missing {EXPECTED_COMMANDS - found}"
    assert (lib.ROOT / ".cursor" / "rules" / "film-system.mdc").exists()


def test_capability_matrix_skill_pointers_resolve():
    import yaml as _yaml
    caps = _yaml.safe_load((lib.ROOT / "config" / "model_capabilities.yaml").read_text(encoding="utf-8"))
    names = {p.parent.name for p in tech_skill_files()}
    for section in ["video_models", "image_models", "voice_models"]:
        for model_id, entry in caps.get(section, {}).items():
            skill = entry.get("skill")
            if skill:
                assert skill in names, f"{section}.{model_id} points at missing skill {skill!r}"
