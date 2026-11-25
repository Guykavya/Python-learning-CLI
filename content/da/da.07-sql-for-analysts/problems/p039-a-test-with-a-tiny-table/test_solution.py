import pandas as pd
import pytest
from solution import retention_on, tiny_case

HEAD = """
WITH cohort AS (SELECT user_id, date_trunc('month', signup_at)::DATE AS cohort_month FROM users),
size AS (SELECT cohort_month, count(*) AS n FROM cohort GROUP BY 1),
"""
TAIL = "SELECT cohort_month, k, active, n FROM cnt JOIN size USING (cohort_month) ORDER BY 1, 2"
ACT = ("act AS (SELECT DISTINCT user_id, date_trunc('month', event_time)::DATE AS m FROM events "
       "WHERE event_type = 'login' AND event_time < TIMESTAMP '{cutoff}'),\n")
CNT = ("cnt AS (SELECT c.cohort_month, date_diff('month', c.cohort_month, a.m) AS k, count(DISTINCT c.user_id) AS active "
       "FROM cohort c JOIN act a USING (user_id) GROUP BY 1, 2)\n")

CORRECT = HEAD + ACT + CNT + TAIL
# bug 1: counts login rows instead of distinct users
BUG1 = (HEAD + "act AS (SELECT user_id, date_trunc('month', event_time)::DATE AS m FROM events "
        "WHERE event_type = 'login' AND event_time < TIMESTAMP '{cutoff}'),\n"
        "cnt AS (SELECT c.cohort_month, date_diff('month', c.cohort_month, a.m) AS k, count(*) AS active "
        "FROM cohort c JOIN act a USING (user_id) GROUP BY 1, 2)\n" + TAIL)
# bug 2: k is the n-th active month of the user, not the months since signup
BUG2 = (HEAD + "base AS (SELECT DISTINCT user_id, date_trunc('month', event_time)::DATE AS m FROM events "
        "WHERE event_type = 'login' AND event_time < TIMESTAMP '{cutoff}'),\n"
        "act AS (SELECT user_id, m, row_number() OVER (PARTITION BY user_id ORDER BY m) - 1 AS k FROM base),\n"
        "cnt AS (SELECT c.cohort_month, a.k AS k, count(DISTINCT c.user_id) AS active FROM cohort c JOIN act a USING (user_id) GROUP BY 1, 2)\n" + TAIL)
# bug 3: cohort size taken from the users who were active
BUG3 = ("WITH cohort AS (SELECT user_id, date_trunc('month', signup_at)::DATE AS cohort_month FROM users),\n" + ACT + CNT.rstrip("\n") + ",\n"
        "size AS (SELECT c.cohort_month, count(DISTINCT c.user_id) AS n FROM cohort c JOIN act a USING (user_id) GROUP BY 1)\n" + TAIL)


def norm(rows):
    return [(str(r[0])[:10], int(r[1]), int(r[2]), int(r[3])) for r in rows]


def run_sql(con, sql, users, events, cutoff):
    con.register("users", users)
    con.register("events", events)
    return norm(con.execute(sql.format(cutoff=cutoff)).fetchall())


def mk(users, logins):
    u = pd.DataFrame({"user_id": [x[0] for x in users], "signup_at": pd.to_datetime([x[1] for x in users]), "channel": "ads", "country": "IN"})
    e = pd.DataFrame({"event_id": range(1, len(logins) + 1), "user_id": [x[0] for x in logins],
                      "event_time": pd.to_datetime([x[1] for x in logins]), "event_type": "login"})
    return u, e


# the chapter's table: user 1 logs in twice in February, user 3 skips February
CH_U, CH_E = mk([(1, "2025-01-05"), (2, "2025-01-20"), (3, "2025-01-25"), (4, "2025-02-02")],
                [(1, "2025-01-05"), (1, "2025-02-03"), (1, "2025-02-20"), (2, "2025-01-20"), (3, "2025-01-25"), (3, "2025-03-01"), (4, "2025-02-02")])


def test_chapter_table(con):
    got = norm(retention_on(con, CH_U, CH_E, "2025-04-01"))
    assert got == [("2025-01-01", 0, 3, 3), ("2025-01-01", 1, 1, 3), ("2025-01-01", 2, 1, 3), ("2025-02-01", 0, 1, 1)], (
        "January cohort: 3 users in month 0; month 1 only user 1 (two logins, counted once); month 2 only user 3 (skipped February). "
        "February cohort: user 4 only.")


def test_cutoff_removes_later_logins(con):
    got = norm(retention_on(con, CH_U, CH_E, "2025-03-01"))
    assert ("2025-01-01", 2, 1, 3) not in got, "The March login is on or after the cutoff 2025-03-01: it must not count."
    assert got == [("2025-01-01", 0, 3, 3), ("2025-01-01", 1, 1, 3), ("2025-02-01", 0, 1, 1)]


def test_user_without_login_counts_in_size(con):
    u, e = mk([(1, "2025-01-05"), (2, "2025-01-06")], [(1, "2025-01-05")])
    assert norm(retention_on(con, u, e, "2025-07-01")) == [("2025-01-01", 0, 1, 2)], "User 2 never logged in: still in cohort_size (2), not in active_users (1)."


def test_returns_list_of_tuples(con):
    got = retention_on(con, CH_U, CH_E, "2025-04-01")
    assert isinstance(got, list) and all(isinstance(r, tuple) for r in got), "Return a list of tuples (cohort_month, k, active_users, cohort_size)."


def test_reference_sql_in_this_file_is_right(con):
    assert run_sql(con, CORRECT, CH_U, CH_E, "2025-04-01") == norm(retention_on(con, CH_U, CH_E, "2025-04-01")), \
        "Your retention_on disagrees with the reference query of this test."


def test_tiny_case_shape():
    users, events, expected = tiny_case()
    assert len(users) <= 5 and len(events) <= 12, "A tiny table: at most 5 users and 12 events."
    assert isinstance(expected, list) and expected, "expected_rows must be a non-empty list of tuples."


def test_tiny_case_hand_count_is_right(con):
    users, events, expected = tiny_case()
    truth = run_sql(con, CORRECT, users, events, "2025-07-01")
    assert norm(expected) == truth, f"Your hand-counted expected_rows is wrong. The correct answer on your table is {truth}."
    assert norm(retention_on(con, users, events, "2025-07-01")) == norm(expected), "Your retention_on does not give your own expected_rows on your own table."


@pytest.mark.parametrize("name, bug, hint", [
    ("bug 1", BUG1, "a user who logs in more than once in the same month (login rows would be counted instead of users)"),
    ("bug 2", BUG2, "a user whose active months are not consecutive from sign-up, e.g. who skips a month (the n-th active month is not k)"),
    ("bug 3", BUG3, "a user who signs up but never logs in (cohort_size must not shrink to the active users)"),
])
def test_tiny_case_catches_the_bug(con, name, bug, hint):
    users, events, expected = tiny_case()
    broken = run_sql(con, bug, users, events, "2025-07-01")
    assert broken != norm(expected), f"Your tiny table does not catch {name}: add {hint}."
