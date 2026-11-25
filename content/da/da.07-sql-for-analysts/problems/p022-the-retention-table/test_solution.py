import pandas as pd
import pytest
from solution import QUERY

users = pd.DataFrame({
    "user_id": [1, 2, 3, 4],
    "signup_at": pd.to_datetime(["2025-01-05", "2025-01-20", "2025-01-25", "2025-02-02"]),
    "channel": ["organic", "ads", "ads", "referral"],
    "country": ["IN", "IN", "US", "UK"]})
events = pd.DataFrame({
    "event_id": [1, 2, 3, 4, 5, 6, 7],
    "user_id": [1, 1, 1, 2, 3, 3, 4],
    "event_time": pd.to_datetime(["2025-01-05", "2025-02-03", "2025-02-20", "2025-01-20", "2025-01-25", "2025-03-01", "2025-02-02"]),
    "event_type": "login"})


def truth(users, events):
    u = users.assign(cohort=users["signup_at"].dt.to_period("M"))
    size = u.groupby("cohort").size()
    login = events[(events["event_type"] == "login") & (events["event_time"] < "2025-07-01")]
    am = login.assign(m=login["event_time"].dt.to_period("M"))[["user_id", "m"]].drop_duplicates()
    j = am.merge(u[["user_id", "cohort"]], on="user_id")
    j["k"] = (j["m"] - j["cohort"]).apply(lambda x: x.n)
    g = j.groupby(["cohort", "k"])["user_id"].nunique().reset_index(name="active")
    return [(r.cohort.start_time.strftime("%Y-%m-%d"), int(r.k), int(r.active), int(size[r.cohort]), r.active / size[r.cohort])
            for r in g.itertuples()]


def test_columns(run):
    cols, _ = run(QUERY, users=users, events=events)
    assert cols == ["cohort", "month_number", "active_users", "cohort_size", "retention"], \
        "Columns: cohort, month_number, active_users, cohort_size, retention."


def test_example(run, same):
    _, rows = run(QUERY, users=users, events=events)
    want = [("2025-01-01", 0, 3, 3, 1.0), ("2025-01-01", 1, 1, 3, 1 / 3), ("2025-01-01", 2, 1, 3, 1 / 3), ("2025-02-01", 0, 1, 1, 1.0)]
    assert same(rows, want), ("Count DISTINCT users per cohort and month (user 1's two February logins count once); "
                              "user 3 skipped February and appears in month 2 only.")


def test_july_is_ignored(run, same):
    e = pd.concat([events, pd.DataFrame({"event_id": [8], "user_id": [1], "event_time": pd.to_datetime(["2025-07-03"]), "event_type": ["login"]})])
    _, rows = run(QUERY, users=users, events=e)
    assert not any(r[1] == 6 for r in rows), "July is not a complete month: keep only events before 2025-07-01 (a 3 July login must not create month 6)."


def test_user_without_login_counts_in_size(run, same):
    u = pd.concat([users, pd.DataFrame({"user_id": [5], "signup_at": pd.to_datetime(["2025-01-28"]), "channel": ["ads"], "country": ["IN"]})])
    _, rows = run(QUERY, users=u, events=events)
    jan0 = [r for r in rows if r[0] == "2025-01-01" and r[1] == 0][0]
    assert jan0[2] == 3 and jan0[3] == 4 and abs(jan0[4] - 0.75) < 1e-9, "User 5 never logged in: still in cohort_size (4), not in active_users (3). retention = 3/4."


@pytest.mark.parametrize("seed", [36, 37, 38])
def test_random_data(run, same, data, seed):
    u, e, _o = data(seed, 80)
    _, rows = run(QUERY, users=u, events=e)
    assert same(rows, truth(u, e)), "Compare with the pandas version: distinct active users per cohort and month number / cohort size."
