import json
import os

import pytest

from solution import safe_update_json


def names(folder):
    return sorted(p.name for p in folder.iterdir())


def test_creates_file_when_missing(tmp_path):
    path = tmp_path / "stats.json"

    def add_visit(data):
        data["visits"] = data.get("visits", 0) + 1

    assert safe_update_json(path, add_visit) == {"visits": 1}, "A missing file starts as {} and the function updates it. Return the new data."
    assert json.loads(path.read_text()) == {"visits": 1}, "The file must contain the new data."
    safe_update_json(path, add_visit)
    assert json.loads(path.read_text()) == {"visits": 2}, "The second call loads the saved data and adds 1."
    assert names(tmp_path) == ["stats.json"], "No temp file may be left."


def test_function_may_return_new_value(tmp_path):
    path = tmp_path / "list.json"
    path.write_text("{}")
    result = safe_update_json(path, lambda data: ["replaced", 1])
    assert result == ["replaced", 1], "If fn returns something, that is the new data."
    assert json.loads(path.read_text()) == ["replaced", 1], "The returned value is what gets saved."


def test_in_place_change_with_none(tmp_path):
    path = tmp_path / "d.json"
    path.write_text(json.dumps({"a": 1}))
    result = safe_update_json(path, lambda data: data.update(b=2))
    assert result == {"a": 1, "b": 2}, "If fn returns None, the changed dict is the new data."


def test_fn_raises_leaves_file_alone(tmp_path):
    path = tmp_path / "keep.json"
    path.write_text('{"x": 1}')
    before = path.read_bytes()

    def bad(data):
        data["x"] = 999
        raise RuntimeError("crash in the middle")

    with pytest.raises(RuntimeError):
        safe_update_json(path, bad)
    assert path.read_bytes() == before, "If fn raises, the file must be unchanged, even if fn already changed the dict."
    assert names(tmp_path) == ["keep.json"], "No temp file may be left after an error in fn."


def test_unserialisable_result_leaves_file_alone(tmp_path):
    path = tmp_path / "keep.json"
    path.write_text('{"x": 1}')
    before = path.read_bytes()
    with pytest.raises(TypeError):
        safe_update_json(path, lambda data: {"ok": [1, 2, 3], "bad": {1, 2}})
    assert path.read_bytes() == before, "json.dump fails half-way through a set. The real file must not be touched."
    assert names(tmp_path) == ["keep.json"], "Delete the half-written temp file when json.dump fails."


def test_replace_failure_cleans_up(tmp_path, monkeypatch):
    path = tmp_path / "keep.json"
    path.write_text('{"x": 1}')
    before = path.read_bytes()

    def failing_replace(src, dst):
        raise OSError("disk problem")

    monkeypatch.setattr(os, "replace", failing_replace)
    with pytest.raises(OSError):
        safe_update_json(path, lambda data: {"x": 2})
    monkeypatch.undo()
    assert path.read_bytes() == before, "If os.replace fails, the old file stays as it was."
    assert names(tmp_path) == ["keep.json"], "If os.replace fails, delete the temp file."


def test_bad_json_raises_and_keeps_file(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{not json")
    with pytest.raises(json.JSONDecodeError):
        safe_update_json(path, lambda data: {})
    assert path.read_text() == "{not json", "Do not overwrite a file that you could not read."
    assert names(tmp_path) == ["broken.json"], "No temp file may be left."


def test_fn_not_called_with_stale_copy(tmp_path):
    path = tmp_path / "n.json"
    for i in range(5):
        safe_update_json(path, lambda data: data.setdefault("items", []).append(i))
    assert json.loads(path.read_text()) == {"items": [0, 1, 2, 3, 4]}, "Every call must start from the saved file."
