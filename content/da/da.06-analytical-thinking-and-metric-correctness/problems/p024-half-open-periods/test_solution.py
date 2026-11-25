import pandas as pd

from solution import in_period

TIMES = ["2025-01-31 23:59:59", "2025-02-01 00:00:00", "2025-02-14 12:00:00", "2025-02-28 15:30:00",
         "2025-02-28 23:59:59.500", "2025-03-01 00:00:00", "2025-03-01 00:00:01", None]


def series():
    return pd.Series(pd.to_datetime(TIMES, format="ISO8601"), index=list("abcdefgh"))


def test_february_with_both_boundaries():
    got = in_period(series(), "2025-02-01", "2025-03-01")
    assert got.tolist() == [False, True, True, True, True, False, False, False], (
        "check each timestamp: 01 Feb 00:00:00 is IN (start is included); 28 Feb 15:30 and 23:59:59.5 are IN "
        "(a closed '<= 2025-02-28' loses them); 01 Mar 00:00:00 is OUT (end is excluded). Got %s" % got.tolist())


def test_nat_is_false_not_missing():
    got = in_period(series(), "2025-02-01", "2025-03-01")
    assert got.dtype == bool, "the result must be plain True/False (dtype bool), NaT must give False. Got dtype %s." % got.dtype
    assert not got["h"], "NaT is not in any period."


def test_same_index_and_input_unchanged():
    s = series()
    got = in_period(s, "2025-02-01", "2025-03-01")
    assert list(got.index) == list("abcdefgh"), "keep the index of s so the mask can be used to filter s."
    assert s["h"] is pd.NaT or pd.isna(s["h"]), "do not change s (for example with fillna)."


def test_accepts_timestamps_and_texts():
    a = in_period(series(), pd.Timestamp("2025-02-01"), pd.Timestamp("2025-03-01"))
    b = in_period(series(), "2025-02-01", "2025-03-01")
    assert a.tolist() == b.tolist(), "start and end may be Timestamps or date texts; convert with pd.Timestamp."


def test_consecutive_months_have_no_gap_and_no_overlap():
    s = series()
    feb = in_period(s, "2025-02-01", "2025-03-01")
    mar = in_period(s, "2025-03-01", "2025-04-01")
    jan = in_period(s, "2025-01-01", "2025-02-01")
    assert (feb & mar).sum() == 0, "a timestamp must never be in two consecutive months: the end is excluded."
    assert (jan | feb | mar).sum() == 7, "every non-missing timestamp lies in Jan, Feb or Mar: there must be no gap."


def test_empty_period_is_empty():
    assert in_period(series(), "2025-02-01", "2025-02-01").sum() == 0, "start == end is an empty period."
