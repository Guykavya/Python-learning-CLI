import pandas as pd
import pytest
from solution import QUERY

events = pd.DataFrame({
    "event_id": list(range(1, 19)),
    "user_id": [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 4, 4, 4, 1],
    "event_time": pd.to_datetime([
        "2025-01-01 09:00", "2025-01-02 08:00", "2025-01-02 21:00", "2025-01-03 10:00", "2025-01-05 11:00", "2025-01-06 12:00",
        "2025-01-06 18:00",
        "2025-01-01 07:00", "2025-01-03 07:00", "2025-01-05 07:00",
        "2025-01-10 10:00", "2025-01-11 10:00",
        "2024-12-30 23:00", "2024-12-31 01:00", "2025-01-01 02:00", "2025-01-02 03:00", "2025-01-02 04:00",
        "2025-01-04 10:00"]),
    "event_type": ["login"] * 17 + ["view_course"]})


def truth(events):
    out = {}
    for uid, g in events[events["event_type"] == "login"].groupby("user_id"):
        days = sorted(set(g["event_time"].dt.normalize()))
        best = run = 1
        for a, b in zip(days, days[1:]):
            run = run + 1 if (b - a).days == 1 else 1
            best = max(best, run)
        out[int(uid)] = best
    return sorted(out.items())


def test_columns(run):
    cols, _ = run(QUERY, events=events)
    assert cols == ["user_id", "longest_streak"], "Columns: user_id, longest_streak."


def test_example(run, same):
    _, rows = run(QUERY, events=events)
    assert same(rows, [(1, 3), (2, 1), (3, 2), (4, 4)]), (
        "User 1: days 1-2-3 then 5-6 -> 3 (two logins on the 2nd count once, the view on the 4th does not count). "
        "User 2: every other day -> 1. User 3: 10-11 Jan -> 2. User 4: 30 Dec to 2 Jan -> 4 (across the new year).")


def test_duplicate_days_do_not_break_streak(run, same):
    e = events[events["user_id"] == 4]
    _, rows = run(QUERY, events=e)
    assert same(rows, [(4, 4)]), "Two logins on 2 January must count as one day: SELECT DISTINCT user and day before numbering."


def test_other_events_do_not_count(run, same):
    e = pd.DataFrame({"event_id": [1, 2, 3], "user_id": [1, 1, 1],
                      "event_time": pd.to_datetime(["2025-01-01 10:00", "2025-01-02 10:00", "2025-01-03 10:00"]),
                      "event_type": ["login", "view_course", "login"]})
    _, rows = run(QUERY, events=e)
    assert same(rows, [(1, 1)]), "Only login events count: the view on the 2nd breaks the streak."


@pytest.mark.parametrize("seed", [24, 25])
def test_random_data(run, same, data, seed):
    _u, e, _o = data(seed, 40)
    _, rows = run(QUERY, events=e)
    assert same(rows, truth(e)), "Longest run of consecutive login days per user (day minus row_number, grouped)."
