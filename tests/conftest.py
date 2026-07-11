import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

FIXTURES = ROOT / "tests" / "fixtures" / "sample-project"


@pytest.fixture
def repo_root() -> Path:
    return ROOT


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES


@pytest.fixture
def tmp_projects(tmp_path, monkeypatch) -> Path:
    """Point the checkpoint CLI at a temp projects dir."""
    monkeypatch.setenv("FAVS_PROJECTS_DIR", str(tmp_path))
    return tmp_path
