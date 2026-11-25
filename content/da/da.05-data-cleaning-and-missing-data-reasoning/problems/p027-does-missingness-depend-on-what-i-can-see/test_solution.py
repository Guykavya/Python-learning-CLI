import math

import numpy as np
import pandas as pd
import pytest

from conftest import hide_income, make_population
from solution import missingness_gap


def test_worked_example():
    df = pd.DataFrame({"income": [10.0, np.nan, 30.0, np.nan, 50.0], "age": [25, 22, 40, 24, 45]})
    out = missingness_gap(df, "income", "age")
    assert set(out) == {"missing_mean", "present_mean", "gap"}, "the dict needs the keys missing_mean, present_mean, gap."
    assert out["missing_mean"] == pytest.approx(23.0), "mean age of the rows where income is missing: (22 + 24) / 2."
    assert out["present_mean"] == pytest.approx(110 / 3), "mean age of the rows where income is present: (25 + 40 + 45) / 3."
    assert out["gap"] == pytest.approx(23.0 - 110 / 3), "gap = missing_mean - present_mean (the sign matters)."


def test_empty_group_gives_nan():
    df = pd.DataFrame({"income": [1.0, 2.0], "age": [30, 40]})
    out = missingness_gap(df, "income", "age")
    assert math.isnan(out["missing_mean"]) and math.isnan(out["gap"]), "nothing is missing: the missing group is empty, so its mean is NaN."
    assert out["present_mean"] == pytest.approx(35.0)


def test_input_not_changed():
    df = pd.DataFrame({"income": [1.0, np.nan], "age": [30, 40]})
    before = df.copy()
    missingness_gap(df, "income", "age")
    pd.testing.assert_frame_equal(df, before, obj="the input frame")


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_mar_data_has_a_clear_gap_in_the_column_that_drives_it(seed):
    pop = make_population(6000, seed)
    d = hide_income(pop, "MAR", 0.25, seed + 100)
    age = missingness_gap(d, "income", "age")
    assert age["gap"] < -3.0, (
        "incomes of the under-40s were hidden twice as often, so the people with a missing income are younger: the age "
        "gap is about -5 years. Got %.2f. Is the gap missing minus present?" % age["gap"])
    edu = missingness_gap(d, "income", "edu_years")
    assert abs(edu["gap"]) < 0.5, (
        "education had nothing to do with the hiding, so its gap must be near zero (got %.2f). A big gap in every "
        "column would mean a bug (for example comparing against the wrong rows)." % edu["gap"])


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_mcar_data_has_no_clear_gap(seed):
    pop = make_population(6000, seed)
    d = hide_income(pop, "MCAR", 0.25, seed + 100)
    for other in ["age", "edu_years"]:
        g = missingness_gap(d, "income", other)["gap"]
        limit = 1.5 if other == "age" else 0.5
        assert abs(g) < limit, "a coin flip hides people of every age and education alike: the %s gap must be near 0 (got %.2f)." % (other, g)
