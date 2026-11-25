import pandas as pd
import pytest
from solution import QUERY

users = pd.DataFrame({
    "user_id": [1, 2, 3, 4, 5, 6],
    "signup_at": pd.to_datetime(["2025-01-05 10:00", "2025-01-31 23:59", "2025-02-01 00:00", "2025-02-14 09:00",
                                 "2025-02-20 18:00", "2025-04-02 12:00"]),
    "channel": ["organic", "ads", "ads", "referral", "organic", "ads"],
    "country": ["IN", "IN", "US", "UK", "US", "IN"]})
events = pd.DataFrame({
    "event_id": [1, 2, 3],
    "user_id": [1, 1, 3],
    "event_time": pd.to_datetime(["2025-01-05 10:00", "2025-02-02 09:00", "2025-02-01 00:00"]),
    "event_type": ["login", "login", "login"]})


def truth(users):
    s = users["signup_at"].dt.to_period("M").dt.start_time.dt.strftime("%Y-%m-%d")
    return [(k, int(v)) for k, v in s.value_counts().items()]


def test_columns(run):
    cols, _ = run(QUERY, users=users, events=events)
    assert cols == ["cohort", "cohort_size"], "Columns: cohort, cohort_size."


def test_example(run, same):
    _, rows = run(QUERY, users=users, events=events)
    assert same(rows, [("2025-01-01", 2), ("2025-02-01", 3), ("2025-04-01", 1)]), (
        "Cohort = month of signup. 31 Jan 23:59 and 1 Feb 00:00 are different cohorts. Users without events still count: "
        "take the sizes from users, not from a join with events.")


@pytest.mark.parametrize("seed", [34, 35])
def test_random_data(run, same, data, seed):
    u, e, _o = data(seed, 70)
    _, rows = run(QUERY, users=u, events=e)
    assert same(rows, truth(u)), "One row per signup month with the number of users."
