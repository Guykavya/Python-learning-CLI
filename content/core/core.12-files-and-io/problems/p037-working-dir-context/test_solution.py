import os
from pathlib import Path

import pytest

from solution import working_dir


def same(a, b):
    return Path(a).resolve() == Path(b).resolve()


@pytest.fixture
def base(tmp_path, monkeypatch):
    start = tmp_path / "start"
    start.mkdir()
    monkeypatch.chdir(start)      # restored by pytest at the end of the test
    return start


def test_changes_and_restores(base, tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    with working_dir(target):
        assert same(os.getcwd(), target), "Inside the with block the current folder must be the target."
    assert same(os.getcwd(), base), "After the with block the old folder must be back."


def test_yields_path(base, tmp_path):
    target = tmp_path / "t2"
    target.mkdir()
    with working_dir(target) as here:
        assert isinstance(here, Path), "Yield the new folder as a Path (use Path.cwd())."
        assert same(here, target), "The yielded Path is the new current folder."


def test_relative_files_land_in_target(base, tmp_path):
    target = tmp_path / "t3"
    target.mkdir()
    with working_dir(target):
        Path("note.txt").write_text("hi")
    assert (target / "note.txt").read_text() == "hi", "A relative path inside the block is relative to the target folder."
    assert not (base / "note.txt").exists(), "The file must not appear in the old folder."


def test_restores_after_error(base, tmp_path):
    target = tmp_path / "t4"
    target.mkdir()
    with pytest.raises(ValueError):
        with working_dir(target):
            raise ValueError("boom")
    assert same(os.getcwd(), base), "Restore the folder in a finally block, so an error in the body does not leave you in the wrong folder. The error must still go up."


def test_nested(base, tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()
    with working_dir(a):
        with working_dir(b):
            assert same(os.getcwd(), b), "The inner block changes to b."
        assert same(os.getcwd(), a), "Leaving the inner block returns to a, not to the start folder."
    assert same(os.getcwd(), base), "Leaving the outer block returns to the start folder."


def test_missing_folder(base, tmp_path):
    with pytest.raises(FileNotFoundError):
        with working_dir(tmp_path / "nope"):
            pass
    assert same(os.getcwd(), base), "If the folder does not exist, the current folder must stay the same."
