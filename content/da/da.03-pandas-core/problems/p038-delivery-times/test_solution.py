import datetime as dt

import numpy as np
import pandas as pd

from solution import delivery_report


def make():
    h = dt.timedelta
    start = dt.datetime(2025, 3, 1, 9, 0)
    rows = [
        (start, start + h(days=2, hours=12), 3),       # 2.5 days, on time
        (start, start + h(days=3), 3),                 # exactly on the promise: not late
        (start, start + h(days=3, minutes=1), 3),      # one minute late
        (start, None, 2),                              # still on its way
        (start + h(days=5), start + h(days=5, hours=6), 0),   # 0.25 days with a promise of 0: late
        (start, start + h(days=30), 7),    # 30 days against a promise of 7: late
    ]
    return pd.DataFrame({
        "id": range(len(rows)),
        "ordered": pd.to_datetime([r[0] for r in rows]),
        "delivered": pd.to_datetime([r[1] for r in rows]),
        "promised_days": [r[2] for r in rows],
    })


def test_days_are_float_days_not_whole_days():
    df = make()
    before = df.copy()
    out = delivery_report(df)
    pd.testing.assert_frame_equal(df, before, obj="the input frame")
    assert out.columns.tolist() == ["id", "ordered", "delivered", "promised_days", "days", "late"], (
        f"expected the old columns then 'days', 'late'; got {out.columns.tolist()}.")
    for i, r in df.iterrows():
        if pd.isna(r["delivered"]):
            assert np.isnan(out["days"].iloc[i]), f"row {i}: not delivered, so days should be NaN, got {out['days'].iloc[i]!r}."
            continue
        want = (r["delivered"].to_pydatetime() - r["ordered"].to_pydatetime()).total_seconds() / 86400
        assert out["days"].iloc[i] == np.float64(want) or abs(out["days"].iloc[i] - want) < 1e-9, (
            f"row {i}: days should be {want}, got {out['days'].iloc[i]!r}. `.dt.days` keeps whole days only; "
            "divide the timedelta by pd.Timedelta(days=1) to keep the fraction.")


def test_late_flag_is_strict_and_undelivered_is_not_late():
    out = delivery_report(make())
    assert out["late"].tolist() == [False, False, True, False, True, True], (
        f"late should be [False, False, True, False, True, True], got {out['late'].tolist()}. "
        "Late means days > promised (exactly on time is not late), and an undelivered order (NaN days) is not late.")
    assert str(out["late"].dtype) == "bool", f"late should have dtype bool, got {out['late'].dtype}."


def test_all_delivered_and_all_undelivered():
    df = make()
    one = delivery_report(df[df["delivered"].notna()].reset_index(drop=True))
    assert one["late"].tolist() == [False, False, True, True, True], f"got {one['late'].tolist()}."
    none = df.assign(delivered=pd.NaT).astype({"delivered": "datetime64[us]"})
    out = delivery_report(none)
    assert out["days"].isna().all() and not out["late"].any(), "with nothing delivered: all days NaN and nobody is late."
