import pytest

from solution import worth_it


def test_weekly_report_is_worth_it():
    assert worth_it(10, 52, 180, 60) == (True, 1560), \
        "10 min x 52 runs x 3 years = 1560 saved; cost 180 + 60*3 = 360; 1560 > 720. Check the default years=3."


def test_yearly_form_is_not():
    assert worth_it(5, 1, 120, 60) == (False, 15), "5 x 1 x 3 = 15 minutes saved against a cost of 300: not worth it."


def test_years_is_used_on_both_sides():
    assert worth_it(2, 250, 90, 60, years=2) == (True, 1000), "Daily 2-minute task over 2 years: saved 1000, cost 210."
    assert worth_it(10, 10, 100, 100, years=1) == (False, 100), \
        "Over 1 year: saved 100, cost 100 + 100*1 = 200. Did you forget to multiply maintenance by the years?"


def test_break_even_is_not_worth_it():
    assert worth_it(10, 10, 150, 0) == (False, 300), "300 saved, cost 150: exactly 2 x cost. Use a strict '>', a tie is not worth it."
    assert worth_it(10, 10, 149, 0) == (True, 300), "One minute cheaper to build tips the balance."


def test_zero_runs():
    assert worth_it(10, 0, 0, 0) == (False, 0), "Zero runs save nothing; 0 > 0 is False."


def test_returns_a_real_bool():
    worth, saved = worth_it(10, 52, 180, 60)
    assert worth is True and isinstance(saved, int), "Return a bool and the minutes saved, as a tuple."


@pytest.mark.parametrize("args", [(-1, 52, 180, 60), (10, -52, 180, 60), (10, 52, -1, 60), (10, 52, 180, -5)])
def test_negative_inputs_raise(args):
    with pytest.raises(ValueError):
        worth_it(*args)


def test_years_must_be_at_least_one():
    with pytest.raises(ValueError):
        worth_it(10, 52, 180, 60, years=0)
