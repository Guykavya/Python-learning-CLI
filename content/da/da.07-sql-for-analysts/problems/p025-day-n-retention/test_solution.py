import pandas as pd
import pytest
from solution import QUERY

users = pd.DataFrame({
    "user_id": [1, 2, 3, 4, 5],
    "signup_at": pd.to_datetime(["2025-06-15 09:00", "2025-06-16 20:00", "2025-03-01 10:00", "2025-03-10 11:00", "2025-07-10 08:00"]),
    "channel": ["organic", "ads", "ads", "referral", "organic"],
    "country": ["IN", "IN", "US", "UK", "US"]})
events = pd.DataFrame({
    "event_id": list(range(1, 13)),
    "user_id": [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 5, 5],
    "event_time": pd.to_datetime(["2025-06-16 07:00", "2025-06-22 22:00", "2025-07-15 06:00", "2025-06-17 10:00", "2025-06-25 10:00", "2025-06-16 20:00",
                                  "2025-03-02 23:30", "2025-03-08 06:00", "2025-03-31 12:00", "2025-03-10 11:00", "2025-07-10 08:00", "2025-07-11 09:00"]),
    "event_type": "login"})


def truth(users, events):
    login = events[events["event_type"] == "login"]
    days = set(zip(login["user_id"], login["event_time"].dt.normalize()))
    out = []
    for n in (1, 7, 30):
        elig = ret = 0
        for r in users.itertuples():
            d = r.signup_at.normalize() + pd.Timedelta(days=n)
            if d <= pd.Timestamp("2025-07-15"):
                elig += 1
                ret += (r.user_id, d) in days
        out.append((n, elig, ret, (ret / elig) if elig else None))
    return out


def test_columns(run):
    cols, _ = run(QUERY, users=users, events=events)
    assert cols == ["day_n", "eligible_users", "retained_users", "retention"], "Columns: day_n, eligible_users, retained_users, retention."


def test_example(run, same):
    _, rows = run(QUERY, users=users, events=events)
    want = [(1, 5, 4, 0.8), (7, 4, 2, 0.5), (30, 3, 2, 2 / 3)]
    assert same(rows, want), ("Eligible = signup date + N on or before 2025-07-15 (user 5 is not eligible for day 7, users 2 and 5 not for day 30). "
                              "Retained = a login on exactly that date.")


def test_nobody_eligible_is_null(run, same):
    u = users[users["user_id"] == 5]
    e = events[events["user_id"] == 5]
    _, rows = run(QUERY, users=u, events=e)
    assert same(rows, [(1, 1, 1, 1.0), (7, 0, 0, None), (30, 0, 0, None)]), "When no user is eligible the retention is NULL (divide by NULLIF(eligible, 0)), and the row for that N must still exist."


@pytest.mark.parametrize("seed", [41, 42, 43])
def test_random_data(run, same, data, seed):
    u, e, _o = data(seed, 90)
    _, rows = run(QUERY, users=u, events=e)
    assert same(rows, truth(u, e)), "Per N: eligible users (signup date + N <= 2025-07-15) and those with a login on that date."
