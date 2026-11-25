import pandas as pd
import pytest
from solution import QUERY

users = pd.DataFrame({
    "user_id": [1, 2, 3, 4, 5],
    "signup_at": pd.to_datetime(["2025-01-03", "2025-01-10", "2025-02-02", "2025-02-14", "2025-03-05"]),
    "channel": ["organic", "ads", "ads", "referral", "organic"],
    "country": ["IN", "IN", "US", "UK", "IN"]})
events = pd.DataFrame({
    "event_id": [1, 2, 3, 4, 5, 6],
    "user_id": [1, 1, 2, 3, 4, 5],
    "event_time": pd.to_datetime(["2025-01-03 10:00", "2025-01-04 09:00", "2025-01-10 12:00", "2025-02-02 08:00",
                                  "2025-02-14 09:00", "2025-03-05 11:00"]),
    "event_type": ["view_course", "purchase", "view_course", "view_course", "purchase", "login"]})


def truth(users, events):
    view = set(events.loc[events["event_type"] == "view_course", "user_id"])
    buy = set(events.loc[events["event_type"] == "purchase", "user_id"])
    out = []
    for c, g in users.groupby("country"):
        v, b = int(g["user_id"].isin(view).sum()), int(g["user_id"].isin(buy).sum())
        out.append((c, v, b, (b / v) if v else None))
    return out


def test_columns(run):
    cols, _ = run(QUERY, users=users, events=events)
    assert cols == ["country", "viewers", "buyers", "purchase_rate"], "Columns: country, viewers, buyers, purchase_rate."


def test_example(run, same):
    _, rows = run(QUERY, users=users, events=events)
    assert same(rows, [("IN", 2, 1, 0.5), ("US", 1, 0, 0.0), ("UK", 0, 1, None)]), \
        "UK has no viewers, so its rate must be NULL. Divide by NULLIF(viewers, 0); do not return inf and do not turn it into 0."


def test_no_infinity(run):
    _, rows = run(QUERY, users=users, events=events)
    for r in rows:
        assert r[3] is None or r[3] != float("inf"), "1 / 0 gives inf in DuckDB (it does not raise). Use NULLIF(denominator, 0) to get NULL."


@pytest.mark.parametrize("seed", [4, 5, 6])
def test_random_data(run, same, data, seed):
    u, e, _o = data(seed, 40)
    _, rows = run(QUERY, users=u, events=e)
    assert same(rows, truth(u, e)), "Count distinct users per country with a view, and with a purchase; divide with NULLIF."
