import pandas as pd
import pytest
from solution import QUERY

users = pd.DataFrame({
    "user_id": [1, 2, 3, 4],
    "signup_at": pd.to_datetime(["2025-01-05", "2025-01-20", "2025-02-03", "2025-06-10"]),
    "channel": ["organic", "ads", "ads", "referral"],
    "country": ["IN", "IN", "US", "UK"]})
events = pd.DataFrame({
    "event_id": list(range(1, 11)),
    "user_id": [1, 1, 1, 2, 3, 3, 3, 4, 4, 1],
    "event_time": pd.to_datetime(["2025-01-05", "2025-02-03", "2025-06-20", "2025-01-20", "2025-02-03", "2025-02-20", "2025-04-01",
                                  "2025-06-10", "2025-07-03", "2025-07-08"]),
    "event_type": "login"})


def truth(users, events):
    u = users.assign(cohort=users["signup_at"].dt.to_period("M"))
    size = u.groupby("cohort").size()
    login = events[(events["event_type"] == "login") & (events["event_time"] < "2025-07-01")]
    am = login.assign(m=login["event_time"].dt.to_period("M"))[["user_id", "m"]].drop_duplicates()
    j = am.merge(u[["user_id", "cohort"]], on="user_id")
    j["k"] = (j["m"] - j["cohort"]).apply(lambda x: x.n)
    act = j.groupby(["cohort", "k"])["user_id"].nunique()
    out = []
    for c in size.index:
        for k in range(6):
            observed = (c + k).start_time < pd.Timestamp("2025-07-01")
            a = int(act.get((c, k), 0)) if observed else None
            out.append((c.start_time.strftime("%Y-%m-%d"), k, a, int(size[c]), (a / size[c]) if observed else None))
    return out


def test_columns(run):
    cols, _ = run(QUERY, users=users, events=events)
    assert cols == ["cohort", "month_number", "active_users", "cohort_size", "retention"], \
        "Columns: cohort, month_number, active_users, cohort_size, retention."


def test_grid_size(run):
    _, rows = run(QUERY, users=users, events=events)
    assert len(rows) == 18, "3 cohorts (Jan, Feb, Jun) x month numbers 0..5 = 18 rows: build the grid first, then LEFT JOIN the counts."


def test_example(run, same):
    _, rows = run(QUERY, users=users, events=events)
    got = {(r[0], r[1]): r[2:] for r in rows}
    assert got[("2025-06-01", 0)] == (1, 1, 1.0), "June cohort, month 0: user 4 was active (the 3 July login is ignored)."
    assert got[("2025-06-01", 1)] == (None, 1, None), ("June cohort, month 1 (July) is not complete: active_users and retention must be NULL, "
                                                       "not 0. 'Zero means observed and nobody; NULL means not observed yet' (Ch. 6.4).")
    assert got[("2025-01-01", 2)] == (0, 2, 0.0), "January cohort, month 2 (March): the month is complete and nobody was active: a real 0."
    assert got[("2025-02-01", 5)] == (None, 1, None), "February cohort, month 5 is July: not complete, so NULL."
    assert same(rows, truth(users, events)), "Observed cells: distinct active users (0 allowed); other cells NULL."


def test_no_invented_zeros(run):
    _, rows = run(QUERY, users=users, events=events)
    june = [r for r in rows if r[0] == "2025-06-01" and r[1] >= 1]
    assert all(r[2] is None and r[4] is None for r in june), "The June cohort has no observed cell after month 0: no 0% allowed there."


@pytest.mark.parametrize("seed", [39, 40])
def test_random_data(run, same, data, seed):
    u, e, _o = data(seed, 80)
    _, rows = run(QUERY, users=u, events=e)
    assert same(rows, truth(u, e)), "Every (cohort, month 0..5) cell: a count if the month is complete, NULL if not."
