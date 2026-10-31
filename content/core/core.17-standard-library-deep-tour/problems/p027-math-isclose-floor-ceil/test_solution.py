import pytest

from solution import close_enough, floor_ceil_trunc, pages_needed, round_down_to


# ------------------------------------------------------------------ floor / ceil / trunc
@pytest.mark.parametrize("x, expected", [
    (2.5, (2, 3, 2)),
    (-2.5, (-3, -2, -2)),
    (3.0, (3, 3, 3)),
    (-0.5, (-1, 0, 0)),
])
def test_floor_ceil_trunc(x, expected):
    got = floor_ceil_trunc(x)
    assert got == expected, (
        f"For {x}: floor goes DOWN (towards -infinity), ceil goes UP, trunc cuts towards 0. "
        f"They differ for negative numbers: expected {expected}, got {got}."
    )
    assert all(type(v) is int for v in got), "math.floor, math.ceil and math.trunc all return int."


# ------------------------------------------------------------------ pages_needed
def test_pages_needed_small():
    assert pages_needed(10, 3) == 4, "10 items, 3 per page: 3 full pages and 1 more page for the last item."
    assert pages_needed(9, 3) == 3, "9 items fill exactly 3 pages: do not add an empty page."
    assert pages_needed(0, 5) == 0, "No items: no pages."
    assert pages_needed(1, 50) == 1, "One item still needs one page."


def test_pages_needed_huge_numbers_are_exact():
    n = 10**17 + 1
    assert pages_needed(n, 1) == n, (
        "math.ceil(n / per_page) goes through a float, and a float cannot hold 10**17 + 1 exactly. "
        "Do ceiling division with integers only: -(-n // per_page)."
    )
    assert pages_needed(10**20 + 1, 10) == 10**19 + 1, "Integer ceiling division stays exact for any size."


def test_pages_needed_rejects_bad_input():
    with pytest.raises(ValueError):
        pages_needed(10, 0)
    with pytest.raises(ValueError):
        pages_needed(-1, 5)


# ------------------------------------------------------------------ round_down_to
@pytest.mark.parametrize("x, step, expected", [
    (7.8, 0.5, 7.5),
    (7.5, 0.5, 7.5),
    (10.0, 0.25, 10.0),
    (-2.3, 1.0, -3.0),
    (-0.1, 0.5, -0.5),
    (13.0, 5.0, 10.0),
])
def test_round_down_to(x, step, expected):
    assert round_down_to(x, step) == expected, (
        f"round_down_to({x}, {step}) is {expected}: the largest multiple of step that is <= x. "
        "For negatives int() rounds towards 0 (the wrong way); math.floor rounds down."
    )


def test_round_down_to_bad_step():
    with pytest.raises(ValueError):
        round_down_to(1.0, 0)


# ------------------------------------------------------------------ close_enough
def test_close_enough_float_error():
    assert close_enough(0.1 + 0.2, 0.3) is True, "0.1 + 0.2 is 0.30000000000000004: == fails, math.isclose succeeds."
    assert close_enough(1.0, 1.001) is False, "A difference of 0.001 is a real difference, not rounding error."


def test_close_enough_near_zero():
    assert close_enough(1e-12, 0.0) is True, (
        "math.isclose(x, 0.0) is False for every x != 0 with only rel_tol: a relative tolerance of zero is zero. "
        "Pass abs_tol=1e-9 too."
    )
    assert close_enough(1e-6, 0.0) is False, "1e-6 is much larger than abs_tol=1e-9: not close."


def test_close_enough_big_numbers():
    assert close_enough(1e10, 1e10 + 1) is True, (
        "For big numbers a relative tolerance is needed: 1 in 10**10 is within rel_tol=1e-9. "
        "A fixed abs(a - b) < 1e-9 check would say False."
    )
    assert close_enough(1e10, 1e10 + 100) is False, "100 in 10**10 is 1e-8, more than rel_tol=1e-9."
