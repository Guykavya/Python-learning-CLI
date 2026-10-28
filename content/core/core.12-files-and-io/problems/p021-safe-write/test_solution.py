import os

import pytest

from solution import safe_write


def test_new_file(tmp_path):
    p = tmp_path / "data.txt"
    safe_write(p, "hello é\n")
    assert p.read_bytes() == "hello é\n".encode("utf-8"), "Write the text as UTF-8 to a new file."
    assert os.listdir(tmp_path) == ["data.txt"], "Only data.txt may exist afterwards. No temporary file may stay."


def test_replaces_old(tmp_path):
    p = tmp_path / "data.txt"
    p.write_text("old old old old\n")
    safe_write(str(p), "new\n")
    assert p.read_text() == "new\n", "The new text must replace the old text."
    assert os.listdir(tmp_path) == ["data.txt"], "No leftover temporary files."


def test_failure_keeps_old_file(tmp_path):
    p = tmp_path / "data.txt"
    p.write_text("precious\n")
    with pytest.raises(TypeError):
        safe_write(p, b"these are bytes")
    assert p.read_text() == "precious\n", "The write failed, but the old file must be untouched. Never open `path` itself for writing."


def test_failure_leaves_no_temp_file(tmp_path):
    p = tmp_path / "data.txt"
    p.write_text("keep\n")
    with pytest.raises(TypeError):
        safe_write(p, 12345)
    assert os.listdir(tmp_path) == ["data.txt"], "Delete the temporary file when the write fails, then re-raise the error."


def test_failure_on_new_file_creates_nothing(tmp_path):
    p = tmp_path / "never.txt"
    with pytest.raises(TypeError):
        safe_write(p, None)
    assert os.listdir(tmp_path) == [], "If writing fails and the target did not exist, nothing may be created."


def test_many_writes(tmp_path):
    p = tmp_path / "data.txt"
    for i in range(20):
        safe_write(p, f"version {i}\n")
    assert p.read_text() == "version 19\n", "Each call replaces the previous content."
    assert os.listdir(tmp_path) == ["data.txt"], "No leftover temporary files."
