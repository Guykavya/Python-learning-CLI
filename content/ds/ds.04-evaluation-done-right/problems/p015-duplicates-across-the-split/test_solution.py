import numpy as np
import pandas as pd

from solution import cross_split_duplicates


def test_worked_example():
    train = pd.DataFrame({"a": [1, 2, 2], "b": ["x", "y", "y"]})
    test = pd.DataFrame({"a": [2, 3, 1], "b": ["y", "z", "x"]}, index=[7, 8, 9])
    assert cross_split_duplicates(train, test, ["a", "b"]) == (2, [7, 9]), "test rows 7 and 9 also appear in train (row 7 once, even though train has two copies)."


def test_planted_overlap():
    rng = np.random.default_rng(1)
    df = pd.DataFrame({"a": rng.integers(0, 10**6, 400), "b": rng.integers(0, 10**6, 400)})
    train, test = df.iloc[:300], df.iloc[300:].copy()
    test.iloc[[3, 50, 77]] = train.iloc[[0, 10, 299]].to_numpy()
    count, ids = cross_split_duplicates(train, test, ["a", "b"])
    assert count == 3 and ids == sorted(test.index[[3, 50, 77]].tolist()), "three planted copies of training rows must be found, by index label."


def test_only_listed_columns_count():
    train = pd.DataFrame({"a": [1], "b": [2], "id": [100]})
    test = pd.DataFrame({"a": [1], "b": [2], "id": [200]})
    assert cross_split_duplicates(train, test, ["a", "b"])[0] == 1, "compare only the columns in `cols` (ids differ by design)."
    assert cross_split_duplicates(train, test, ["a", "b", "id"])[0] == 0, "with the id column included they are different rows."
