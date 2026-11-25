import hashlib
import json
import platform

import pytest

from solution import manifest


def test_known_digest():
    got = manifest([1, 2, 3], 42, {"bins": 10})
    want = hashlib.sha256(b"[1,2,3]").hexdigest()
    assert got["sha256"] == want, "Hash the canonical JSON text '[1,2,3]' (no spaces) encoded as UTF-8."


def test_other_fields():
    got = manifest([1, 2, 3], 42, {"bins": 10})
    assert got["seed"] == 42 and got["n"] == 3, "seed is copied and n is len(values)."
    assert got["params"] == {"bins": 10}, "params must be stored."
    assert got["python"] == platform.python_version(), "python must be platform.python_version()."
    assert set(got) == {"sha256", "seed", "params", "python", "n"}, "Return exactly the five keys."


def test_json_serialisable():
    text = json.dumps(manifest([1.5, 2.5], 1, {"a": [1, 2], "b": None}))
    assert json.loads(text)["n"] == 2, "The manifest must survive json.dumps."


def test_same_inputs_same_hash():
    a = manifest([3, 1, 2], 7, {})
    b = manifest([3, 1, 2], 7, {})
    assert a == b, "The same inputs must give the same manifest."


def test_record_key_order_does_not_change_the_hash():
    one = manifest([{"a": 1, "b": 2}, {"a": 3, "b": 4}], 0, {})["sha256"]
    two = manifest([{"b": 2, "a": 1}, {"b": 4, "a": 3}], 0, {})["sha256"]
    assert one == two, "Records with the same content but a different key order must hash the same: use sort_keys=True."


def test_a_changed_value_or_order_changes_the_hash():
    base = manifest([1, 2, 3], 0, {})["sha256"]
    assert manifest([1, 2, 4], 0, {})["sha256"] != base, "A changed value must change the hash."
    assert manifest([3, 2, 1], 0, {})["sha256"] != base, "A different order of values is different data: the hash changes."


def test_params_are_copied():
    params = {"bins": [1, 2]}
    m = manifest([1], 0, params)
    params["bins"].append(3)
    params["extra"] = True
    assert m["params"] == {"bins": [1, 2]}, "Store a deep copy of params: later changes by the caller must not change the manifest."


def test_unicode_and_floats():
    m = manifest(["caf\u00e9", 0.1, 1e-7], 1, {})
    want = hashlib.sha256(json.dumps(["caf\u00e9", 0.1, 1e-7], sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    assert m["sha256"] == want, "Encode the JSON text as UTF-8 before hashing."


@pytest.mark.parametrize("bad", [float("nan"), float("inf")])
def test_non_finite_values_are_refused(bad):
    with pytest.raises(ValueError):
        manifest([1.0, bad], 0, {})
