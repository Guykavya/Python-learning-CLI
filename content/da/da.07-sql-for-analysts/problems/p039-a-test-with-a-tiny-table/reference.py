import pandas as pd

SQL = """
WITH cohort AS (SELECT user_id, date_trunc('month', signup_at)::DATE AS cohort_month FROM users),
size AS (SELECT cohort_month, count(*) AS n FROM cohort GROUP BY 1),
act AS (SELECT DISTINCT user_id, date_trunc('month', event_time)::DATE AS m FROM events
        WHERE event_type = 'login' AND event_time < TIMESTAMP '{cutoff}'),
cnt AS (SELECT c.cohort_month, date_diff('month', c.cohort_month, a.m) AS k, count(DISTINCT c.user_id) AS active
        FROM cohort c JOIN act a USING (user_id) GROUP BY 1, 2)
SELECT cohort_month, k, active, n FROM cnt JOIN size USING (cohort_month) ORDER BY 1, 2
"""


def retention_on(con, users, events, cutoff):
    con.register("users", users)
    con.register("events", events)
    return [tuple(r) for r in con.execute(SQL.format(cutoff=cutoff)).fetchall()]


def tiny_case():
    users = pd.DataFrame({"user_id": [1, 2, 3], "signup_at": pd.to_datetime(["2025-01-05", "2025-01-20", "2025-02-02"]),
                          "channel": "ads", "country": "IN"})
    times = ["2025-01-05", "2025-01-06", "2025-03-01", "2025-02-02"]
    events = pd.DataFrame({"event_id": [1, 2, 3, 4], "user_id": [1, 1, 1, 3], "event_time": pd.to_datetime(times), "event_type": "login"})
    expected = [("2025-01-01", 0, 1, 2), ("2025-01-01", 2, 1, 2), ("2025-02-01", 0, 1, 1)]
    return users, events, expected
