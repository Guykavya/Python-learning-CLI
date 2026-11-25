import pandas as pd
import pytest
from solution import QUERY

users = pd.DataFrame({
    "user_id": [1, 2, 3, 4, 5],
    "signup_at": pd.to_datetime(["2025-01-02", "2025-01-03", "2025-02-02", "2025-03-04", "2025-01-05"]),
    "channel": "ads", "country": "IN"})
logins = {1: [1, 2, 3, 4, 5], 2: [1, 3], 3: [2, 3], 4: [3], 5: [1, 2, 5]}      # months in which each user logs in
rows = [(u, pd.Timestamp(2025, m, 10, 9)) for u, ms in logins.items() for m in ms]
events = pd.DataFrame({
    "event_id": range(1, len(rows) + 1),
    "user_id": [r[0] for r in rows], "event_time": [r[1] for r in rows], "event_type": "login"})


def truth(events):
    login = events[(events["event_type"] == "login") & (events["event_time"] < "2025-07-01")]
    am = login.assign(m=login["event_time"].dt.to_period("M"))[["user_id", "m"]].drop_duplicates()
    out = []
    for uid, g in am.groupby("user_id"):
        ms = sorted(g["m"])
        s = set(ms)
        for i, m in enumerate(ms):
            if i == 0:
                st = "new"
            elif ms[i - 1] == m - 1:
                st = "retained"
            else:
                st = "resurrected"
            out.append((int(uid), m.start_time.strftime("%Y-%m-%d"), st))
            nxt = m + 1
            if nxt.start_time < pd.Timestamp("2025-07-01") and nxt not in s:
                out.append((int(uid), nxt.start_time.strftime("%Y-%m-%d"), "churned"))
    return out


def test_columns(run):
    cols, _ = run(QUERY, users=users, events=events)
    assert cols == ["user_id", "month", "state"], "Columns: user_id, month, state."


def test_example_timeline(run, same):
    _, rows = run(QUERY, users=users, events=events)
    want = [(1, "2025-01-01", "new"), (1, "2025-02-01", "retained"), (1, "2025-03-01", "retained"), (1, "2025-04-01", "retained"),
            (1, "2025-05-01", "retained"), (1, "2025-06-01", "churned"),
            (2, "2025-01-01", "new"), (2, "2025-02-01", "churned"), (2, "2025-03-01", "resurrected"), (2, "2025-04-01", "churned"),
            (3, "2025-02-01", "new"), (3, "2025-03-01", "retained"), (3, "2025-04-01", "churned"),
            (4, "2025-03-01", "new"), (4, "2025-04-01", "churned"),
            (5, "2025-01-01", "new"), (5, "2025-02-01", "retained"), (5, "2025-03-01", "churned"), (5, "2025-05-01", "resurrected"),
            (5, "2025-06-01", "churned")]
    assert same(rows, want), ("Hand timeline: user 2 (Jan, Mar) is new, churned, resurrected, churned; user 5 (Jan, Feb, May) churns in March only "
                              "(not again in April) and is resurrected in May; users active in May get a churned row in June.")


def test_identities(run):
    _, rows = run(QUERY, users=users, events=events)
    by = {}
    for _u, m, s in rows:
        by.setdefault(m, {}).setdefault(s, 0)
        by[m][s] += 1
    months = sorted(by)
    mau = {m: sum(by[m].get(s, 0) for s in ("new", "retained", "resurrected")) for m in months}
    for prev, m in zip(months, months[1:]):
        assert mau[prev] == by[m].get("retained", 0) + by[m].get("churned", 0), f"MAU({prev}) must equal retained + churned in {m}."


@pytest.mark.parametrize("seed", [60, 61])
def test_random_data(run, same, data, seed):
    _u, e, _o = data(seed, 40)
    _, rows = run(QUERY, events=e)
    assert same(rows, truth(e)), "Label every active month with new / retained / resurrected, and the first absent complete month with churned."
