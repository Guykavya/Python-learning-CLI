import pandas as pd

from solution import jobs_per_ist_day

# One row per rule. IST = UTC + 5:30, so the UTC clock time 18:30:00 is exactly midnight in India.
ROWS = [
    (1, "2025-01-31 09:00:00"),   # IST 14:30 on 31 Jan: same day
    (2, "2025-01-31 18:29:59"),   # IST 23:59:59 on 31 Jan: last second before midnight, same day
    (3, "2025-01-31 18:30:00"),   # IST 00:00:00 on 1 Feb: exactly on the boundary, next day
    (4, "2025-01-31 20:00:00"),   # IST 01:30 on 1 Feb: next day (the chapter's example)
    (5, "2025-02-01 02:00:00"),   # IST 07:30 on 1 Feb
    (6, "2025-02-28 23:59:00"),   # IST 05:29 on 1 Mar: leaves February
    (7, "2025-03-05 00:00:00"),   # IST 05:30 on 5 Mar
]


def jobs():
    return pd.DataFrame(ROWS, columns=["job_id", "created_at"]).assign(created_at=lambda d: pd.to_datetime(d["created_at"]))


def test_counts_per_ist_day():
    got = jobs_per_ist_day(jobs())
    want = {"2025-01-31": 2, "2025-02-01": 3, "2025-03-01": 1, "2025-03-05": 1}
    assert got == want, ("shift by +5:30 first, then take the date. UTC 18:30:00 is already the next day in India, "
                         "and UTC 18:29:59 is still the same day. Expected %s but got %s" % (want, got))


def test_dates_are_text_in_increasing_order_and_counts_are_ints():
    got = jobs_per_ist_day(jobs())
    assert list(got) == sorted(got), "list the dates in increasing order."
    assert all(isinstance(k, str) and len(k) == 10 for k in got), "keys are texts like '2025-02-01'."
    assert all(type(v) is int for v in got.values()), "counts must be plain ints."


def test_utc_dates_would_give_a_different_answer():
    utc = jobs()["created_at"].dt.strftime("%Y-%m-%d").value_counts().to_dict()
    got = jobs_per_ist_day(jobs())
    assert got != {k: int(v) for k, v in sorted(utc.items())}, "this data is built so that UTC dates and IST dates differ."
    assert got.get("2025-01-31") == 2, "only jobs 1 and 2 are on 31 January in India; jobs 3 and 4 are already on 1 February."


def test_input_unchanged_and_empty_table():
    d = jobs()
    jobs_per_ist_day(d)
    assert d["created_at"].iloc[3] == pd.Timestamp("2025-01-31 20:00:00"), "do not shift created_at inside the caller's table."
    empty = pd.DataFrame({"job_id": [], "created_at": pd.to_datetime([])})
    assert jobs_per_ist_day(empty) == {}, "no jobs gives an empty dict."
