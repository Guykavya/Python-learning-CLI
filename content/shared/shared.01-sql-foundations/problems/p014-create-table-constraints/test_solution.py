import sqlite3
import pytest
from solution import SCRIPT


def fresh():
    con = sqlite3.connect(":memory:")
    try:
        con.executescript(SCRIPT)
    except sqlite3.Error as e:
        pytest.fail(f"SQLite rejected your SCRIPT: {e}")
    return con


def accepts(con, sql, params=()):
    try:
        con.execute(sql, params)
        return True
    except sqlite3.IntegrityError:
        return False
    except sqlite3.Error as e:
        pytest.fail(f"SQLite rejected the test INSERT (is the table/column named correctly?): {e}")


INS = "INSERT INTO members (email, name, age, plan) VALUES (?, ?, ?, ?)"


def test_table_and_columns_exist():
    con = fresh()
    info = con.execute("PRAGMA table_info(members)").fetchall()
    assert [r[1] for r in info] == ["member_id", "email", "name", "age", "plan"], \
        "Table members needs the columns member_id, email, name, age, plan, in this order."
    pk = [r[1] for r in info if r[5]]
    assert pk == ["member_id"], "member_id must be the PRIMARY KEY."


def test_good_rows_accepted():
    con = fresh()
    assert accepts(con, INS, ("a@x.com", "Asha", 30, "pro")), "A fully valid row was rejected."
    assert accepts(con, INS, ("b@x.com", "Ben", None, "free")), "age is optional: a NULL age must be accepted."
    assert accepts(con, INS, ("c@x.com", "Chen", 13, "free")), "age 13 is allowed (at least 13)."


def test_email_required_and_unique():
    con = fresh()
    assert not accepts(con, INS, (None, "No Email", 20, "free")), "email must be NOT NULL."
    assert accepts(con, INS, ("a@x.com", "Asha", 30, "free"))
    assert not accepts(con, INS, ("a@x.com", "Other", 40, "free")), "Two members may not share an email: add UNIQUE."


def test_name_required():
    con = fresh()
    assert not accepts(con, INS, ("n@x.com", None, 20, "free")), "name must be NOT NULL."


def test_age_check():
    con = fresh()
    assert not accepts(con, INS, ("k@x.com", "Kid", 12, "free")), "age 12 must be rejected: CHECK (age >= 13)."
    assert not accepts(con, INS, ("k2@x.com", "Neg", -5, "free")), "A negative age must be rejected."


def test_plan_check_and_default():
    con = fresh()
    assert not accepts(con, INS, ("g@x.com", "Gold", 20, "gold")), "plan must be 'free' or 'pro': add a CHECK with IN."
    assert not accepts(con, INS, ("n@x.com", "Nul", 20, None)), "plan is NOT NULL."
    con.execute("INSERT INTO members (email, name) VALUES ('d@x.com', 'Default')")
    assert con.execute("SELECT plan FROM members WHERE email = 'd@x.com'").fetchone() == ("free",), \
        "When plan is not given, it must default to 'free'. Add DEFAULT 'free'."


def test_member_id_autofills():
    con = fresh()
    con.execute("INSERT INTO members (email, name) VALUES ('p@x.com', 'P')")
    con.execute("INSERT INTO members (email, name) VALUES ('q@x.com', 'Q')")
    ids = [r[0] for r in con.execute("SELECT member_id FROM members ORDER BY member_id")]
    assert ids == [1, 2], "INTEGER PRIMARY KEY gives ids 1, 2 automatically."
