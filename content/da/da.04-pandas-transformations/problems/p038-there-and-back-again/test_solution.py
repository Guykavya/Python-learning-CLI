import math
import random

import pandas as pd
import pytest

from solution import to_long, to_wide


def random_long(seed):
    """A small long table: every store and every month has at least one row; some pairs are absent."""
    rng = random.Random(seed)
    stores = ["S%d" % i for i in range(1, rng.randint(2, 5) + 1)]
    months = ["2025-%02d" % m for m in range(1, rng.randint(3, 6) + 1)]
    pairs = {(s, m) for s in stores for m in months if rng.random() < 0.7}
    for s in stores:
        pairs.add((s, rng.choice(months)))
    for m in months:
        pairs.add((rng.choice(stores), m))
    pairs = list(pairs)
    rng.shuffle(pairs)
    return pd.DataFrame({"store_id": [p[0] for p in pairs], "month": [p[1] for p in pairs],
                         "sales": [rng.randint(0, 500) for _ in pairs]})


def slow_wide_cells(long):
    """{(store, month): sales} - what every wide cell must hold."""
    return {(s, m): v for s, m, v in long.itertuples(index=False)}


def small():
    return pd.DataFrame({"store_id": ["S2", "S1", "S1", "S2"], "month": ["2025-02", "2025-01", "2025-03", "2025-01"],
                         "sales": [7, 10, 0, 3]})


def test_to_wide_small():
    w = to_wide(small())
    assert list(w.columns) == ["store_id", "2025-01", "2025-02", "2025-03"], "store_id, then sorted months; got %s" % list(w.columns)
    assert w.columns.name is None, "clear columns.name after the pivot"
    assert w["store_id"].tolist() == ["S1", "S2"] and w.index.tolist() == [0, 1], "one row per store, sorted, fresh index"
    assert math.isnan(w.loc[0, "2025-02"]) and math.isnan(w.loc[1, "2025-03"]), "absent pairs must be NaN in the wide table (do not fill 0)"
    assert w.loc[0, "2025-03"] == 0, "a REAL zero (S1, March) must stay 0"


def test_to_long_small():
    back = to_long(to_wide(small()))
    assert len(back) == 4, "the round trip must give the 4 original rows back, not 6: drop the missing cells (got %d)" % len(back)
    assert str(back["sales"].dtype) == "int64", "sales must be int64 again after dropping the NaN cells (got %s)" % back["sales"].dtype
    assert back.values.tolist() == [["S1", "2025-01", 10], ["S1", "2025-03", 0], ["S2", "2025-01", 3], ["S2", "2025-02", 7]], (
        "rows sorted by store then month; the real 0 for S1 March must survive")


@pytest.mark.parametrize("seed", range(20))
def test_long_wide_long_round_trip(seed):
    long = random_long(seed)
    want = long.sort_values(["store_id", "month"]).reset_index(drop=True)
    w = to_wide(long)
    cells = slow_wide_cells(long)
    stores = sorted({s for s, _ in cells})
    months = sorted({m for _, m in cells})
    assert w.shape == (len(stores), len(months) + 1), "wide shape must be stores x (1 + months)"
    for i, s in enumerate(stores):
        for m in months:
            v = w.loc[i, m]
            if (s, m) in cells:
                assert v == cells[(s, m)], "cell (%s, %s) must hold %s" % (s, m, cells[(s, m)])
            else:
                assert math.isnan(v), "absent pair (%s, %s) must be NaN" % (s, m)
    back = to_long(w)
    pd.testing.assert_frame_equal(back, want, obj="to_long(to_wide(long)) (seed %d)" % seed)


@pytest.mark.parametrize("seed", range(20))
def test_wide_long_wide_round_trip(seed):
    w = to_wide(random_long(seed))
    pd.testing.assert_frame_equal(to_wide(to_long(w)), w, obj="to_wide(to_long(wide)) (seed %d)" % seed)


def test_inputs_unchanged():
    long = small()
    before = long.copy()
    w = to_wide(long)
    w_before = w.copy()
    to_long(w)
    pd.testing.assert_frame_equal(long, before, obj="long")
    pd.testing.assert_frame_equal(w, w_before, obj="wide")
