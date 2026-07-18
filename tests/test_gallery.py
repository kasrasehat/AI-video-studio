"""review_gallery.py renders a self-contained HTML compare page from fixture manifests."""
from pathlib import Path

import review_gallery


def test_gallery_from_fixture_asset_manifest(monkeypatch):
    fixtures_root = Path(__file__).parent / "fixtures"
    monkeypatch.setenv("FAVS_PROJECTS_DIR", str(fixtures_root))
    assert review_gallery.main(["sample-project"]) == 0
    out = fixtures_root / "sample-project" / "gallery" / "asset_manifest.html"
    assert out.exists()
    page = out.read_text(encoding="utf-8")
    assert "CH01_sheet" in page and "LOCKED" in page          # locked element badged
    assert "LOC01_plate" in page and "pick pending" in page   # unlocked element badged
    assert "SELECTED" in page                                  # selected variant highlighted
    assert "<audio" in page or "missing:" in page              # voice sample rendered or marked missing
    assert "http://" not in page and "https://" not in page    # fully self-contained


def test_gallery_storyboard_source(monkeypatch):
    fixtures_root = Path(__file__).parent / "fixtures"
    monkeypatch.setenv("FAVS_PROJECTS_DIR", str(fixtures_root))
    assert review_gallery.main(["sample-project", "--source", "storyboard_set"]) == 0
    page = (fixtures_root / "sample-project" / "gallery" / "storyboard_set.html").read_text(encoding="utf-8")
    assert "S01" in page and "Board A" in page and "Board B" in page
