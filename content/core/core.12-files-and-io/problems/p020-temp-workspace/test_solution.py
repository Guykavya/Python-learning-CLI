import os
from pathlib import Path

from solution import sort_via_temp


def test_sorted_lines(tmp_path):
    lines, path = sort_via_temp("pear\napple\nfig\n")
    assert lines == ["apple", "fig", "pear"], "Return the sorted lines without newlines."


def test_path_is_gone(tmp_path):
    lines, path = sort_via_temp("b\na\n")
    assert isinstance(path, str), "Return the path as a str."
    assert Path(path).name == "work.txt", "The file must be called work.txt."
    assert not os.path.exists(path), "The temporary file must be deleted when the function returns. Use TemporaryDirectory() in a with block."
    assert not os.path.exists(os.path.dirname(path)), "The temporary folder must be deleted too."


def test_each_call_is_separate(tmp_path):
    _, p1 = sort_via_temp("x\n")
    _, p2 = sort_via_temp("y\n")
    assert p1 != p2, "Each call needs its own fresh temporary folder."


def test_nothing_in_current_folder(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    sort_via_temp("z\na\n")
    assert os.listdir(tmp_path) == [], "Do not create files in the current folder. Write inside the temporary folder."


def test_empty_and_unicode(tmp_path):
    assert sort_via_temp("")[0] == [], "Empty text gives no lines."
    assert sort_via_temp("é\nz\na\n")[0] == ["a", "z", "é"], "Use UTF-8 for writing and reading; sorting is by code point."
