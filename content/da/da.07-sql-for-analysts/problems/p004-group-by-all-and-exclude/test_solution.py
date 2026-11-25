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
    m = events.merge(users, on="user_id")
    g = m.groupby(["channel", "country", "event_type"]).size().reset_index(name="events")
    return [tuple(r) for r in g.itertuples(index=False)]


def test_columns(run):
    cols, _ = run(QUERY, users=users, events=events)
    assert cols == ["channel", "country", "event_type", "events"], "Columns: channel, country, event_type, events."


def test_uses_both_features():
    text = " ".join(QUERY.upper().split())
    assert "GROUP BY ALL" in text, "Use GROUP BY ALL for the final grouping."
    assert "EXCLUDE" in text and "EVENT_ID" in text, "Use SELECT * EXCLUDE (event_id) FROM events somewhere in the query."


def test_example(run, same):
    _, rows = run(QUERY, users=users, events=events)
    assert ("organic", "IN", "purchase", 2) in [tuple(r) for r in rows], "User 1 has two purchase events: count events, not users."
    assert same(rows, truth(users, events)), "One row per (channel, country, event_type) with the number of events."


@pytest.mark.parametrize("seed", [9, 10])
def test_random_data(run, same, data, seed):
    u, e, _o = data(seed, 40)
    _, rows = run(QUERY, users=u, events=e)
    assert same(rows, truth(u, e)), "Group by the three plain columns and count events."
