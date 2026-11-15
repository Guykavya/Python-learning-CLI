import json
import logging
import os
from pathlib import Path

import pytest

from solution import load_checkpoint, save_checkpoint


def files_in(folder):
    return sorted(p.name for p in Path(folder).iterdir())


def test_round_trip(tmp_path):
    path = tmp_path / "cp.json"
    state = {"run_id": "r7", "cursor": "tok006x", "loaded": 6, "city": "Pune → Mumbaï"}
    save_checkpoint(path, state)
    assert load_checkpoint(path) == state, "load_checkpoint must return exactly what was saved."
    on_disk = json.loads(path.read_text(encoding="utf-8"))
    assert on_disk == state, "The file must contain the state as JSON, written as UTF-8."


def test_accepts_a_str_path_and_creates_folders(tmp_path):
    path = tmp_path / "state" / "orders" / "cp.json"
    save_checkpoint(str(path), {"cursor": None})
    assert path.exists(), (
        "The checkpoint was not created. Convert str to Path and create missing parent folders "
        "(path.parent.mkdir(parents=True, exist_ok=True))."
    )
    assert load_checkpoint(str(path)) == {"cursor": None}


def test_overwrite_leaves_no_temp_file(tmp_path):
    path = tmp_path / "cp.json"
    save_checkpoint(path, {"cursor": "a"})
    save_checkpoint(path, {"cursor": "b"})
    assert load_checkpoint(path) == {"cursor": "b"}, "The second save must replace the first."
    assert files_in(tmp_path) == ["cp.json"], (
        f"Folder contains {files_in(tmp_path)}. After a successful save only cp.json may remain: "
        "os.replace MOVES the temp file onto the checkpoint."
    )


def test_crash_before_the_rename_keeps_the_old_checkpoint(tmp_path, monkeypatch):
    path = tmp_path / "cp.json"
    save_checkpoint(path, {"cursor": "tok003x", "loaded": 3})
    calls = []

    def crashing_replace(src, dst):
        calls.append((Path(src), Path(dst)))
        raise OSError("simulated crash just before the rename")

    monkeypatch.setattr(os, "replace", crashing_replace)
    with pytest.raises(OSError):
        save_checkpoint(path, {"cursor": "tok006x", "loaded": 6})
    monkeypatch.undo()

    assert calls, (
        "os.replace was never called. Write to a temp file and move it into place with "
        "os.replace; writing the checkpoint directly is not atomic."
    )
    src, dst = calls[0]
    assert dst == path, f"os.replace must move the temp file ONTO the checkpoint path, not to {dst}."
    assert src.parent == path.parent and src != path, (
        f"The temp file {src} must be a different file in the SAME folder as the checkpoint; "
        "a rename to another folder or disk is not atomic."
    )
    assert json.loads(path.read_text(encoding="utf-8")) == {"cursor": "tok003x", "loaded": 3}, (
        "The crash happened before the rename, yet the checkpoint changed. You wrote into the "
        "real file before os.replace; write the new content only into the temp file."
    )

    save_checkpoint(path, {"cursor": "tok006x", "loaded": 6})   # the next run works normally
    assert load_checkpoint(path) == {"cursor": "tok006x", "loaded": 6}
    assert files_in(tmp_path) == ["cp.json"], (
        f"Folder contains {files_in(tmp_path)}. A later successful save must reuse/replace the "
        "leftover temp file."
    )


def test_unserialisable_state_keeps_the_old_checkpoint(tmp_path):
    path = tmp_path / "cp.json"
    save_checkpoint(path, {"cursor": "ok"})
    with pytest.raises(TypeError):
        save_checkpoint(path, {"cursor": "next", "when": object()})
    assert load_checkpoint(path) == {"cursor": "ok"}, (
        "json could not serialise the new state, and the old checkpoint was damaged. The real "
        "file may only change through os.replace at the very end."
    )


def test_missing_file_returns_a_copy_of_the_default(tmp_path):
    path = tmp_path / "nope.json"
    assert load_checkpoint(path) == {}, "No file and no default: return {}."
    default = {"cursor": None, "loaded": 0}
    first = load_checkpoint(path, default)
    assert first == default, "No file: return the default."
    first["loaded"] = 99
    assert default == {"cursor": None, "loaded": 0}, (
        "Changing the returned dict changed the caller's default. Return a COPY (dict(default))."
    )
    assert not path.exists(), "Loading must not create the checkpoint file."


@pytest.mark.parametrize("content", [
    b'{"cursor": "tok0',          # truncated by a crash
    b"",                           # emptied by write_text, then the crash
    b"[1, 2, 3]",                 # valid JSON, but not an object
    b"\xff\xfe\x00garbage",       # not even UTF-8
    b"null",
])
def test_corrupt_file_is_moved_aside(tmp_path, caplog, content):
    caplog.set_level(logging.WARNING, logger="pipeline")
    path = tmp_path / "cp.json"
    path.write_bytes(content)
    result = load_checkpoint(path, {"cursor": None})
    assert result == {"cursor": None}, (
        f"For a corrupt file ({content!r}) return the default instead of crashing. Catch "
        "ValueError (JSONDecodeError and UnicodeDecodeError are both ValueErrors) and check "
        "that the result is a dict."
    )
    corrupt = tmp_path / "cp.json.corrupt"
    assert corrupt.exists() and corrupt.read_bytes() == content, (
        "Move the bad file to cp.json.corrupt (unchanged) so someone can inspect it later."
    )
    assert not path.exists(), "After moving it aside, cp.json must be gone so the next save starts clean."
    warnings = [r for r in caplog.records if r.name == "pipeline" and r.levelno == logging.WARNING]
    assert len(warnings) == 1 and "cp.json" in warnings[0].getMessage(), (
        "Log exactly one WARNING on logger 'pipeline' that names the file. A silently ignored "
        "corrupt checkpoint means a full re-run nobody can explain."
    )


def test_second_corruption_replaces_the_old_corrupt_copy(tmp_path):
    path = tmp_path / "cp.json"
    path.write_text("oops 1", encoding="utf-8")
    load_checkpoint(path)
    path.write_text("oops 2", encoding="utf-8")
    assert load_checkpoint(path) == {}, "A second corrupt file must also be handled."
    assert (tmp_path / "cp.json.corrupt").read_text(encoding="utf-8") == "oops 2", (
        "Use os.replace to move the file aside; it overwrites an older .corrupt file (and "
        "Path.rename fails on Windows when the target exists)."
    )


def test_leftover_temp_file_is_ignored(tmp_path):
    path = tmp_path / "cp.json"
    save_checkpoint(path, {"cursor": "good"})
    (tmp_path / "cp.json.tmp").write_text('{"cursor": "half-writ', encoding="utf-8")
    assert load_checkpoint(path) == {"cursor": "good"}, (
        "A .tmp file left by a crash is not the checkpoint. Read only the real path."
    )
    save_checkpoint(path, {"cursor": "newer"})
    assert load_checkpoint(path) == {"cursor": "newer"}
    assert files_in(tmp_path) == ["cp.json"]
