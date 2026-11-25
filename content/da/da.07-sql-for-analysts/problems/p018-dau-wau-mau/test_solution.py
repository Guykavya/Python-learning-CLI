import pandas as pd
import pytest
from solution import QUERY

events = pd.DataFrame({
    "event_id": list(range(1, 9)),
    "user_id": [1, 1, 2, 3, 4, 4, 5, 2],
    "event_time": pd.to_datetime(["2025-06-01 09:00", "2025-06-02 09:00", "2025-06-01 10:00", "2025-06-08 11:00",
                                  "2025-06-08 12:00", "2025-06-09 08:00", "2025-07-05 10:00", "2025-06-08 13:00"]),
    "event_type": ["login", "login", "login", "login", "login", "login", "login", "view_course"]})


def truth(events):
    e = events[events["event_type"] == "login"]
    day = e["event_time"].dt.normalize()
    out = []
    for d in pd.date_range(day.min(), day.max()):
        def users(back):
            return int(e.loc[(day >= d - pd.Timedelta(days=back)) & (day <= d), "user_id"].nunique())
        out.append((d.strftime("%Y-%m-%d"), users(0), users(6), users(29)))
    return out


def test_columns(run):
    cols, _ = run(QUERY, events=events)
    assert cols == ["day", "dau", "wau", "mau"], "Columns: day, dau, wau, mau."


def test_example(run, same):
    _, rows = run(QUERY, events=events)
    got = {r[0]: r[1:] for r in rows}
    assert len(rows) == 35, "One row per calendar day from 1 June to 5 July: 35 rows (days without logins included)."
    assert got["2025-06-08"] == (2, 3, 4), "8 June: DAU 2 (users 3, 4); WAU 3 (users 1, 3, 4: user 2 logged in on 1 June, outside 2-8 June); MAU 4."
    assert got["2025-06-09"] == (1, 2, 4), "9 June: DAU 1 (user 4); WAU = users active 3-9 June = 3 and 4; MAU 4."
    assert same(rows, truth(events)), "Compare each day with a Python loop over the window."


def test_distinct_not_summed(run):
    e = pd.DataFrame({"event_id": [1, 2, 3], "user_id": [1, 1, 1],
                      "event_time": pd.to_datetime(["2025-06-01 09:00", "2025-06-02 09:00", "2025-06-03 09:00"]),
                      "event_type": ["login"] * 3})
    _, rows = run(QUERY, events=e)
    assert rows[-1][2] == 1 and rows[-1][3] == 1, "One user active on three days is ONE weekly and ONE monthly active user: count DISTINCT users."


@pytest.mark.parametrize("seed", [30, 31])
def test_random_data(run, same, data, seed):
    _u, e, _o = data(seed, 25)
    _, rows = run(QUERY, events=e)
    assert same(rows, truth(e)), "For each day: distinct users in day, the last 7 days, the last 30 days (both ends included)."
