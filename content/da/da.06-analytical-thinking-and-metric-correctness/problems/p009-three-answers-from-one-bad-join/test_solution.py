import pandas as pd

from solution import correct_totals


def joined():
    jobs = pd.DataFrame({
        "job_id": [1, 2, 3, 4],
        "quote_total": [1000, 400, 700, 300],       # sum 2400
    })
    items = pd.DataFrame({
        "job_id": [1, 1, 1, 2, 3, 3],               # job 1 has 3 lines, job 2 one, job 3 two; job 4 has none
        "line_no": [1, 2, 3, 1, 1, 2],
    })
    return jobs.merge(items, on="job_id", how="left")      # 7 rows: 6 lines plus one empty row for job 4


def test_the_joined_table_really_is_fanned_out():
    j = joined()
    assert len(j) == 7 and int(j["quote_total"].sum()) == 5100, "test data check: 7 rows and a naive sum of 5100."


def test_jobs_are_counted_distinct():
    got = correct_totals(joined())["jobs"]
    assert got == 4, "there are 4 jobs; len() gives 7 rows. Count distinct job_id. Got %s." % got


def test_job_value_is_summed_once_per_job():
    got = correct_totals(joined())["job_value"]
    assert got == 2400, ("quote_total belongs to the JOB, so take one row per job before summing: 1000+400+700+300 = 2400. "
                         "Got %s (5100 means every line repeated the quote)." % got)


def test_items_do_not_count_the_empty_row_of_a_job_without_lines():
    got = correct_totals(joined())["items"]
    assert got == 6, ("there are 6 real line items. Job 4 has no line, its row has line_no missing: count the non-missing "
                      "line_no, not the rows. Got %s." % got)


def test_all_values_are_plain_ints():
    got = correct_totals(joined())
    assert all(type(v) is int for v in got.values()), "return plain ints: wrap numpy results in int(...)."


def test_input_is_not_changed():
    j = joined()
    before = j.copy()
    correct_totals(j)
    pd.testing.assert_frame_equal(j, before)
