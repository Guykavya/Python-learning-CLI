import pandas as pd
import pandera.pandas as pa

from solution import SCHEMA

IDX = [10, 11, 12, 13]


def users(**changes):
    d = pd.DataFrame({
        "user_id": [1, 2, 3, 4],
        "signup": pd.to_datetime(["2025-01-01", "2025-03-10", "2025-05-01", "2025-06-01"]),
        "last_seen": pd.to_datetime(["2025-02-01", "2025-03-10", "2025-05-20", "2025-06-30"]),
        "age": [20, 40, 35, 29],
        "student": [True, False, False, True],
    }, index=IDX)
    for k, v in changes.items():
        d[k] = v
    return d


def failing_rows(df):
    try:
        SCHEMA.validate(df, lazy=True)
    except pa.errors.SchemaErrors as e:
        return sorted(set(e.failure_cases["index"].dropna()))
    return []


def test_good_table_passes():
    assert failing_rows(users()) == [], (
        "row 11 was last seen the same day it signed up (fine); row 12 is a 35-year-old NON-student (fine); row 13 is a "
        "29-year-old student (fine). Failing rows: %s." % failing_rows(users()))


def test_last_seen_before_signup():
    d = users(last_seen=pd.to_datetime(["2025-02-01", "2025-03-09", "2025-05-20", "2025-06-30"]))
    assert failing_rows(d) == [11], "row 11 was last seen one day before it signed up. Reported rows: %s." % failing_rows(d)


def test_student_over_thirty():
    d = users(age=[20, 40, 35, 31])
    assert failing_rows(d) == [13], (
        "only the student of 31 (row 13) breaks the rule; the non-students of 40 and 35 are fine ('if student then age < 30'). "
        "Reported rows: %s." % failing_rows(d))


def test_both_rules_in_different_rows():
    d = users(signup=pd.to_datetime(["2025-01-01", "2025-03-10", "2025-07-01", "2025-06-01"]), age=[45, 40, 35, 29])
    assert failing_rows(d) == [10, 12], (
        "row 10 is a student of 45; row 12 signed up (July) after it was last seen (May). Reported rows: %s." % failing_rows(d))


def test_one_row_breaking_both_rules_is_reported_once():
    d = users(last_seen=pd.to_datetime(["2024-12-01", "2025-03-10", "2025-05-20", "2025-06-30"]), age=[45, 40, 35, 29])
    assert failing_rows(d) == [10], "row 10 breaks both rules; it is one row. Reported rows: %s." % failing_rows(d)


def test_column_rules_still_work():
    assert failing_rows(users(age=[20, 40, 35, 12])) == [13], "age 12 is below 13: the column rule must still fire."
    assert failing_rows(users(user_id=[1, 2, 2, 4])) == [11, 12], "duplicate user_id: both copies are reported."
