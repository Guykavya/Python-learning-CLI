import random
from itertools import combinations

from solution import min_arrows


def brute(balloons):
    """Smallest set of positions that hits every balloon. Some best answer shoots only at balloon ends."""
    if not balloons:
        return 0
    spots = sorted({e for _, e in balloons})
    for k in range(1, len(spots) + 1):
        for shots in combinations(spots, k):
            if all(any(s <= x <= e for x in shots) for s, e in balloons):
                return k
    return len(spots)


def test_chapter_examples():
    assert min_arrows([(10, 16), (2, 8), (1, 6), (7, 12)]) == 2, (
        "Arrows at 6 and 12 burst all four. Sort by END and shoot at the end of the first balloon not yet burst.")
    assert min_arrows([(1, 2), (3, 4), (5, 6), (7, 8)]) == 4, "Four separate balloons need four arrows."
    assert min_arrows([(1, 2), (2, 3), (3, 4), (4, 5)]) == 2, (
        "Balloons are CLOSED: an arrow at 2 bursts (1,2) and (2,3). Start a new arrow only when start > shot_at, "
        "not when start >= shot_at.")


def test_sort_by_end_not_start():
    assert min_arrows([(1, 10), (2, 3), (4, 5)]) == 2, (
        "If you shoot at the end of the balloon that STARTS first, (1,10), the arrow at 10 misses (2,3). "
        "Sort by end: arrows at 3 and 5.")


def test_edge_cases():
    assert min_arrows([]) == 0, "No balloons: no arrows."
    assert min_arrows([(3, 3)]) == 1, "A single balloon that is one point wide still needs one arrow."
    assert min_arrows([[-5, -1], [-1, 0], [2, 2]]) == 2, (
        "Negative positions and lists: (-5,-1) and (-1,0) touch at -1, (2,2) needs its own arrow.")
    assert min_arrows([(1, 5), (1, 5), (1, 5)]) == 1, "Three identical balloons: one arrow."


def test_input_not_changed():
    data = [(10, 16), (2, 8), (1, 6)]
    copy = list(data)
    min_arrows(data)
    assert data == copy, "Do not sort the caller's list in place; use sorted(...)."


def test_random_against_brute_force():
    rng = random.Random(6)
    for _ in range(400):
        n = rng.randint(0, 7)
        balloons = []
        for _ in range(n):
            s = rng.randint(-3, 10)
            balloons.append((s, s + rng.randint(0, 5)))
        expected = brute(balloons)
        got = min_arrows(list(balloons))
        assert got == expected, (
            f"balloons={balloons}: the fewest arrows is {expected}, you returned {got}. Sort by end, shoot at the "
            "end of the first balloon not yet hit, new arrow only when start > shot_at.")


def test_large_input_is_fast():
    balloons = [(i, i + 1) for i in range(0, 200_000, 2)]
    assert min_arrows(balloons) == 100_000, "100,000 separate balloons need 100,000 arrows; one sort and one pass."
