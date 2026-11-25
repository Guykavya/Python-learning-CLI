import time

import numpy as np
import pandas as pd

from solution import zscore_by_group


def slow(df, key="store_id", col="revenue"):
    return df.groupby(key)[col].transform(lambda s: (s - s.mean()) / s.std())


def lines():
    return pd.DataFrame({
        "order_id": [10001, 10001, 10002, 10003, 10004, 10005, 10006, 10007],
        "store_id": ["S1", "S2", "S1", "S3", "S2", "S1", "S2", "S4"],
        "revenue": [100.0, 40.0, 300.0, 55.0, 60.0, 200.0, 80.0, 70.0],
    }, index=[12, 3, 7, 0, 5, 9, 1, 30])


def best(fn, repeat):
    times = []
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    return min(times)


def test_small_values():
    z = zscore_by_group(lines())
    # S1: 100, 300, 200 -> mean 200, std 100 -> -1, 1, 0 ; S2: 40, 60, 80 -> mean 60, std 20 -> -1, 0, 1
    got = dict(zip(z.index, z.tolist()))
    assert got[12] == -1.0 and got[7] == 1.0 and got[9] == 0.0, (
        "S1 has 100, 300, 200: mean 200, std 100 (ddof=1), so z = -1, 1, 0; got %s, %s, %s" % (got[12], got[7], got[9]))
    assert got[3] == -1.0 and got[5] == 0.0 and got[1] == 1.0, "S2 has 40, 60, 80: mean 60, std 20, so z = -1, 0, 1"


def test_single_row_groups_are_nan():
    z = zscore_by_group(lines())
    assert np.isnan(z[0]) and np.isnan(z[30]), "S3 and S4 have one row: no standard deviation, so z must be NaN (as in the slow line)"


def test_index_and_name():
    df = lines()
    z = zscore_by_group(df)
    assert isinstance(z, pd.Series), "return a Series"
    assert z.index.tolist() == df.index.tolist(), "keep df's index, in df's order (do not reset or sort it)"
    assert z.name == "z", "name the Series 'z' (.rename('z'))"


def test_other_key_and_column():
    df = lines().rename(columns={"store_id": "shop", "revenue": "qty"})
    z = zscore_by_group(df, key="shop", col="qty")
    assert np.allclose(z, slow(df, "shop", "qty"), equal_nan=True), "use the key and col arguments, not fixed column names"


def test_matches_slow_and_is_much_faster():
    rng = np.random.default_rng(0)
    n = 300_000
    df = pd.DataFrame({"store_id": rng.integers(0, 2000, n), "revenue": rng.uniform(40, 900, n).round(2)})
    mine = zscore_by_group(df)
    assert np.allclose(mine, slow(df), equal_nan=True), "the fast version must give exactly the slow line's numbers"
    t_slow = best(lambda: slow(df), 1)
    t_mine = best(lambda: zscore_by_group(df), 3)
    assert t_mine * 5 <= t_slow, (
        "yours took %.0f ms, the lambda %.0f ms in this run: not 5x faster. Use g.transform('mean') and "
        "g.transform('std') (built-ins), no lambda or apply" % (t_mine * 1000, t_slow * 1000))


def test_input_unchanged():
    df = lines()
    before = df.copy()
    zscore_by_group(df)
    pd.testing.assert_frame_equal(df, before, obj="df")
