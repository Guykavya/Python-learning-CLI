import pandas as pd
import pytest

from solution import avg_job_value


def customers():
    return pd.DataFrame({
        "customer_id": [1, 2, 3, 4, 5],
        "city": ["Pune", "Pune", "Delhi", "Jaipur", "Goa"],       # customer 5 (Goa) has no job: Goa must not appear
    })


def jobs():
    return pd.DataFrame({
        "job_id": [1, 2, 3, 4, 5, 6, 7],
        "customer_id": [1, 1, 2, 2, 3, 4, 4],
        "quote_total": [200, 400, 600, 800,   # Pune: 4 jobs, mean 500
                        1000,                 # Delhi: 1 job, mean 1000
                        200, 400],            # Jaipur: 2 jobs, mean 300
    })


def test_by_city_means():
    got = avg_job_value(jobs(), customers())["by_city"]
    assert got == pytest.approx({"Pune": 500.0, "Delhi": 1000.0, "Jaipur": 300.0}), (
        "per city = the mean of the quotes of the jobs of that city's customers. Goa has no job and must not appear. Got %s." % got)


def test_overall_is_total_over_jobs():
    got = avg_job_value(jobs(), customers())["overall"]
    assert got == pytest.approx(3600 / 7), (
        "overall = 3600 quoted / 7 jobs = 514.29. Got %s. 600 is the mean of the three city means: it gives Delhi's single job "
        "the same weight as Pune's four." % got)


def test_overall_is_not_the_mean_of_city_means():
    out = avg_job_value(jobs(), customers())
    mean_of_means = sum(out["by_city"].values()) / len(out["by_city"])
    assert mean_of_means == pytest.approx(600.0), "test data check: the mean of the city means is 600."
    assert out["overall"] != pytest.approx(mean_of_means), (
        "never average averages: add the quotes, add the jobs, divide once (3600 / 7, not (500+1000+300) / 3).")


def test_weighted_city_means_give_back_the_overall():
    out = avg_job_value(jobs(), customers())
    counts = {"Pune": 4, "Delhi": 1, "Jaipur": 2}
    rebuilt = sum(out["by_city"][c] * n for c, n in counts.items()) / 7
    assert rebuilt == pytest.approx(out["overall"]), "weighting each city mean by its job count must reproduce the overall mean."


def test_values_are_plain_floats():
    out = avg_job_value(jobs(), customers())
    assert type(out["overall"]) is float and all(type(v) is float for v in out["by_city"].values()), (
        "return plain floats (float(...)), not numpy numbers.")


def test_inputs_are_not_changed():
    j, c = jobs(), customers()
    j0, c0 = j.copy(), c.copy()
    avg_job_value(j, c)
    pd.testing.assert_frame_equal(j, j0)
    pd.testing.assert_frame_equal(c, c0)
