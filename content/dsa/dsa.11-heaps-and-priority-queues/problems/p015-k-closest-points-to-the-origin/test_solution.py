import random

from solution import k_closest


def model(points, k):
    return sorted(points, key=lambda p: (p[0] * p[0] + p[1] * p[1], p[0], p[1]))[:max(k, 0)]


def test_the_example():
    pts = [(3, 3), (5, -1), (-2, 4), (0, 1), (-1, -1)]
    got = k_closest(pts, 2)
    assert got == [(0, 1), (-1, -1)], (
        f"Squared distances 18, 26, 20, 1, 2: the two closest are (0, 1) then (-1, -1); got {got}. Nearest first.")


def test_ties_are_decided_by_x_then_y():
    pts = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    got = k_closest(pts, 2)
    assert got == [(-1, 0), (0, -1)], f"All four are at distance 1: the order is (-1, 0), (0, -1), (0, 1), (1, 0); the first two are expected, got {got}."
    got = k_closest(pts, 3)
    assert got == [(-1, 0), (0, -1), (0, 1)], f"Expected [(-1, 0), (0, -1), (0, 1)], got {got}."
    assert k_closest(pts, 4) == [(-1, 0), (0, -1), (0, 1), (1, 0)], "k = n: all points in the fixed order."


def test_a_tie_at_the_border_keeps_the_smaller_point():
    pts = [(5, 5), (3, 4), (-3, 4), (4, 3), (0, 5), (-5, 0)]
    # squared distances: 50, 25, 25, 25, 25, 25 -> the 25s in (x, y) order: (-5,0) (-3,4) (0,5) (3,4) (4,3)
    got = k_closest(pts, 3)
    assert got == [(-5, 0), (-3, 4), (0, 5)], (
        f"Five points are at distance 5; with k = 3 the ones with the smallest (x, y) must stay: [(-5, 0), (-3, 4), (0, 5)], got {got}. "
        "Is the tie at the border decided against the right point?")
    got = k_closest(list(reversed(pts)), 3)
    assert got == [(-5, 0), (-3, 4), (0, 5)], f"The input order must not matter: expected [(-5, 0), (-3, 4), (0, 5)], got {got}."


def test_the_origin_and_duplicates():
    assert k_closest([(0, 0), (1, 1)], 1) == [(0, 0)], "The origin itself is at distance 0."
    got = k_closest([(2, 1), (2, 1), (1, 2), (0, 0)], 3)
    assert got == [(0, 0), (1, 2), (2, 1)], f"Expected [(0, 0), (1, 2), (2, 1)] ((1, 2) before (2, 1): same distance, smaller x), got {got}."
    assert k_closest([(2, 1), (2, 1), (2, 1)], 2) == [(2, 1), (2, 1)], "Every copy counts: two of the three equal points."


def test_k_zero_negative_too_large_and_empty():
    assert k_closest([(1, 1)], 0) == [], "k = 0 gives an empty list."
    assert k_closest([(1, 1)], -3) == [], "A negative k gives an empty list."
    assert k_closest([(3, 0), (1, 0)], 10) == [(1, 0), (3, 0)], "k larger than n: all points, nearest first."
    assert k_closest([], 4) == [], "No points: empty list."


def test_big_coordinates_need_exact_squared_distances():
    far_a = (10 ** 9, 0)              # squared distance 10**18
    far_b = (-10 ** 9, 1)             # squared distance 10**18 + 1: farther, but the same float after sqrt
    got = k_closest([far_b, far_a], 1)
    assert got == [far_a], (
        f"(1000000000, 0) is closer than (-1000000000, 1) by one unit of squared distance; got {got}. "
        "Do not use sqrt or hypot: the floats are equal and the tie rule picks the wrong point. Compare x*x + y*y (exact integers).")
    assert k_closest([far_a, far_b], 2) == [far_a, far_b], "Both points, the closer one first."


def test_the_input_is_not_changed():
    pts = [(3, 1), (1, 1), (2, 2), (0, 5)]
    copy = list(pts)
    k_closest(pts, 2)
    assert pts == copy, "Do not change the list you receive (no points.sort(...))."


def test_returns_tuples_in_a_list():
    got = k_closest([(2, 1), (0, 3)], 1)
    assert isinstance(got, list) and got == [(2, 1)] and isinstance(got[0], tuple), f"Return a list of (x, y) tuples, got {got!r}."


def test_random_inputs_against_a_full_sort():
    rng = random.Random(18)
    for _ in range(500):
        pts = [(rng.randint(-4, 4), rng.randint(-4, 4)) for _ in range(rng.randint(0, 25))]
        k = rng.randint(-1, 30)
        want = model(pts, k)
        got = k_closest(pts, k)
        assert got == want, f"k_closest({pts}, {k}) should be {want}, got {got}."


def test_a_hundred_thousand_points():
    rng = random.Random(19)
    pts = [(rng.randint(-10 ** 9, 10 ** 9), rng.randint(-10 ** 9, 10 ** 9)) for _ in range(100_000)]
    got = k_closest(pts, 20)
    assert got == model(pts, 20), "The 20 closest of 100,000 random points are wrong or wrongly ordered."
