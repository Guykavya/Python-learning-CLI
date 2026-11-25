import pandas as pd
import pytest
from solution import QUERY

events = pd.DataFrame({
    "event_id": [1, 2, 3, 4, 5, 6, 7, 8],
    "user_id": [1, 1, 1, 1, 1, 2, 3, 3],
    "event_time": pd.to_datetime(["2025-03-01 10:00", "2025-03-01 10:20", "2025-03-01 10:50", "2025-03-01 11:30",
                                  "2025-03-01 11:35", "2025-03-01 12:00", "2025-03-01 09:00", "2025-03-02 09:00"]),
    "event_type": ["login", "view_course", "add_to_cart", "view_course", "checkout_start", "login", "login", "login"]})


def truth(events):
    e = events.sort_values(["user_id", "event_time", "event_id"]).copy()
    gap = e.groupby("user_id")["event_time"].diff()
    e["new"] = (gap.isna() | (gap > pd.Timedelta(minutes=30))).astype(int)
    e["sess"] = e.groupby("user_id")["new"].cumsum()
    length = e.groupby(["user_id", "sess"])["event_time"].agg(lambda s: (s.max() - s.min()).total_seconds() / 60)
    out = length.groupby("user_id").agg(["size", "mean"])
    return [(int(u), int(r["size"]), float(r["mean"])) for u, r in out.iterrows()]


def test_columns(run):
    cols, _ = run(QUERY, events=events)
    assert cols == ["user_id", "sessions", "avg_session_minutes"], "Columns: user_id, sessions, avg_session_minutes."


def test_example(run, same):
    _, rows = run(QUERY, events=events)
    assert same(rows, [(1, 2, 27.5), (2, 1, 0.0), (3, 2, 0.0)]), (
        "User 1: 10:00, 10:20, 10:50 is ONE session (gaps 20 and 30; exactly 30 stays in), then 11:30 starts a new one (gap 40). "
        "Lengths 50 and 5 minutes -> 2 sessions, average 27.5.")


def test_exactly_30_minutes_stays_in_the_session(run, same):
    e = pd.DataFrame({"event_id": [1, 2], "user_id": [1, 1], "event_time": pd.to_datetime(["2025-03-01 10:00", "2025-03-01 10:30"]),
                      "event_type": ["login", "login"]})
    _, rows = run(QUERY, events=e)
    assert same(rows, [(1, 1, 30.0)]), "A gap of exactly 30 minutes is not MORE than 30: it stays in the same session."


def test_events_at_the_same_time(run, same):
    e = pd.DataFrame({"event_id": [1, 2, 3], "user_id": [1, 1, 1],
                      "event_time": pd.to_datetime(["2025-03-01 10:00", "2025-03-01 10:00", "2025-03-01 10:10"]),
                      "event_type": ["login", "view_course", "add_to_cart"]})
    _, rows = run(QUERY, events=e)
    assert same(rows, [(1, 1, 10.0)]), "Events with the same time belong to the same session: add event_id as a tie-break in the window."


@pytest.mark.parametrize("seed", [26, 27])
def test_random_data(run, same, data, seed):
    _u, e, _o = data(seed, 40)
    _, rows = run(QUERY, events=e)
    assert same(rows, truth(e)), "Flag a new session (gap > 30 min), number with a running sum, then group."
