import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def home(tmp_path, monkeypatch):
    """A throwaway learning folder with the real syllabus and content."""
    shutil.copy(ROOT / "syllabus.yaml", tmp_path / "syllabus.yaml")
    shutil.copytree(ROOT / "content", tmp_path / "content")
    (tmp_path / "config.toml").write_text('[plan]\ndaily_minutes = 60\nfocus = ["core", "dsa"]\n')
    monkeypatch.setenv("LEARN_HOME", str(tmp_path))
    from learn import content, syllabus
    content.reload()
    syllabus.load.cache_clear()
    yield tmp_path
    content.reload()
    syllabus.load.cache_clear()
