import random
from itertools import product

from solution import two_colour


def possible(n, dislikes):
    return any(all(c[a] != c[b] for a, b in dislikes) for c in product((0, 1), repeat=n))


def check(n, dislikes, got, label):
    assert got is not None, f"{label}: a split exists, but you returned None."
    assert isinstance(got, list) and len(got) == n, f"{label}: return a list of length {n}, got {got!r}."
    bad = [x for x in got if x not in (0, 1)]
    assert not bad, (
        f"{label}: every group must be 0 or 1, found {bad[:3]}. People in another piece (or without any dislike) "
        "must be coloured too: start a BFS from every uncoloured person.")
    for a, b in dislikes:
        assert got[a] != got[b], (
            f"{label}: {a} and {b} dislike each other but are both in group {got[a]}. Give each neighbour the "
            "OPPOSITE group (1 - group[u]) and add every dislike in both directions.")


def test_examples():
    check(4, [(0, 1), (0, 2), (1, 3)], two_colour(4, [(0, 1), (0, 2), (1, 3)]), "example 1")
    assert two_colour(3, [(0, 1), (1, 2), (2, 0)]) is None, (
        "Three people who all dislike each other (an odd cycle): no split, return None.")
    check(3, [], two_colour(3, []), "no dislikes")


def test_pieces_and_special_pairs():
    d = [(0, 1), (3, 4), (4, 5), (5, 3)]
    assert two_colour(6, d) is None, "The triangle 3-4-5 is in another piece than 0: check every piece."
    d = [(5, 4), (3, 4), (1, 0)]
    check(6, d, two_colour(6, d), "pieces {0,1}, {3,4,5} and the lonely person 2")
    assert two_colour(3, [(1, 1)]) is None, "(1, 1): someone who dislikes themself can never be split: None."
    d = [(0, 1), (1, 0), (2, 1)]
    check(3, d, two_colour(3, d), "a pair listed in both orders")


def test_direction_does_not_matter():
    d = [(1, 0), (2, 1), (3, 2), (0, 3)]
    check(4, d, two_colour(4, d), "a square given as pairs pointing 'backwards'")


def test_random_against_brute_force():
    rng = random.Random(40)
    for _ in range(500):
        n = rng.randint(1, 9)
        d = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, n + 2))]
        if rng.random() < 0.6:
            d = [(a, b) for a, b in d if a != b]
        if rng.random() < 0.5:
            side = [rng.randint(0, 1) for _ in range(n)]
            d = [(a, b) for a, b in d if side[a] != side[b]]
        got = two_colour(n, d)
        if possible(n, d):
            check(n, d, got, f"n={n}, dislikes={d}")
        else:
            assert got is None, f"n={n}, dislikes={d}: impossible, expected None, got {got}."


def test_long_chain():
    n = 100000
    d = [(i, i + 1) for i in range(n - 1)]
    crashed = False
    try:
        got = two_colour(n, d)
        odd = two_colour(n - 1, [(i, i + 1) for i in range(n - 2)] + [(n - 2, 0)])
    except RecursionError:
        crashed = True
    assert not crashed, "RecursionError on a chain of 100,000 people: use BFS or an explicit stack."
    check(n, d, got, "chain of 100,000 people")
    assert odd is None, "A ring of 99,999 people (odd) cannot be split: None."
