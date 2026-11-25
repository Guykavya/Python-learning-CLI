import numpy as np
import pytest

from solution import load_dataset, save_dataset


def sample():
    return {
        "scores": np.array([[1.5, 2.25], [3.0, -1.0]], dtype=np.float32),
        "ids": np.array([7, 8, 9], dtype=np.int16),
        "passed": np.array([True, False, True]),
        "names": np.array(["Asha", "Bo", "Chen"]),
        "total": np.array(42.0),
    }


def test_round_trip_keeps_names_shapes_and_dtypes(tmp_path):
    p = tmp_path / "survey.npz"
    arrays = sample()
    save_dataset(p, **arrays)
    got = load_dataset(p)
    assert isinstance(got, dict), f"load_dataset must return a plain dict, got {type(got).__name__} (copy the NpzFile into a dict)."
    assert sorted(got) == sorted(arrays), f"names must survive the round trip: expected {sorted(arrays)}, got {sorted(got)}."
    for name, a in arrays.items():
        b = got[name]
        assert isinstance(b, np.ndarray), f"{name}: expected an array, got {type(b).__name__}."
        assert b.dtype == a.dtype, f"{name}: dtype must stay {a.dtype}, got {b.dtype} (do not convert before saving)."
        assert b.shape == a.shape, f"{name}: shape must stay {a.shape}, got {b.shape}."
        np.testing.assert_array_equal(b, a, err_msg=f"{name}: values changed in the round trip.")


def test_file_is_written_exactly_at_path(tmp_path):
    p = tmp_path / "survey.data"
    save_dataset(p, x=np.arange(3))
    assert p.exists(), ("the file must be written exactly at the given path; np.savez(path) adds '.npz' to a name "
                        "without it. Open the file yourself: with open(path, 'wb') as f: np.savez(f, ...).")
    assert not (tmp_path / "survey.data.npz").exists(), "found survey.data.npz: write to the exact path instead."
    assert load_dataset(p)["x"].tolist() == [0, 1, 2], "reading back from the exact path failed."


def test_str_path_works(tmp_path):
    p = str(tmp_path / "plain.npz")
    save_dataset(p, a=np.array([1.0]))
    assert load_dataset(p)["a"].tolist() == [1.0], "a str path must work as well as a Path."


def test_values_are_in_memory_after_loading(tmp_path):
    p = tmp_path / "d.npz"
    save_dataset(p, a=np.arange(5))
    got = load_dataset(p)
    p.unlink()   # works on Windows only if the file was closed
    assert got["a"].tolist() == [0, 1, 2, 3, 4], "the arrays must be read into memory before the file is closed (not lazy)."


def test_no_arrays_raises(tmp_path):
    with pytest.raises(ValueError):
        save_dataset(tmp_path / "empty.npz")


def test_object_array_is_refused_when_saving(tmp_path):
    with pytest.raises(ValueError) as info:
        save_dataset(tmp_path / "bad.npz", good=np.arange(2), mixed=np.array([1, "two", None], dtype=object))
    assert "mixed" in str(info.value), f"the message should name the object array ('mixed'), got {str(info.value)!r}."


def test_loading_a_pickled_object_array_raises(tmp_path):
    p = tmp_path / "evil.npz"
    np.savez(p, payload=np.array([{"a": 1}, [2, 3]], dtype=object))   # stored with pickle
    with pytest.raises(ValueError):
        load_dataset(p)


def test_inputs_are_not_changed(tmp_path):
    a = np.array([3.0, 1.0, 2.0])
    save_dataset(tmp_path / "k.npz", a=a)
    assert a.tolist() == [3.0, 1.0, 2.0], "saving must not change the caller's array."
