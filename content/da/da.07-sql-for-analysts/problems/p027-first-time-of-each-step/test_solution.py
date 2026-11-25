import pandas as pd
import pytest
from solution import QUERY

users = pd.DataFrame({
    "user_id": [1, 2, 3, 4, 5],
    "signup_at": pd.to_datetime(["2025-01-03", "2025-01-10", "2025-02-02", "2025-02-14", "2025-03-05"]),
    "channel": ["organic", "ads", "ads", "referral", "organic"],
    "country": ["IN", "IN", "US", "UK", "US"]})
events = pd.DataFrame({
    "event_id": list(range(1, 14)),
    "user_id": [1, 1, 1, 1, 1, 1, 2, 2, 3, 3, 4, 5, 2],
    "event_time": pd.to_datetime(["2025-01-03 10:00", "2025-01-04 09:00", "2025-01-04 09:30", "2025-01-04 10:00", "2025-01-04 10:05",
                                  "2025-01-05 08:00", "2025-01-10 12:00", "2025-01-10 12:30", "2025-02-02 08:00", "2025-02-03 08:00",
                                  "2025-02-14 09:00", "2025-03-05 11:00", "2025-01-12 12:00"]),
    "event_type": ["login", "view_course", "view_course", "add_to_cart", "checkout_start", "purchase",
                   "view_course", "add_to_cart", "view_course", "view_course", "purchase", "login", "view_course"]})

STEPS = ["view_course", "add_to_cart", "checkout_start", "purchase"]


def truth(users, events):
    out = []
    for uid in users["user_id"]:
        e = events[events["user_id"] == uid]
        row = [int(uid)]
        for s in STEPS:
            t = e.loc[e["event_type"] == s, "event_time"]
            row.append(t.min().strftime("%Y-%m-%d %H:%M:%S") if len(t) else None)
        out.append(tuple(row))
    return out


def test_columns(run):
    cols, _ = run(QUERY, users=users, events=events)
    assert cols == ["user_id", "t_view", "t_cart", "t_checkout", "t_purchase"], "Columns: user_id, t_view, t_cart, t_checkout, t_purchase."


def test_example(run, same):
    _, rows = run(QUERY, users=users, events=events)
    got = {r[0]: r[1:] for r in rows}
    assert len(rows) == 5, "One row per user: 5 users, including user 5 who only logged in."
    assert got[1] == ("2025-01-04 09:00:00", "2025-01-04 10:00:00", "2025-01-04 10:05:00", "2025-01-05 08:00:00"), \
        "User 1: the FIRST view is 09:00 (two views); every later step has its own time."
    assert got[5] == (None, None, None, None), "User 5 did no funnel step: four NULLs, but the row must exist (LEFT JOIN from users)."
    assert got[2][2] is None and got[2][3] is None, "User 2 never started checkout or purchased: NULL, not a default date."
    assert same(rows, truth(users, events)), "min(event_time) per user and step."


@pytest.mark.parametrize("seed", [47, 48])
def test_random_data(run, same, data, seed):
    u, e, _o = data(seed, 50)
    _, rows = run(QUERY, users=u, events=e)
    assert same(rows, truth(u, e)), "One row per user with the earliest time of each step (NULL if never)."
