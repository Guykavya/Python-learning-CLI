import pytest

from conftest import make_wages
from solution import experience_slope_by_education


@pytest.mark.parametrize("seed", [11, 12, 13])
def test_slopes_by_level(seed):
    s = experience_slope_by_education(make_wages(3000, seed))
    assert set(s) == {"school", "degree", "masters"}, f"expected one slope per education level, got keys {sorted(s)}."
    assert s["school"] == pytest.approx(0.025, abs=0.005), "school slope: the plain `experience` coefficient."
    assert s["degree"] == pytest.approx(0.025, abs=0.006), "degree slope = experience + experience:degree interaction (the interaction is about 0)."
    assert s["masters"] == pytest.approx(0.035, abs=0.006), "masters slope = 0.025 + 0.01: add the interaction to the baseline slope, do not report it alone."


def test_masters_slope_is_steeper_than_school():
    s = experience_slope_by_education(make_wages(3000, 11))
    assert s["masters"] > s["school"] + 0.004, "the masters group gains more per year: its slope must be clearly larger than school's."


def test_values_are_floats():
    s = experience_slope_by_education(make_wages(1000, 11))
    assert all(isinstance(v, float) for v in s.values()), "return plain floats."
