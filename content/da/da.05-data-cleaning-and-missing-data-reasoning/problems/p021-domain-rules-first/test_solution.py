import numpy as np
import pandas as pd

from solution import flag_impossible


def frame():
    return pd.DataFrame({
        "age": [25, -3, 130, np.nan, 0, 120],
        "income": [50000.0, 0.0, -5.0, 120000.0, np.nan, 10.0],
        "city": ["a", "b", "c", "d", "e", "f"],
    }, index=[10, 11, 12, 13, 14, 15])


RULES = {"age": (0, 120), "income": (0, None)}


def test_flags_are_a_boolean_frame_with_the_same_index():
    flags, counts = flag_impossible(frame(), RULES)
    assert list(flags.columns) == ["age", "income"], "one column per rule, in the order of the rules (no column for 'city')."
    assert flags.index.tolist() == [10, 11, 12, 13, 14, 15], "keep the index of df, so the flags can be used as a mask."
    assert all(t == bool for t in flags.dtypes), "every flag column must be Boolean (True or False, never NaN)."


def test_values_with_two_bounds():
    flags, _ = flag_impossible(frame(), RULES)
    assert flags["age"].tolist() == [False, True, True, False, False, False], (
        "age -3 and 130 are impossible; 0 and 120 are allowed (inclusive bounds); the missing age is not impossible. "
        "Got %s." % flags["age"].tolist())


def test_none_means_no_limit():
    flags, _ = flag_impossible(frame(), RULES)
    assert flags["income"].tolist() == [False, False, True, False, False, False], (
        "income only has a low bound: -5 is impossible, 0 is allowed, 120000 is fine (no high bound), NaN is not flagged. "
        "Got %s." % flags["income"].tolist())


def test_counts_are_plain_ints():
    _, counts = flag_impossible(frame(), RULES)
    assert counts == {"age": 2, "income": 1}, "counts must be {'age': 2, 'income': 1}, got %s." % counts
    assert all(type(v) is int for v in counts.values()), "use int(...) so the counts are plain Python integers."


def test_low_bound_none():
    df = pd.DataFrame({"x": [1.0, 5.0, 11.0]})
    flags, counts = flag_impossible(df, {"x": (None, 10)})
    assert flags["x"].tolist() == [False, False, True], "(None, 10) only forbids values above 10."
    assert counts == {"x": 1}


def test_nullable_integer_column():
    df = pd.DataFrame({"age": pd.array([30, None, 200], dtype="Int64")})
    flags, counts = flag_impossible(df, {"age": (0, 120)})
    assert flags["age"].tolist() == [False, False, True], (
        "a missing Int64 value compares as <NA>; turn it into False (fillna(False)). Got %s." % flags["age"].tolist())
    assert counts == {"age": 1}


def test_input_not_changed():
    df = frame()
    before = df.copy()
    flag_impossible(df, RULES)
    pd.testing.assert_frame_equal(df, before, obj="the input frame")
