import math

import pandas as pd
import pytest

from solution import reconcile


def lines():
    return pd.DataFrame({
        "order_id": [10001, 10001, 10002, 10003, 10004, 10005],
        "store_id": ["S1", "S1", "S2", "S1", "S3", "S2"],
        "category": ["grocery", "toys", "home", "grocery", "toys", "office"],
        "revenue": [120.10, 80.20, 300.30, 49.40, 150.00, 0.00],
    })


def test_groupby_parts_reconcile():
    df = lines()
    ok, diff = reconcile(df.groupby("store_id")["revenue"].sum(), df["revenue"].sum(), "by store")
    assert ok is True, "revenue by store must add up to the total: ok must be True"
    assert diff == 0.0, "the difference is 0.0 (got %r)" % diff


def test_types_are_plain_python():
    ok, diff = reconcile({"a": 1.0, "b": 2.0}, 3.0)
    assert type(ok) is bool, "ok must be a plain bool, not %s" % type(ok).__name__
    assert type(diff) is float, "difference must be a plain float, not %s" % type(diff).__name__


def test_float_noise_passes_and_no_negative_zero():
    ok, diff = reconcile([0.1] * 10, 1.0, "noise")
    assert ok, "0.1 ten times is 0.9999999999999999: within the tolerance, so ok"
    assert diff == 0.0 and math.copysign(1.0, diff) == 1.0, (
        "round(-1.1e-16, 2) is -0.0; return 0.0 instead (add 0.0 after rounding); got %r" % diff)


def test_dict_and_list_parts():
    assert reconcile({"S1": 100.0, "S2": 50.0}, 150.0) == (True, 0.0), (
        "a dict of parts: add the VALUES (pd.Series(parts).sum()), not the keys")
    assert reconcile([100.0, 50.0], 150.0) == (True, 0.0), "a list of parts works too"


def test_mismatch_reports_difference():
    df = lines()
    parts = df.groupby("category")["revenue"].sum().drop("toys")
    ok, diff = reconcile(parts, df["revenue"].sum(), "forgot toys")
    assert ok is False, "a breakdown that leaves out a category does not reconcile"
    assert diff == -230.2, "the missing toys revenue is 80.20 + 150.00 = 230.20, so diff = -230.2 (got %r)" % diff


def test_tolerance():
    assert reconcile([10.0, 10.4], 20.0, tol=0.5)[0] is True, "a difference of 0.4 is inside tol=0.5"
    assert reconcile([10.0, 10.4], 20.0)[0] is False, "but outside the default tol=0.01"
    assert reconcile([10.0, 0.01], 10.0) == (True, 0.01), "exactly one cent off is still ok with tol=0.01 (<=)"


def test_strict_raises_readable_message():
    with pytest.raises(ValueError) as err:
        reconcile({"S1": 6216711.12}, 7360844.05, "revenue by store", strict=True)
    assert str(err.value) == "revenue by store: parts=6,216,711.12 total=7,360,844.05 diff=-1,144,132.93", (
        "message format '<label>: parts=<sum> total=<total> diff=<diff>' with ',' separators and 2 decimals; got %r" % str(err.value))


def test_strict_does_not_raise_when_ok():
    assert reconcile([1.0, 2.0], 3.0, "fine", strict=True) == (True, 0.0), "strict only raises on a mismatch"


def test_default_does_not_raise():
    assert reconcile([1.0], 3.0, "report only") == (False, -2.0), "without strict, a mismatch is returned, not raised"


def test_parts_unchanged():
    s = pd.Series({"S1": 1.0, "S2": 2.0})
    before = s.copy()
    reconcile(s, 3.0)
    pd.testing.assert_series_equal(s, before, obj="parts")
