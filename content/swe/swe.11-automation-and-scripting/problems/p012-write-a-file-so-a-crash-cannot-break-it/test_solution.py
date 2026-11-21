import os
from pathlib import Path

import pytest

import solution
from solution import atomic_write_text


def files_in(folder):
    return sorted(p.name for p in folder.iterdir())


def test_writes_and_replaces(tmp_path):
    target = tmp_path / "state.json"
    atomic_write_text(target, '{"last_run": 1}')
    atomic_write_text(target, '{"last_run": 2}')
    assert target.read_text(encoding="utf-8") == '{"last_run": 2}'
    assert files_in(tmp_path) == ["state.json"], "No temp files may be left after a successful write."


def test_accepts_a_string_path_and_writes_utf8(tmp_path):
    target = tmp_path / "note.txt"
    atomic_write_text(str(target), "héllo ✓")
    assert target.read_bytes() == "héllo ✓".encode("utf-8"), "Write UTF-8 explicitly (os.fdopen(fd, 'w', encoding='utf-8'))."


def test_temp_file_is_in_the_same_folder(tmp_path, monkeypatch):
    seen = []
    real_replace = os.replace

    def spy(src, dst):
        seen.append((Path(src), Path(dst)))
        return real_replace(src, dst)

    monkeypatch.setattr(solution.os, "replace", spy)
    target = tmp_path / "state.json"
    atomic_write_text(target, "x")
    assert len(seen) == 1, "Finish with exactly one os.replace(tmp, path)."
    src, dst = seen[0]
    assert src.parent == tmp_path, f"The temp file must be in the SAME folder as the target (atomic rename); it was in {src.parent}"
    assert dst == target


def test_fsync_is_called(tmp_path, monkeypatch):
    synced = []
    real_fsync = os.fsync

    def spy(fd):
        synced.append(fd)
        return real_fsync(fd)

    monkeypatch.setattr(solution.os, "fsync", spy)
    atomic_write_text(tmp_path / "a.txt", "data")
    assert synced, "Call os.fsync(f.fileno()) after flush(), so the bytes reach the disk before the rename."


def test_crash_before_replace_keeps_the_old_content(tmp_path, monkeypatch):
    target = tmp_path / "state.json"
    target.write_text("OLD", encoding="utf-8")

    def crash(src, dst):
        raise OSError("simulated crash")

    monkeypatch.setattr(solution.os, "replace", crash)
    with pytest.raises(OSError, match="simulated crash"):
        atomic_write_text(target, "NEW")
    assert target.read_text(encoding="utf-8") == "OLD", "A crash before the replace must leave the old file untouched."
    assert files_in(tmp_path) == ["state.json"], "After a failure, delete the temp file (no '*.tmp' left behind)."


def test_crash_while_writing_keeps_the_old_content(tmp_path, monkeypatch):
    target = tmp_path / "state.json"
    target.write_text("OLD", encoding="utf-8")

    def crash(fd):
        raise OSError("disk full")

    monkeypatch.setattr(solution.os, "fsync", crash)
    with pytest.raises(OSError, match="disk full"):
        atomic_write_text(target, "NEW")
    assert target.read_text(encoding="utf-8") == "OLD", "Never write into the target directly: it would be half-written now."
    assert files_in(tmp_path) == ["state.json"], "Clean up the temp file and re-raise."


def test_missing_folder_is_an_error(tmp_path):
    with pytest.raises(OSError):
        atomic_write_text(tmp_path / "no" / "such" / "file.txt", "x")
