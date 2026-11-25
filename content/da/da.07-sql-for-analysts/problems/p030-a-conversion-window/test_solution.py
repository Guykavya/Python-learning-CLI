import pandas as pd
import pytest
from solution import QUERY

users = pd.DataFrame({
    "user_id": list(range(1, 8)),
    "signup_at": pd.to_datetime(["2025-06-01"] * 7),
    "channel": ["ads", "ads", "organic", "organic", "ads", "referral", "organic"],
    "country": "IN"})
events = pd.DataFrame({
    "event_id": list(range(1, 11)),
    "user_id": [1, 1, 2, 2, 3, 4, 6, 6, 7, 7],
    "event_time": pd.to_datetime(["2025-06-01 10:00", "2025-06-08 10:00", "2025-06-01 10:00", "2025-06-09 10:00", "2025-06-02 09:00",
                                  "2025-07-10 12:00", "2025-06-01 08:00", "2025-06-05 10:00", "2025-06-03 10:00", "2025-06-04 10:00"]),
    "event_type": ["view_course", "purchase", "view_course", "purchase", "view_course", "view_course", "purchase", "view_course",
                   "view_course", "purchase"]})


def truth(events):
    elig = conv = 0
    for uid, g in events.groupby("user_id"):
        views = g.loc[g["event_type"] == "view_course", "event_time"]
        if not len(views):
            continue
        t = views.min()
        if t + pd.Timedelta(days=7) > pd.Timestamp("2025-07-15"):
            continue
        elig += 1
        p = g.loc[g["event_type"] == "purchase", "event_time"]
        conv += bool(((p >= t) & (p <= t + pd.Timedelta(days=7))).any())
    return [(elig, conv, (conv / elig) if elig else None)]


def test_columns(run):
    cols, _ = run(QUERY, users=users, events=events)
    assert cols == ["eligible_users", "converted_users", "conversion_rate"], "Columns: eligible_users, converted_users, conversion_rate."


def test_example(run, same):
    _, rows = run(QUERY, users=users, events=events)
    assert same(rows, [(5, 2, 0.4)]), ("Eligible: users 1, 2, 3, 6, 7 (user 4's window ends after 15 July). Converted: user 1 (exactly 7 days) "
                                       "and user 7 (1 day). User 2 (8 days) and user 6 (bought before viewing) did not.")


def test_exactly_seven_days_counts(run, same):
    e = events[events["user_id"] == 1]
    _, rows = run(QUERY, users=users, events=e)
    assert same(rows, [(1, 1, 1.0)]), "A purchase exactly 7 days after the first view is inside the window (<=)."


def test_nobody_eligible(run, same):
    e = events[events["user_id"] == 4]
    _, rows = run(QUERY, users=users, events=e)
    assert same(rows, [(0, 0, None)]), "With no eligible user the rate is NULL (divide by NULLIF(count, 0)), and the row still exists."


@pytest.mark.parametrize("seed", [55, 56, 57])
def test_random_data(run, same, data, seed):
    _u, e, _o = data(seed, 120)
    _, rows = run(QUERY, events=e)
    assert same(rows, truth(e)), "Eligible = a first view at least 7 days before the extraction; converted = a purchase in [first view, +7 days]."
