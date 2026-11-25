import numpy as np
import pandas as pd

from solution import time_split


def test_day_numbers():
    df = pd.DataFrame({"day": [1, 5, 9, 10, 12], "y": [0, 1, 0, 1, 1]})
    tr, te = time_split(df, "day", 10)
    assert tr["day"].tolist() == [1, 5, 9], "training rows: strictly before the cutoff."
    assert te["day"].tolist() == [10, 12], "a row ON the cutoff goes to the test part."


def test_every_train_date_before_every_test_date():
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"date": pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 365, 500), unit="D"), "x": rng.normal(size=500)})
    tr, te = time_split(df, "date", "2024-09-01")
    assert tr["date"].max() < pd.Timestamp("2024-09-01") <= te["date"].min(), "all training dates before the cutoff, all test dates on or after it."
    assert len(tr) + len(te) == 500, "no row lost."


def test_order_and_index_kept():
    df = pd.DataFrame({"day": [9, 2, 11, 3]}, index=[40, 10, 30, 20])
    tr, te = time_split(df, "day", 5)
    assert list(tr.index) == [10, 20] and list(te.index) == [40, 30], "keep the original order and index labels (do not sort or reset)."
