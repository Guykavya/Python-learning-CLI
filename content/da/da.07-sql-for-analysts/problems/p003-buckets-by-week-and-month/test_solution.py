import pandas as pd
import pytest
from solution import QUERY

users = pd.DataFrame({
    "user_id": [1, 2, 3, 4, 5, 6, 7],
    "signup_at": pd.to_datetime(["2024-12-31 09:00", "2025-01-01 10:00", "2025-01-05 23:59", "2025-01-06 00:00",
                                 "2025-01-31 12:00", "2025-02-01 08:00", "2025-02-10 15:30"]),
    "channel": ["organic", "ads", "ads", "referral", "organic", "ads", "organic"],
    "country": ["IN", "IN", "US", "UK", "US", "IN", "IN"]})


def truth(users):
    s = users["signup_at"]
    wk = (s.dt.normalize() - pd.to_timedelta(s.dt.weekday, unit="D")).dt.strftime("%Y-%m-%d")
    mo = s.dt.to_period("M").dt.start_time.dt.strftime("%Y-%m-%d")
    out = [("week", k, int(v)) for k, v in wk.value_counts().items()]
    out += [("month", k, int(v)) for k, v in mo.value_counts().items()]
    return out


def test_columns(run):
    cols, _ = run(QUERY, users=users)
    assert cols == ["period", "period_start", "signups"], "Columns: period, period_start, signups."


def test_example(run, same):
    _, rows = run(QUERY, users=users)
    want = [("week", "2024-12-30", 3), ("week", "2025-01-06", 1), ("week", "2025-01-27", 2), ("week", "2025-02-10", 1),
            ("month", "2024-12-01", 1), ("month", "2025-01-01", 4), ("month", "2025-02-01", 2)]
    assert same(rows, want), "Weeks start on Monday (users 3 and 4 are one minute apart but in different weeks); months start on the 1st."


def test_week_starts_monday(run):
    _, rows = run(QUERY, users=users)
    assert ("week", "2024-12-30", 3) in rows, "Users 1 (Tue 31 Dec), 2 (Wed 1 Jan) and 3 (Sun 5 Jan, 23:59) share the week that starts on Monday 2024-12-30."


@pytest.mark.parametrize("seed", [7, 8])
def test_random_data(run, same, data, seed):
    u, _e, _o = data(seed, 60)
    _, rows = run(QUERY, users=u)
    assert same(rows, truth(u)), "Group by date_trunc of the signup time, once per unit, and stack with UNION ALL."
