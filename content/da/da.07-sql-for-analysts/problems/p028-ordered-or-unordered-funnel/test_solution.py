import pandas as pd
import pytest
from solution import QUERY

users = pd.DataFrame({
    "user_id": [1, 2, 3, 4, 5, 6],
    "signup_at": pd.to_datetime(["2025-03-01"] * 6),
    "channel": ["organic", "ads", "ads", "referral", "organic", "ads"],
    "country": ["IN", "IN", "US", "UK", "US", "IN"]})
events = pd.DataFrame({
    "event_id": list(range(1, 13)),
    "user_id": [1, 1, 1, 1, 2, 2, 3, 3, 4, 5, 3, 1],
    "event_time": pd.to_datetime(["2025-03-02 10:00", "2025-03-02 11:00", "2025-03-02 12:00", "2025-03-02 12:30",
                                  "2025-03-01 09:00", "2025-03-03 09:00", "2025-03-04 10:00", "2025-03-04 10:00",
                                  "2025-03-05 08:00", "2025-03-06 08:00", "2025-03-04 09:59", "2025-03-09 10:00"]),
    "event_type": ["view_course", "add_to_cart", "checkout_start", "purchase", "purchase", "view_course", "view_course", "add_to_cart",
                   "purchase", "view_course", "login", "login"]})

STEPS = ["view_course", "add_to_cart", "checkout_start", "purchase"]


def truth(users, events):
    first = {}
    for uid in users["user_id"]:
        e = events[events["user_id"] == uid]
        first[uid] = [e.loc[e["event_type"] == s, "event_time"].min() for s in STEPS]
    counts = [0, 0, 0, 0]
    for t in first.values():
        if pd.notna(t[0]):
            counts[0] += 1
            if pd.notna(t[1]) and t[1] >= t[0]:
                counts[1] += 1
                if pd.notna(t[2]) and t[2] >= t[1]:
                    counts[2] += 1
                    if pd.notna(t[3]) and t[3] >= t[2]:
                        counts[3] += 1
    return [(i + 1, STEPS[i], counts[i]) for i in range(4)]


def test_columns(run):
    cols, _ = run(QUERY, users=users, events=events)
    assert cols == ["step", "name", "users"], "Columns: step, name, users."


def test_example(run, same):
    _, rows = run(QUERY, users=users, events=events)
    want = [(1, "view_course", 4), (2, "add_to_cart", 2), (3, "checkout_start", 1), (4, "purchase", 1)]
    assert same(rows, want), ("Ordered funnel: viewers are users 1, 2, 3, 5 (4); carts on/after the view: users 1 and 3 (same moment counts) -> 2; "
                              "checkout: user 1; purchase: user 1. User 2 bought BEFORE viewing and user 4 never viewed: not in the ordered purchase step.")


def test_unordered_count_is_larger(run):
    _, rows = run(QUERY, users=users, events=events)
    assert rows and [r for r in rows if r[0] == 4][0][2] == 1, "The unordered purchase count would be 3 (users 1, 2, 4); the ordered one is 1."


@pytest.mark.parametrize("seed", [49, 50, 51])
def test_random_data(run, same, data, seed):
    u, e, _o = data(seed, 80)
    _, rows = run(QUERY, users=u, events=e)
    assert same(rows, truth(u, e)), "Each step requires the whole chain: first times on or after each other."
