import pytest

from solution import atomic_open


def names(folder):
    return sorted(p.name for p in folder.iterdir())


def test_creates_new_file(tmp_path):
    target = tmp_path / "new.txt"
    with atomic_open(target, encoding="utf-8") as f:
        f.write("hello\n")
    assert target.read_text(encoding="utf-8") == "hello\n", "After the with block the file must have the new content."
    assert names(tmp_path) == ["new.txt"], "No temp file may stay in the folder."


def test_replaces_old_content(tmp_path):
    target = tmp_path / "a.txt"
    target.write_text("old")
    with atomic_open(target) as f:
        f.write("new")
    assert target.read_text() == "new", "The old content must be replaced by the new content."
    assert names(tmp_path) == ["a.txt"], "No temp file may stay in the folder."


def test_old_file_untouched_while_writing(tmp_path):
    target = tmp_path / "a.txt"
    target.write_text("old")
    with atomic_open(target) as f:
        f.write("partial new text")
        f.flush()
        assert target.read_text() == "old", "While the block runs, the real file must still have the old content. Write to a temp file."
    assert target.read_text() == "partial new text", "After the block the new content is in place."


def test_new_file_not_visible_until_done(tmp_path):
    target = tmp_path / "later.txt"
    with atomic_open(target) as f:
        f.write("x")
        f.flush()
        assert not target.exists(), "A new file must not exist before the block ends."
    assert target.exists(), "It exists after the block."


def test_error_keeps_old_file_and_cleans_up(tmp_path):
    target = tmp_path / "keep.txt"
    target.write_text("precious")
    with pytest.raises(RuntimeError):
        with atomic_open(target) as f:
            f.write("half written")
            raise RuntimeError("crash")
    assert target.read_text() == "precious", "After an error the old file must be unchanged."
    assert names(tmp_path) == ["keep.txt"], "After an error the temp file must be deleted."


def test_error_with_no_old_file(tmp_path):
    target = tmp_path / "never.txt"
    with pytest.raises(ValueError):
        with atomic_open(target) as f:
            f.write("x")
            raise ValueError("bad")
    assert names(tmp_path) == [], "If the block fails and there was no file, nothing may be left behind."


def test_binary_mode(tmp_path):
    target = tmp_path / "b.bin"
    with atomic_open(target, "wb") as f:
        f.write(b"\x00\x01\x02")
    assert target.read_bytes() == b"\x00\x01\x02", "Mode 'wb' must give a binary file object."


def test_kwargs_are_passed(tmp_path):
    target = tmp_path / "u.txt"
    with atomic_open(target, encoding="utf-8", newline="\n") as f:
        f.write("caf\u00e9\n")
    assert target.read_bytes() == b"caf\xc3\xa9\n", "Pass **kwargs (encoding, newline) on to the file object."
