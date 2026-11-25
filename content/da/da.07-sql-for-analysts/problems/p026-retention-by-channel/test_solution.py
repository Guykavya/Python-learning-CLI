import pandas as pd
import pytest
from solution import QUERY

users = pd.DataFrame({
    "user_id": list(range(1, 10)),
    "signup_at": pd.to_datetime(["2025-01-05", "2025-01-20", "2025-02-03", "2025-03-15", "2025-02-10", "2025-04-02",
                                 "2025-05-30", "2025-03-03", "2025-06-10"]),
    "channel": ["ads", "ads", "ads", "ads", "organic", "organic", "organic", "referral", "ads"],
    "country": "IN"})
events = pd.DataFrame({
    "event_id": list(range(1, 11)),
    "user_id": [1, 2, 3, 3, 4, 5, 6, 8, 9, 9],
    "event_time": pd.to_datetime(["2025-02-02", "2025-01-25", "2025-03-04", "2025-02-03", "2025-05-01", "2025-03-10", "2025-05-03",
                                  "2025-04-02", "2025-07-02", "2025-06-10"]),
    "event_type": "login"})


def truth(users, events):
    login = events[events["event_type"] == "login"]
    months = set(zip(login["user_id"], login["event_time"].dt.to_period("M")))
    out = {}
    for r in users[users["signup_at"] < "2025-06-01"].itertuples():
        n, k = out.get(r.channel, (0, 0))
        out[r.channel] = (n + 1, k + ((r.user_id, r.signup_at.to_period("M") + 1) in months))
    return [(ch, n, k, (k / n) if n >= 3 else None) for ch, (n, k) in out.items()]


def test_columns(run):
    cols, _ = run(QUERY, users=users, events=events)
    assert cols == ["channel", "users", "retained_m1", "m1_retention"], "Columns: channel, users, retained_m1, m1_retention."


def test_example(run, same):
    _, rows = run(QUERY, users=users, events=events)
    want = [("ads", 4, 2, 0.5), ("organic", 3, 2, 2 / 3), ("referral", 1, 1, None)]
    assert same(rows, want), ("Measure cohorts Jan-May only (user 9 is June: left out). ads: users 1 and 3 retained = 2 of 4. "
                              "organic: users 5 (login 10 Mar) and 6 (login 3 May) are retained, user 7 is not: 2 of 3. referral has 1 user: rate NULL, counts shown.")


def test_exactly_three_is_enough(run):
    _, rows = run(QUERY, users=users, events=events)
    organic = [r for r in rows if r[0] == "organic"][0]
    assert organic[1] == 3 and organic[3] is not None, "A channel with exactly 3 measured users is large enough: the rule is 'fewer than 3'."


@pytest.mark.parametrize("seed", [44, 45, 46])
def test_random_data(run, same, data, seed):
    u, e, _o = data(seed, 70)
    _, rows = run(QUERY, users=u, events=e)
    assert same(rows, truth(u, e)), "Per channel: measured users (signup before June), those with a login in the next calendar month, NULL rate if < 3."
