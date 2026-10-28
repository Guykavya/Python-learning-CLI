import pytest

from solution import read_or_default


def test_reads_text(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("héllo\nworld\n", encoding="utf-8")
    assert read_or_default(p, "none") == "héllo\nworld\n", "An existing file returns its whole text (UTF-8)."


def test_missing_returns_default(tmp_path):
    assert read_or_default(tmp_path / "nope.txt", "none") == "none", "A missing file must return the default."
    assert read_or_default(str(tmp_path / "nope.txt")) == "", "The default default is the empty string."


def test_default_can_be_any_object(tmp_path):
    marker = ["x"]
    assert read_or_default(tmp_path / "nope.txt", marker) is marker, "Return the default object itself."


def test_empty_file_is_not_missing(tmp_path):
    p = tmp_path / "empty.txt"
    p.write_text("")
    assert read_or_default(p, "none") == "", "An empty file exists, so return its text (empty), not the default."


def test_other_errors_not_hidden(tmp_path):
    with pytest.raises(OSError) as info:
        read_or_default(tmp_path, "none")
    assert not isinstance(info.value, FileNotFoundError), "A folder is not a missing file."


def test_folder_error_is_raised(tmp_path):
    folder = tmp_path / "sub"
    folder.mkdir()
    with pytest.raises(OSError):
        read_or_default(folder, "none")
    # reaching here means the error was not swallowed
