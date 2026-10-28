import pytest

from solution import count_by_type, leaves
from solution import partition as _partition


def partition(eg, exc_type):
    try:
        return _partition(eg, exc_type)
    except (TypeError, AttributeError) as e:
        pytest.fail(
            f"partition raised {type(e).__name__}: {e}. eg.split() returns None for an empty part; "
            "turn None into [] before you look for leaves."
        )


def sample():
    return ExceptionGroup("upload", [
        ValueError("bad name"),
        ExceptionGroup("file a", [
            OSError("disk full"),
            ExceptionGroup("chunk 3", [ValueError("bad crc")]),
        ]),
        KeyError("size"),
    ])


def test_leaves_paths_and_order():
    got = [(path, str(e)) for path, e in leaves(sample())]
    assert got == [((0,), "bad name"), ((1, 0), "disk full"), ((1, 1, 0), "bad crc"), ((2,), "'size'")], (
        f"Got {got}. Go depth first, left to right. The path holds the index at every level, "
        "so the leaf inside 'chunk 3' has path (1, 1, 0)."
    )


def test_paths_are_tuples():
    for path, _ in leaves(sample()):
        assert type(path) is tuple, "Each path is a tuple of ints, for example (1, 0), even for one level: (0,)."


def test_leaves_are_the_same_objects():
    eg = sample()
    inner = eg.exceptions[1].exceptions[1].exceptions[0]
    found = [e for path, e in leaves(eg) if path == (1, 1, 0)]
    assert found and found[0] is inner, "Return the leaf objects themselves, not copies or their messages."


def test_flat_group():
    a, b = ValueError("a"), TypeError("b")
    got = leaves(ExceptionGroup("flat", [a, b]))
    assert [(p, e) for p, e in got] == [((0,), a), ((1,), b)], "A flat group: paths (0,) and (1,)."


def test_deep_nesting():
    eg = ExceptionGroup("l0", [ExceptionGroup("l1", [ExceptionGroup("l2", [ExceptionGroup("l3", [ValueError("deep")])])])])
    got = [(p, str(e)) for p, e in leaves(eg)]
    assert got == [((0, 0, 0, 0), "deep")], "Recursion must work at any depth: four levels give a path of length 4."


def test_groups_are_not_leaves():
    for _, exc in leaves(sample()):
        assert not isinstance(exc, BaseExceptionGroup), "A nested group is not a leaf. Go inside it."


def test_base_exception_group():
    stop = KeyboardInterrupt()
    eg = BaseExceptionGroup("mixed", [ValueError("v"), BaseExceptionGroup("inner", [stop])])
    try:
        got = leaves(eg)
    except TypeError:
        pytest.fail("A BaseExceptionGroup is an exception group too. Check isinstance(eg, BaseExceptionGroup).")
    assert [p for p, _ in got] == [(0,), (1, 0)], "Check for BaseExceptionGroup (the parent class), not only ExceptionGroup."
    assert got[1][1] is stop, "The KeyboardInterrupt is a leaf too."


def test_not_a_group():
    with pytest.raises(TypeError, match="expected an exception group"):
        leaves(ValueError("x"))
    with pytest.raises(TypeError, match="expected an exception group"):
        leaves([ValueError("x")])


def test_count_by_type():
    counts = count_by_type(sample())
    assert counts == {"ValueError": 2, "OSError": 1, "KeyError": 1}, f"Count every leaf by class name. Got {counts}."
    assert list(counts) == ["ValueError", "OSError", "KeyError"], "Keys in the order each class first appears in leaves()."


def test_count_uses_exact_class_name():
    class UploadError(ValueError):
        pass

    eg = ExceptionGroup("g", [UploadError("u"), ValueError("v"), UploadError("w")])
    assert count_by_type(eg) == {"UploadError": 2, "ValueError": 1}, "Use type(exc).__name__: a subclass has its own name."


def test_partition():
    assert partition(sample(), ValueError) == (["bad name", "bad crc"], ["disk full", "'size'"]), (
        "matched: leaves that are ValueErrors (also the nested one); rest: the others, both in leaf order."
    )


def test_partition_with_parent_class():
    assert partition(sample(), LookupError) == (["'size'"], ["bad name", "disk full", "bad crc"]), (
        "KeyError is a subclass of LookupError, so it matches. split() uses isinstance."
    )


def test_partition_nothing_matches():
    assert partition(sample(), ZeroDivisionError) == ([], ["bad name", "disk full", "bad crc", "'size'"]), (
        "When nothing matches, split() returns None for the match part. Turn None into []."
    )


def test_partition_everything_matches():
    assert partition(sample(), Exception) == (["bad name", "disk full", "bad crc", "'size'"], []), (
        "When everything matches, the rest part is None. Turn it into []."
    )


def test_partition_tuple_of_types():
    assert partition(sample(), (OSError, KeyError)) == (["disk full", "'size'"], ["bad name", "bad crc"]), (
        "split() also accepts a tuple of types, like isinstance."
    )
