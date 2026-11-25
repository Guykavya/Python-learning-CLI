import pandas as pd
import pytest
from solution import QUERY

users = pd.DataFrame({
    "user_id": [1, 2, 3, 4, 5, 6],
    "signup_at": pd.to_datetime(["2025-01-03", "2025-01-10", "2025-02-02", "2025-02-14", "2025-03-05", "2025-03-09"]),
    "channel": ["organic", "ads", "ads", "referral", "organic", "ads"],
    "country": ["IN", "IN", "US", "UK", "US", "IN"]})
events = pd.DataFrame({
    "event_id": [1, 2, 3, 4, 5, 6, 7, 8],
    "user_id": [1, 1, 2, 3, 3, 4, 5, 1],
    "event_time": pd.to_datetime(["2025-01-03 10:00", "2025-01-04 09:00", "2025-01-10 12:00", "2025-02-02 08:00",
                                  "2025-02-03 08:00", "2025-02-14 09:00", "2025-03-05 11:00", "2025-03-01 10:00"]),
    "event_type": ["view_course", "purchase", "view_course", "view_course", "purchase", "purchase", "login", "purchase"]})


def truth(users, events):
    buyers = set(events.loc[events["event_type"] == "purchase", "user_id"])
    out = []
    for ch, g in users.groupby("channel"):
        b = int(g["user_id"].isin(buyers).sum())
        out.append((ch, len(g), b, b / len(g)))
    return out


def test_columns(run):
    cols, _ = run(QUERY, users=users, events=events)
    assert cols == ["channel", "users", "buyers", "purchase_rate"], "Columns must be channel, users, buyers, purchase_rate, in that order."


def test_example(run, same):
    _, rows = run(QUERY, users=users, events=events)
    want = [("ads", 3, 1, 1 / 3), ("organic", 2, 1, 0.5), ("referral", 1, 1, 1.0)]
    assert len(rows) == 3, "One row per channel."
    assert same(rows, want), "Count users and buyers as DISTINCT users: user 1 bought twice and is still one buyer."


def test_user_without_events_counts(run, same):
    u = users.copy()
    u.loc[len(u)] = [7, pd.Timestamp("2025-03-20"), "referral", "IN"]   # user 7 has no events at all
    _, rows = run(QUERY, users=u, events=events)
    assert same(rows, [("ads", 3, 1, 1 / 3), ("organic", 2, 1, 0.5), ("referral", 2, 1, 0.5)]), \
        "A user with no events still counts in `users`: use a LEFT JOIN from users (an INNER JOIN drops them)."


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_random_data(run, same, data, seed):
    u, e, _o = data(seed, 40)
    _, rows = run(QUERY, users=u, events=e)
    assert same(rows, truth(u, e)), "Compare with a one-row-per-user view: the counts must be users, not events."
