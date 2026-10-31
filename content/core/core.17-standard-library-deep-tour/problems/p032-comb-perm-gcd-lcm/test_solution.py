import math

import pytest

from solution import first_common_time, handshakes, is_perfect_square, podium_orders, simplify


def test_handshakes():
    assert handshakes(2) == 1, "Two people: one handshake."
    assert handshakes(4) == 6, "Four people: 6 handshakes. Order does not matter (A-B is B-A): that is comb(n, 2)."
    assert handshakes(1) == 0 and handshakes(0) == 0, "Fewer than two people: no handshakes. math.comb gives 0."
    assert handshakes(1000) == 499500, "comb(1000, 2) = 1000 * 999 / 2."


def test_podium_orders():
    assert podium_orders(8) == 336, "8 runners, gold/silver/bronze: 8 * 7 * 6 = 336. Order matters: that is perm(n, k)."
    assert podium_orders(5, 2) == 20, "5 * 4 = 20 ordered pairs."
    assert podium_orders(2, 3) == 0, "You cannot fill 3 places with 2 runners: perm gives 0."
    assert podium_orders(10, 10) == math.factorial(10), "perm(n, n) is n!."


@pytest.mark.parametrize("num, den, expected", [
    (6, 8, (3, 4)),
    (10, 5, (2, 1)),
    (0, 7, (0, 1)),
    (3, -9, (-1, 3)),
    (-4, -6, (2, 3)),
    (-4, 6, (-2, 3)),
    (17, 13, (17, 13)),
])
def test_simplify(num, den, expected):
    assert simplify(num, den) == expected, (
        f"{num}/{den} in lowest terms is {expected[0]}/{expected[1]}: divide both by math.gcd, "
        "then move any minus sign to the numerator (the denominator is always positive)."
    )


def test_simplify_types_and_zero():
    n, d = simplify(6, 8)
    assert type(n) is int and type(d) is int, "Use // after gcd so the parts stay ints (/ would make floats)."
    with pytest.raises(ZeroDivisionError):
        simplify(1, 0)


def test_first_common_time():
    assert first_common_time([4, 6]) == 12, "Every 4 and every 6 minutes: together again at 12 (lcm), not 24 (product)."
    assert first_common_time([10, 15, 25]) == 150, "lcm(10, 15, 25) = 150."
    assert first_common_time([7]) == 7, "One bus: its own interval."
    assert first_common_time([3, 5, 7, 9]) == 315, "lcm of several numbers: math.lcm accepts any number of arguments."


def test_first_common_time_bad_input():
    with pytest.raises(ValueError):
        first_common_time([])
    with pytest.raises(ValueError):
        first_common_time([5, 0])


def test_is_perfect_square_small():
    assert [n for n in range(50) if is_perfect_square(n)] == [0, 1, 4, 9, 16, 25, 36, 49], "Squares below 50."
    assert is_perfect_square(-4) is False, "Negative numbers are never squares of integers."


def test_is_perfect_square_huge():
    k = 10**20 + 1
    assert is_perfect_square(k * k) is True, (
        "math.sqrt works with floats (about 16 digits), so int(math.sqrt(n)) is wrong for big n. "
        "math.isqrt(n) is exact for any int."
    )
    assert is_perfect_square(k * k + 1) is False, "One more than a square is not a square."
    assert is_perfect_square(k * k - 1) is False, "One less than a square is not a square."
