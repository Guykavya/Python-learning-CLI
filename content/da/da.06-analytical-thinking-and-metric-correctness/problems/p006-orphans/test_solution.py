import pandas as pd

from solution import orphans


def customers():
    return pd.DataFrame({"customer_id": [1, 2, 3, 4], "city": ["Pune", "Delhi", "Pune", "Jaipur"]})     # 3 and 4 have no job


def jobs():
    return pd.DataFrame({
        "job_id": [5004, 5001, 5002, 5003, 5005, 5006],
        "customer_id": [2, 1, 1, 77, 88, None],       # 77 and 88 are not customers; 5006 has no customer at all
    })


def test_jobs_without_a_customer_sorted():
    got = orphans(jobs(), customers())["jobs_without_customer"]
    assert got == [5003, 5005, 5006], ("jobs 5003 (customer 77), 5005 (88) and 5006 (missing customer) have no customer row; "
                                       "a missing customer_id is also an orphan. Sorted by job_id. Got %s." % got)


def test_customers_without_a_job_sorted():
    got = orphans(jobs(), customers())["customers_without_job"]
    assert got == [3, 4], "customers 3 and 4 never appear in jobs. Got %s." % got


def test_ids_are_plain_python_ints():
    got = orphans(jobs(), customers())
    assert all(type(x) is int for x in got["jobs_without_customer"] + got["customers_without_job"]), (
        "return plain ints (use .tolist()), not numpy numbers or floats.")


def test_clean_tables_have_no_orphans():
    j = pd.DataFrame({"job_id": [1, 2], "customer_id": [1, 2]})
    c = pd.DataFrame({"customer_id": [1, 2]})
    assert orphans(j, c) == {"jobs_without_customer": [], "customers_without_job": []}, "no orphans on either side: two empty lists."


def test_a_customer_with_two_jobs_is_not_an_orphan_twice():
    j = pd.DataFrame({"job_id": [1, 2, 3], "customer_id": [9, 9, 1]})
    c = pd.DataFrame({"customer_id": [1]})
    got = orphans(j, c)
    assert got["jobs_without_customer"] == [1, 2], "two jobs point at the unknown customer 9: list both JOB ids, not the customer."


def test_frames_are_not_changed():
    j, c = jobs(), customers()
    j0, c0 = j.copy(), c.copy()
    orphans(j, c)
    pd.testing.assert_frame_equal(j, j0)
    pd.testing.assert_frame_equal(c, c0)
