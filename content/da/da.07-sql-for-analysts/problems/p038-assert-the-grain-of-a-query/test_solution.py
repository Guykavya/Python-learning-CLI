import pandas as pd
import pytest
from solution import assert_grain

USERS = "SELECT * FROM (VALUES (1, 'IN'), (2, 'US'), (3, 'UK')) AS t(user_id, country)"


def test_unique_key_returns_dataframe(con):
    df = assert_grain(con, USERS, ["user_id"])
    assert isinstance(df, pd.DataFrame) and len(df) == 3, "When the key is unique return the result as a DataFrame (3 rows here)."


def test_duplicate_key_raises_and_names_it(con):
    sql = "SELECT * FROM (VALUES ('zz_alpha', 1), ('zz_alpha', 2), ('zz_beta', 3)) AS t(k, v)"
    with pytest.raises(AssertionError) as e:
        assert_grain(con, sql, ["k"])
    msg = str(e.value)
    assert "duplicate" in msg.lower(), "The message must contain the word 'duplicate'."
    assert "zz_alpha" in msg, "Name the duplicated key (zz_alpha) in the message."
    assert "zz_beta" not in msg, "zz_beta is unique: do not list it as a duplicate."


def test_names_at_most_three_duplicates(con):
    vals = ", ".join(f"('zz_{i}', {j})" for i in range(1, 6) for j in range(2))
    with pytest.raises(AssertionError) as e:
        assert_grain(con, f"SELECT * FROM (VALUES {vals}) AS t(k, v)", ["k"])
    named = sum(f"zz_{i}" in str(e.value) for i in range(1, 6))
    assert 1 <= named <= 3, f"Name up to 3 duplicated keys (not all 5, not none); your message names {named}."


def test_null_key_raises(con):
    sql = "SELECT * FROM (VALUES (1, 'a'), (NULL, 'b')) AS t(id, v)"
    with pytest.raises(AssertionError) as e:
        assert_grain(con, sql, ["id"])
    assert "null" in str(e.value).lower(), "A NULL in a key column must raise an AssertionError whose message contains NULL."


def test_two_column_key(con):
    ok = "SELECT * FROM (VALUES (1, 'a'), (1, 'b'), (2, 'a')) AS t(x, y)"
    assert len(assert_grain(con, ok, ["x", "y"])) == 3, "Each column repeats but the PAIR (x, y) is unique: this is fine."
    bad = "SELECT * FROM (VALUES (1, 'a'), (1, 'a'), (2, 'a')) AS t(x, y)"
    with pytest.raises(AssertionError):
        assert_grain(con, bad, ["x", "y"])


def test_fan_out_after_left_join(con):
    users = pd.DataFrame({"user_id": [1, 2, 3]})
    orders = pd.DataFrame({"order_id": [10, 11, 12], "user_id": [1, 1, 2]})
    con.register("users", users)
    con.register("orders", orders)
    sql = "SELECT u.user_id, o.order_id FROM users u LEFT JOIN orders o USING (user_id)"
    with pytest.raises(AssertionError):
        assert_grain(con, sql, ["user_id"])
    with pytest.raises(AssertionError):
        assert_grain(con, sql, ["order_id"])      # user 3 has no order: a NULL key
