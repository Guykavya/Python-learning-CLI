import ast
from functools import partial
from pathlib import Path

import pytest

import solution
from solution import checkout, flat_off, no_discount, percent_off


def test_no_discount_is_the_default():
    assert checkout([10, 20, 5.5]) == 35.5, "With no strategy given, checkout returns the plain sum."
    assert checkout([]) == 0, "An empty basket costs 0."
    assert no_discount(42) == 42, "no_discount(total) returns the total unchanged."


def test_percent_off():
    assert checkout([100, 100], percent_off(10)) == 180.0, "10% off 200 is 180."
    assert checkout([19.99], strategy=percent_off(15)) == 16.99, (
        "15% off 19.99 is 16.9915, which checkout must round to 2 decimals (16.99)."
    )
    assert percent_off(50)(10) == pytest.approx(5), "percent_off(50) must be a function: total in, total out."
    assert percent_off(0)(10) == pytest.approx(10), "0% off changes nothing."


def test_flat_off_never_goes_negative():
    assert checkout([30, 20], flat_off(5)) == 45, "5 off 50 is 45."
    assert checkout([3], flat_off(5)) == 0, "A flat discount larger than the total must stop at 0, not -2."
    assert flat_off(5)(100) == 95, "flat_off(5) must be a function: total in, total out."


def test_strategies_are_independent_closures():
    ten, twenty = percent_off(10), percent_off(20)
    assert ten(100) == pytest.approx(90) and twenty(100) == pytest.approx(80), (
        "Two strategies made by the same factory must keep their own number (each closes over its own p)."
    )


def test_any_callable_works():
    assert checkout([10, 10], lambda t: t / 2) == 10, "A lambda is a valid strategy."

    def bulk(total, threshold, rate):
        return total * rate if total >= threshold else total

    assert checkout([40, 60], partial(bulk, threshold=100, rate=0.9)) == 90, (
        "functools.partial objects are callables too: checkout must just call strategy(total)."
    )
    assert checkout([40, 50], partial(bulk, threshold=100, rate=0.9)) == 90, "Below the threshold: no discount."


def test_strategy_called_once_with_the_total():
    seen = []

    def spy(total):
        seen.append(total)
        return total

    checkout([1, 2, 3], spy)
    assert seen == [6], f"The strategy must be called exactly once with the sum of the items, got calls {seen}."


def test_checkout_has_no_branching_on_names():
    tree = ast.parse(Path(solution.__file__).read_text())
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "checkout")
    strings = [n for n in ast.walk(fn) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    ifs = [n for n in ast.walk(fn) if isinstance(n, ast.If)]
    assert not ifs and not strings, (
        "checkout must not choose a discount with if/elif on names. Call the strategy function you were given."
    )
