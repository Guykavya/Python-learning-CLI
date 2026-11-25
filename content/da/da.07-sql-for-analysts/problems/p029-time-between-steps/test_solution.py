import pandas as pd
import pytest
from solution import QUERY

users = pd.DataFrame({
    "user_id": list(range(1, 10)),
    "signup_at": pd.to_datetime(["2025-03-01"] * 9),
    "channel": ["ads", "ads", "ads", "organic", "organic", "ads", "organic", "referral", "ads"],
    "country": "IN"})
events = pd.DataFrame({
    "event_id": list(range(1, 15)),
    "user_id": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 8],
    "event_time": pd.to_datetime(["2025-03-02 10:00", "2025-03-02 15:00", "2025-03-03 08:00", "2025-03-03 11:00",
                                  "2025-03-04 09:00", "2025-03-04 19:00", "2025-03-05 10:00", "2025-03-05 12:00",
                                  "2025-03-06 10:00", "2025-03-06 14:00", "2025-03-07 10:00", "2025-03-07 08:00",
                                  "2025-03-08 10:00", "2025-03-09 10:00"]),
    "event_type": ["add_to_cart", "purchase", "add_to_cart", "purchase", "add_to_cart", "purchase", "add_to_cart", "purchase",
                   "add_to_cart", "purchase", "add_to_cart", "purchase", "add_to_cart", "purchase"]})


def truth(users, events):
    out = {}
    for r in users.itertuples():
        e = events[events["user_id"] == r.user_id]
        c = e.loc[e["event_type"] == "add_to_cart", "event_time"].min()
        p = e.loc[e["event_type"] == "purchase", "event_time"].min()
        if pd.notna(c) and pd.notna(p) and p >= c:
            out.setdefault(r.channel, []).append((p - c).total_seconds() / 3600)
    return [(ch, len(v), float(pd.Series(v).median())) for ch, v in out.items()]


def test_columns(run):
    cols, _ = run(QUERY, users=users, events=events)
    assert cols == ["channel", "converters", "median_hours"], "Columns: channel, converters, median_hours."


def test_example(run, same):
    _, rows = run(QUERY, users=users, events=events)
    assert same(rows, [("ads", 3, 5.0), ("organic", 2, 3.0)]), (
        "ads: gaps 5, 3 and 10 hours -> median 5 (user 6 bought BEFORE the cart: not a converter). "
        "organic: gaps 2 and 4 hours -> median 3 (even count: average of the middle two). referral has no converter: no row.")


def test_fractional_hours(run, same):
    e = pd.DataFrame({"event_id": [1, 2], "user_id": [1, 1], "event_time": pd.to_datetime(["2025-03-02 10:59", "2025-03-02 11:01"]),
                      "event_type": ["add_to_cart", "purchase"]})
    u = users[users["user_id"] == 1]
    _, rows = run(QUERY, users=u, events=e)
    assert same(rows, [("ads", 1, 2 / 60)]), "10:59 to 11:01 is 2 minutes = 0.0333 hours: use epoch(t2 - t1) / 3600.0, not date_diff('hour', ...)."


@pytest.mark.parametrize("seed", [52, 53, 54])
def test_random_data(run, same, data, seed):
    u, e, _o = data(seed, 150)
    _, rows = run(QUERY, users=u, events=e)
    assert same(rows, truth(u, e)), "Median hours per channel among users whose first purchase is at or after their first cart."
