import struct
import sys

from solution import capacity, copy_cost, growth_points

# No test uses a fixed size or a fixed growth point: those differ between versions and platforms.


def measured_points(n):
    """Ground truth, measured the same way on whatever Python runs the tests."""
    lst, prev, points = [], sys.getsizeof([]), []
    for _ in range(n):
        lst.append(0)
        size = sys.getsizeof(lst)
        if size != prev:
            points.append(len(lst))
            prev = size
    return points


def test_zero_appends():
    assert growth_points(0) == [], "With no appends the size never changes: return an empty list."


def test_matches_measurement():
    got = growth_points(500)
    assert got == measured_points(500), (
        "The points must be the lengths right after each append that changed sys.getsizeof(lst). "
        "Compare with the PREVIOUS size, starting from the size of the empty list."
    )


def test_strictly_increasing_and_in_range():
    points = growth_points(1000)
    assert points, "A list that grows to 1000 items must have reallocated at least once."
    assert all(a < b for a, b in zip(points, points[1:])), "Lengths only grow: the points must be strictly increasing."
    assert 1 <= points[0] <= 8 and points[-1] <= 1000, (
        "Points are lengths between 1 and n, and the first allocation happens within the first few appends."
    )


def test_far_fewer_reallocations_than_appends():
    points = growth_points(1000)
    assert len(points) < 500, (
        f"{len(points)} size changes for 1000 appends. If you record every append, you are not "
        "comparing sizes: the list over-allocates, so most appends do not change getsizeof."
    )


def test_reallocations_grow_logarithmically():
    small, big = len(growth_points(1000)), len(growth_points(100_000))
    assert big < 4 * small, (
        f"100x more appends gave {big} vs {small} reallocations. Growth is proportional to the size, "
        "so the count grows like log(n), not like n."
    )


def test_gaps_get_wider():
    points = growth_points(100_000)
    first_gap = points[1] - points[0]
    last_gap = points[-1] - points[-2]
    assert last_gap > first_gap, (
        "The spare room is proportional to the list size, so later gaps between reallocations are wider."
    )


def test_copy_cost_follows_the_model():
    for n in (0, 10, 1000):
        expected = sum(p - 1 for p in growth_points(n))
        assert copy_cost(n) == expected, f"copy_cost({n}) must be the sum of (p - 1) over the growth points."


def test_copy_cost_is_amortised_constant():
    per_item_small = copy_cost(1000) / 1000
    per_item_big = copy_cost(100_000) / 100_000
    assert per_item_big < 20, (
        f"{per_item_big:.1f} copies per append: over-allocation should keep this a small constant."
    )
    assert per_item_big < 3 * per_item_small + 1, (
        "Copies per append must stay about the same as n grows (amortised O(1)), not grow with n."
    )


def test_capacity_of_empty_list():
    assert capacity([]) == 0, "An empty list has no slot block, so its capacity is 0."


def test_capacity_formula():
    lst = list(range(37))
    expected = (sys.getsizeof(lst) - sys.getsizeof([])) // struct.calcsize("P")
    assert capacity(lst) == expected, (
        "capacity = (getsizeof(lst) - getsizeof([])) // struct.calcsize('P'): extra bytes / pointer size."
    )


def test_capacity_never_below_length_and_has_spare_room():
    lst, spare_seen = [], False
    for i in range(200):
        lst.append(i)
        cap = capacity(lst)
        assert cap >= len(lst), f"Capacity {cap} < length {len(lst)}: a list cannot hold more items than slots."
        spare_seen = spare_seen or cap > len(lst)
    assert spare_seen, "After appends the list should have spare slots sometimes. Are you returning len(lst)?"
