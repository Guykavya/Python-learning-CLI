import pandas as pd
import pytest
from solution import QUERY

events = pd.DataFrame({
    "event_id": [1, 2, 3, 4, 5, 6, 7, 8],
    "user_id": [1, 2, 1, 3, 2, 1, 3, 2],
    "event_time": pd.to_datetime(["2025-05-31 22:00", "2025-06-01 08:00", "2025-06-01 21:00", "2025-06-03 09:00",
                                  "2025-06-03 09:30", "2025-06-04 12:00", "2025-06-29 07:00", "2025-07-01 00:00"]),
    "event_type": ["login", "login", "login", "login", "view_course", "view_course", "login", "login"]})


def truth(events):
    e = events[(events["event_type"] == "login")]
    per = e.groupby(e["event_time"].dt.normalize()).size()
    return [(d.strftime("%Y-%m-%d"), int(per.get(d, 0))) for d in pd.date_range("2025-06-01", "2025-06-30")]


def test_columns(run):
    cols, _ = run(QUERY, events=events)
    assert cols == ["day", "logins"], "Columns: day, logins."


def test_thirty_rows(run):
    _, rows = run(QUERY, events=events)
    assert len(rows) == 30, f"June has 30 days and every day needs a row; you returned {len(rows)}. Start from generate_series and LEFT JOIN the events."


def test_example(run, same):
    _, rows = run(QUERY, events=events)
    got = dict(rows)
    assert got["2025-06-01"] == 2 and got["2025-06-02"] == 0, "1 June has 2 logins; 2 June has none and must show 0."
    assert got["2025-06-03"] == 1, "3 June: one login and one view_course; only logins count."
    assert same(rows, truth(events)), "Exactly the days of June, with the number of login events per day."


@pytest.mark.parametrize("seed", [28, 29])
def test_random_data(run, same, data, seed):
    _u, e, _o = data(seed, 60)
    _, rows = run(QUERY, events=e)
    assert same(rows, truth(e)), "Calendar LEFT JOIN login events; the login condition belongs in ON."
