import random

import pytest

from solution import trap


def slow(height):
    total = 0
    for i, h in enumerate(height):
        level = min(max(height[:i + 1]), max(height[i:]))
        total += level - h
    return total


@pytest.mark.parametrize("height, want, why", [
    ([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1], 6, "the classic example"),
    ([4, 2, 0, 3, 2, 5], 9, "a pool with steps inside"),
    ([3, 0, 3], 3, "one simple pool"),
    ([1, 2, 3], 0, "rising: water runs off the left edge (no left wall)"),
    ([3, 2, 1], 0, "falling: water runs off the right edge"),
    ([], 0, "no bars"),
    ([5], 0, "one bar"),
    ([2, 2, 2, 2], 0, "flat: nothing to hold water"),
    ([5, 0, 0, 0, 5], 15, "a wide flat pool: width 3, depth 5"),
    ([5, 4, 3, 2, 1, 2, 3, 4, 5], 16, "a V shape: layer by layer"),
    ([2, 0, 5], 2, "the lower wall decides the level: min(2, 5)"),
    ([0, 3, 0, 1, 0, 3, 0], 8, "edges with height 0 hold nothing"),
])
def test_cases(height, want, why):
    got = trap(list(height))
    assert got == want, f"trap({height}) should be {want}, got {got}: {why}."


def test_random_against_formula():
    rng = random.Random(35)
    for _ in range(1000):
        h = [rng.randint(0, 6) for _ in range(rng.randint(0, 12))]
        assert trap(list(h)) == slow(h), f"trap({h}) should be {slow(h)}."


def test_big():
    h = [10000] + [0] * 99998 + [10000]
    assert trap(h) == 10000 * 99998, "A pool 99,998 bars wide and 10,000 deep."
    h = [i % 100 for i in range(100000)]
    assert trap(h) == 4950 * 999, (
        "100,000 bars in a saw-tooth 0, 1, ..., 99, 0, 1, ...: each of the 999 pools after the first peak holds 4950.")
