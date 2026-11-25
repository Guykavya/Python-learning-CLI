import pandas as pd
import pytest
from solution import QUERY

events = pd.DataFrame({
    "event_id": [1, 2, 3, 4, 5, 6, 7],
    "user_id": [1, 1, 1, 2, 2, 3, 3],
    "event_time": pd.to_datetime(["2025-03-01 10:00", "2025-03-02 09:00", "2025-03-02 09:00", "2025-03-01 08:00",
                                  "2025-03-05 12:30", "2025-03-06 07:00", "2025-03-04 22:00"]),
    "event_type": ["login", "view_course", "add_to_cart", "login", "purchase", "login", "view_course"]})


def truth(events):
    e = events.sort_values(["user_id", "event_time", "event_id"]).drop_duplicates("user_id", keep="last")
    return [(int(r.event_id), int(r.user_id), r.event_time.strftime("%Y-%m-%d %H:%M:%S"), r.event_type) for r in e.itertuples()]


def test_columns(run):
    cols, _ = run(QUERY, events=events)
    assert cols == ["event_id", "user_id", "event_time", "event_type"], "Return the four columns of events, in their original order."


def test_example(run, same):
    _, rows = run(QUERY, events=events)
    want = [(3, 1, "2025-03-02 09:00:00", "add_to_cart"), (5, 2, "2025-03-05 12:30:00", "purchase"),
            (6, 3, "2025-03-06 07:00:00", "login")]
    assert len(rows) == 3, "Exactly one row per user: a tie in event_time must still give one row."
    assert same(rows, want), "Latest = largest event_time, then largest event_id. User 1's tied events 2 and 3 -> 3; user 3 -> event 6 (time beats id)."


@pytest.mark.parametrize("seed", [21, 22, 23])
def test_random_data(run, same, data, seed):
    _u, e, _o = data(seed, 50)
    _, rows = run(QUERY, events=e)
    assert same(rows, truth(e)), "Number each user's rows from newest to oldest with a tie-break and keep number 1."
