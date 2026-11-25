import pandas as pd

from solution import relationship


def customers():
    return pd.DataFrame({"customer_id": [1, 2, 3, 4], "city": ["Pune", "Delhi", "Pune", "Jaipur"]})   # customer 4 has no job


def jobs():
    return pd.DataFrame({
        "job_id": [5001, 5002, 5003, 5004, 5005],
        "customer_id": [1, 1, 2, 3, 77],           # customer 1 has two jobs; customer 77 does not exist
    })


def items():
    return pd.DataFrame({"job_id": [5001, 5001, 5002, 5003, 5099], "line_no": [1, 2, 1, 1, 1]})    # job 5099 does not exist


def test_one_to_many():
    got = relationship(customers(), jobs(), "customer_id", "customer_id")
    assert got["relationship"] == "1:m", ("customers.customer_id is unique and jobs.customer_id repeats (customer 1 has "
                                         "two jobs), so it is '1:m'. Got %r." % got["relationship"])


def test_many_to_one_is_the_reverse():
    got = relationship(jobs(), customers(), "customer_id", "customer_id")
    assert got["relationship"] == "m:1", "swap the tables and the answer swaps too: 'm:1'. Got %r." % got["relationship"]


def test_one_to_one():
    a = pd.DataFrame({"k": [1, 2, 3]})
    b = pd.DataFrame({"k": [2, 3, 4]})
    got = relationship(a, b, "k", "k")
    assert got == {"relationship": "1:1", "left_orphans": 1, "right_orphans": 1}, "both keys are unique, so '1:1'; key 1 is only left, key 4 only right. Got %s." % got


def test_many_to_many():
    a = pd.DataFrame({"job_id": [1, 1, 2]})
    b = pd.DataFrame({"job_id": [1, 2, 2]})
    assert relationship(a, b, "job_id", "job_id")["relationship"] == "m:m", (
        "both sides repeat a key, so every pair multiplies: 'm:m'.")


def test_orphans_count_rows_without_a_partner():
    got = relationship(customers(), jobs(), "customer_id", "customer_id")
    assert got["left_orphans"] == 1, "customer 4 has no job: left_orphans must be 1 (count LEFT rows without a match). Got %s." % got["left_orphans"]
    assert got["right_orphans"] == 1, "job 5005 points at customer 77 who does not exist: right_orphans must be 1. Got %s." % got["right_orphans"]


def test_orphans_count_rows_not_distinct_keys():
    got = relationship(jobs(), items(), "job_id", "job_id")
    assert got["relationship"] == "1:m"
    assert got["left_orphans"] == 2, "jobs 5004 and 5005 have no line item: 2 jobs without items. Got %s." % got["left_orphans"]
    assert got["right_orphans"] == 1, "one item row (job 5099) has no job. Got %s." % got["right_orphans"]
    two = pd.DataFrame({"k": [1, 2]})
    many = pd.DataFrame({"k": [9, 9, 9]})
    assert relationship(two, many, "k", "k")["right_orphans"] == 3, "count ROWS: three right rows with key 9 are three orphans, not one."


def test_missing_key_counts_as_orphan():
    a = pd.DataFrame({"k": [1, None, 3]})
    b = pd.DataFrame({"k": [1.0, 3.0]})
    assert relationship(a, b, "k", "k")["left_orphans"] == 1, "a row whose key is missing has no partner: count it as an orphan."


def test_frames_are_not_changed():
    c, j = customers(), jobs()
    c0, j0 = c.copy(), j.copy()
    relationship(c, j, "customer_id", "customer_id")
    pd.testing.assert_frame_equal(c, c0)
    pd.testing.assert_frame_equal(j, j0)
