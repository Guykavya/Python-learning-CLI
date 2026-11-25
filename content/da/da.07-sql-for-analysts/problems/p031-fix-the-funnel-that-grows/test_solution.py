import pandas as pd
import pytest
from solution import QUERY

users = pd.DataFrame({
    "user_id": [1, 2, 3, 4, 5],
    "signup_at": pd.to_datetime(["2025-03-01"] * 5),
    "channel": ["organic", "ads", "ads", "referral", "organic"],
    "country": ["IN", "IN", "US", "UK", "US"]})
events = pd.DataFrame({
    "event_id": list(range(1, 15)),
    "user_id": [1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 5, 1, 2],
    "event_time": pd.to_datetime(["2025-03-02 10:00", "2025-03-02 10:05", "2025-03-02 11:00", "2025-03-02 12:00", "2025-03-02 12:30",
                                  "2025-03-03 10:00", "2025-03-03 11:00", "2025-03-03 12:00", "2025-03-04 10:00", "2025-03-04 10:30",
                                  "2025-03-05 10:00", "2025-03-06 10:00", "2025-04-02 12:30", "2025-04-03 12:00"]),
    "event_type": ["view_course", "view_course", "add_to_cart", "checkout_start", "purchase", "view_course", "add_to_cart", "checkout_start",
                   "view_course", "add_to_cart", "view_course", "view_course", "purchase", "purchase"]})
orders = pd.DataFrame({
    "order_id": [9001, 9002, 9003],
    "user_id": [1, 1, 2],
    "order_time": pd.to_datetime(["2025-03-02 12:30", "2025-04-02 12:30", "2025-04-03 12:00"]),
    "plan": ["monthly", "monthly", "monthly"],
    "amount": [499, 499, 499]})

STEPS = ["view_course", "add_to_cart", "checkout_start", "purchase"]


def truth(events):
    return [(i + 1, s, int(events.loc[events["event_type"] == s, "user_id"].nunique())) for i, s in enumerate(STEPS)]


def test_columns(run):
    cols, _ = run(QUERY, users=users, events=events, orders=orders)
    assert cols == ["step", "name", "users"], "Keep the columns step, name, users."


def test_example(run, same):
    _, rows = run(QUERY, users=users, events=events, orders=orders)
    assert same(rows, [(1, "view_course", 5), (2, "add_to_cart", 3), (3, "checkout_start", 2), (4, "purchase", 2)]), \
        "Distinct users per step: 5 viewers, 3 with a cart, 2 with checkout, 2 purchasers. Do not count rows and do not multiply rows with the orders join."


def test_funnel_never_grows(run):
    _, rows = run(QUERY, users=users, events=events, orders=orders)
    counts = [r[2] for r in sorted(rows)]
    assert counts == sorted(counts, reverse=True), f"Each step must be at most the previous one; you have {counts}. A funnel that grows is a fan-out bug."


def test_counts_are_users_not_rows(run):
    _, rows = run(QUERY, users=users, events=events, orders=orders)
    assert max(r[2] for r in rows) <= len(users), "No step can have more users than there are users (5): you are counting rows."


@pytest.mark.parametrize("seed", [58, 59])
def test_random_data(run, same, data, seed):
    u, e, o = data(seed, 60)
    _, rows = run(QUERY, users=u, events=e, orders=o)
    assert same(rows, truth(e)), "Distinct users with an event of each type, computed on events alone."
