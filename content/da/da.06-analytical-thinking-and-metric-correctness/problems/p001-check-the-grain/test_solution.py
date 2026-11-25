import pandas as pd
import pytest

from solution import check_grain


def jobs():
    return pd.DataFrame({
        "job_id": [5001, 5002, 5003, 5004],        # one row per job: unique
        "city": ["Pune", "Pune", "Delhi", "Delhi"],
    })


def items():
    return pd.DataFrame({
        "job_id": [5001, 5001, 5002, 5003],        # job 5001 has two lines
        "line_no": [1, 2, 1, 1],                   # (job_id, line_no) is unique, each alone is not
        "amount": [500, 300, 400, 700],
    })


def test_unique_single_key_returns_true():
    assert check_grain(jobs(), "job_id", "jobs") is True, "a unique key must make check_grain return True (the value True, not None)."


def test_unique_composite_key_returns_true():
    assert check_grain(items(), ["job_id", "line_no"], "items") is True, (
        "(job_id, line_no) is unique, so return True. Check the PAIR of columns, not each column alone.")


def test_one_column_alone_is_not_the_composite_key():
    with pytest.raises(ValueError, match="1 duplicate rows"):
        check_grain(items(), "job_id", "items")


def test_message_has_name_count_and_example():
    with pytest.raises(ValueError) as e:
        check_grain(items(), "job_id", "items")
    msg = str(e.value)
    assert "items" in msg, "the message must start with the table name, so a log says WHICH table failed."
    assert "1 duplicate rows" in msg, "the message must contain 'N duplicate rows' (here 1: job 5001 has one extra row). Got: %s" % msg
    assert "[5001]" in msg, "the message must show the repeated key values as a list, here [5001]. Got: %s" % msg


def test_duplicate_count_counts_extra_rows_not_keys():
    df = pd.DataFrame({"k": [1, 1, 1, 2, 2, 3]})      # key 1 appears 3 times (2 extra), key 2 twice (1 extra)
    with pytest.raises(ValueError) as e:
        check_grain(df, "k", "t")
    assert "3 duplicate rows" in str(e.value), (
        "count the EXTRA rows (2 for key 1, 1 for key 2 = 3), not the number of repeated keys. Got: %s" % e.value)
    assert "[1, 2]" in str(e.value), "list each repeated key once, in order of first appearance: [1, 2]. Got: %s" % e.value


def test_at_most_five_examples():
    df = pd.DataFrame({"k": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7]})
    with pytest.raises(ValueError) as e:
        check_grain(df, "k", "t")
    msg = str(e.value)
    assert "[1, 2, 3, 4, 5]" in msg, "list at most 5 repeated key values (the first five): [1, 2, 3, 4, 5]. Got: %s" % msg
    assert "6" not in msg.replace("7 duplicate", ""), "do not list more than 5 examples, a huge table would print a huge message."
    assert "7 duplicate rows" in msg, "the count must still be the full count (7 extra rows). Got: %s" % msg


def test_composite_key_examples_are_tuples():
    df = pd.DataFrame({"job_id": [1, 1, 2], "line_no": [1, 1, 1]})
    with pytest.raises(ValueError) as e:
        check_grain(df, ["job_id", "line_no"], "items")
    assert "[(1, 1)]" in str(e.value), "for a composite key show each repeated key as a tuple: [(1, 1)]. Got: %s" % e.value


def test_missing_key_is_a_failure_even_when_values_differ():
    df = pd.DataFrame({"job_id": [1, 2, None]})
    with pytest.raises(ValueError, match="missing"):
        check_grain(df, "job_id", "jobs")


def test_frame_is_not_changed():
    df = items()
    before = df.copy()
    check_grain(df, ["job_id", "line_no"], "items")
    pd.testing.assert_frame_equal(df, before)
    assert list(df.columns) == list(before.columns), "check_grain must only read the table."
