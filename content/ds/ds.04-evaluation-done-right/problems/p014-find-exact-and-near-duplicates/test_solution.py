import numpy as np
import pandas as pd

from solution import duplicate_groups


def test_worked_example():
    df = pd.DataFrame({"a": [1.0, 2.0, 1.0004, 1.0], "b": ["x", "y", "x", "z"]})
    out = duplicate_groups(df, ["a", "b"], 2)
    assert out.tolist() == [0, 1, 0, 2], "rows 0 and 2 are equal after rounding to 2 decimals; ids follow first appearance."


def test_planted_near_copies_are_found():
    rng = np.random.default_rng(0)
    base = pd.DataFrame({"amount": rng.uniform(10, 500, 100).round(2), "shop": rng.choice(["A", "B", "C"], 100)})
    copies = base.iloc[[5, 17, 42]].copy()
    copies["amount"] = copies["amount"] + 0.0004          # re-export noise
    df = pd.concat([base, copies], ignore_index=True)
    out = duplicate_groups(df, ["amount", "shop"], 2)
    for orig, copy in zip([5, 17, 42], [100, 101, 102]):
        assert out[orig] == out[copy], f"row {copy} is a near-copy of row {orig} and must get the same group id."
    assert out.nunique() == base.drop_duplicates().shape[0], "every other row is its own group."


def test_aligned_with_the_index_and_input_unchanged():
    df = pd.DataFrame({"a": [3.14159, 3.14, 2.0]}, index=[10, 20, 30])
    before = df.copy()
    out = duplicate_groups(df, ["a"], 2)
    assert list(out.index) == [10, 20, 30] and out.tolist() == [0, 0, 1], "aligned with df.index; 3.14159 and 3.14 match at 2 decimals."
    pd.testing.assert_frame_equal(df, before)


def test_more_decimals_separate_them():
    df = pd.DataFrame({"a": [3.14159, 3.14]})
    assert duplicate_groups(df, ["a"], 4).tolist() == [0, 1], "with 4 decimals the two values differ."
