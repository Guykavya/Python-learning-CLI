import pytest

from conftest import make_wages
from solution import fit_wages


def param(res, level):
    names = [n for n in res.params.index if f"[T.{level}]" in n and "education" in n]
    assert len(names) == 1, f"expected exactly one education coefficient for '{level}', found {names}. Is `school` the baseline?"
    return names[0]


@pytest.mark.parametrize("seed", [11, 12, 13])
def test_education_effects_are_relative_to_school(seed):
    res = fit_wages(make_wages(1500, seed))
    assert not any("[T.school]" in n for n in res.params.index), "school must be the baseline, so it has no coefficient of its own."
    assert res.params[param(res, "degree")] == pytest.approx(0.18, abs=0.06), "degree vs school should be about 0.18 on the log scale. Did you model log(wage)?"
    assert res.params[param(res, "masters")] == pytest.approx(0.55, abs=0.08), "masters vs school should be about 0.55: 0.40 at zero experience plus the average growth (0.01 * mean experience of about 15) that the missing interaction pushes into this coefficient."


def test_experience_slope_is_on_the_log_scale():
    res = fit_wages(make_wages(1500, 11))
    assert res.params["experience"] == pytest.approx(0.027, abs=0.006), "experience should add about 2.5% per year on log(wage)."


def test_city_has_two_dummies():
    res = fit_wages(make_wages(1500, 11))
    city = [n for n in res.params.index if "city" in n]
    assert len(city) == 2, f"3 cities need 2 dummies, found {city}."


def test_response_is_log_wage():
    res = fit_wages(make_wages(1500, 11))
    assert "log(wage)" in res.model.endog_names, f"the response should be np.log(wage), got {res.model.endog_names}."
