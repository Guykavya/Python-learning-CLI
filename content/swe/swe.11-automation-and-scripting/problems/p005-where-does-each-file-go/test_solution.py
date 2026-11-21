from pathlib import Path

import pytest

from solution import category_for, unique_destination


@pytest.mark.parametrize("name, folder", [
    ("holiday.JPG", "images"), ("logo.png", "images"), ("invoice.PDF", "documents"),
    ("sales.csv", "data"), ("song.Mp3", "audio"), ("backup.tar.gz", "archives"),
])
def test_known_types_ignoring_case(name, folder):
    assert category_for(name) == folder, f"{name} belongs in {folder}: look up the LAST suffix, lower-cased."


@pytest.mark.parametrize("name", ["README", "script.py", ".bashrc", "photo.jpg.part"])
def test_unknown_types_are_other(name):
    assert category_for(name) == "other", f"{name!r} is not in the table (or has no suffix): 'other'."


def test_accepts_a_path():
    assert category_for(Path("x") / "a.PNG") == "images", "category_for must accept a Path as well as a str."


def test_free_destination_is_returned_unchanged(tmp_path):
    dst = tmp_path / "documents" / "a.txt"
    assert unique_destination(dst) == dst, "Nothing exists there: return dst itself."
    assert not (tmp_path / "documents").exists(), "unique_destination must not create anything."


def test_taken_names_get_a_counter(tmp_path):
    (tmp_path / "a.txt").write_text("old", encoding="utf-8")
    assert unique_destination(tmp_path / "a.txt") == tmp_path / "a (1).txt", "If a.txt exists, use 'a (1).txt' (space, brackets)."
    (tmp_path / "a (1).txt").write_text("old", encoding="utf-8")
    assert unique_destination(tmp_path / "a.txt") == tmp_path / "a (2).txt", \
        "'a (1).txt' is taken too: keep counting. Returning it would overwrite a file."
    assert (tmp_path / "a.txt").read_text(encoding="utf-8") == "old", "Never touch existing files."


def test_no_suffix(tmp_path):
    (tmp_path / "README").write_text("x", encoding="utf-8")
    assert unique_destination(tmp_path / "README") == tmp_path / "README (1)", "With no suffix the counter goes at the end."


def test_double_suffix_keeps_the_last(tmp_path):
    (tmp_path / "b.tar.gz").write_text("x", encoding="utf-8")
    assert unique_destination(tmp_path / "b.tar.gz") == tmp_path / "b.tar (1).gz", \
        "Use dst.stem and dst.suffix: the stem of 'b.tar.gz' is 'b.tar'."


def test_a_folder_counts_as_taken(tmp_path):
    (tmp_path / "data.csv").mkdir()
    assert unique_destination(tmp_path / "data.csv") == tmp_path / "data (1).csv", "A folder with that name also blocks the name: use exists()."


def test_gap_in_the_numbers(tmp_path):
    for name in ("r.txt", "r (1).txt", "r (3).txt"):
        (tmp_path / name).write_text("x", encoding="utf-8")
    assert unique_destination(tmp_path / "r.txt") == tmp_path / "r (2).txt", "Return the FIRST free name."
