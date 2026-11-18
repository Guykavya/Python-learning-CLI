import random
from itertools import permutations

from solution import reconstruct_queue


def counts_ok(queue):
    """True if every (h, k) has exactly k people of height >= h in front of it."""
    for i, (h, k) in enumerate(queue):
        if sum(1 for j in range(i) if queue[j][0] >= h) != k:
            return False
    return True


def brute(people):
    for p in permutations(people):
        if counts_ok(p):
            return list(p)
    return None


def make_input(rng, n, max_h):
    queue = [rng.randint(1, max_h) for _ in range(n)]
    people = [(h, sum(1 for j in range(i) if queue[j] >= h)) for i, h in enumerate(queue)]
    shuffled = list(people)
    rng.shuffle(shuffled)
    return people, shuffled


def as_tuples(out):
    return [tuple(p) for p in out]


def test_example():
    people = [(7, 0), (4, 4), (7, 1), (5, 0), (6, 1), (5, 2)]
    want = [(5, 0), (7, 0), (5, 2), (6, 1), (4, 4), (7, 1)]
    got = as_tuples(reconstruct_queue(people))
    assert got == want, (
        f"Expected {want}, got {got}. Sort by height DESCENDING (equal heights by k ascending) and insert each "
        "person at index k.")


def test_equal_heights_order():
    people = [(5, 2), (5, 0), (5, 1)]
    got = as_tuples(reconstruct_queue(people))
    assert got == [(5, 0), (5, 1), (5, 2)], (
        f"Three people of height 5: equal heights COUNT (>=), so the queue is (5,0), (5,1), (5,2); got {got}. "
        "For equal heights, insert in increasing k.")


def test_empty_and_one():
    assert list(reconstruct_queue([])) == [], "No people: an empty queue."
    assert as_tuples(reconstruct_queue([(3, 0)])) == [(3, 0)], "One person: (3, 0)."


def test_lists_as_input_tuples_as_output():
    people = [[3, 2], [6, 0], [1, 4], [5, 0], [2, 2], [4, 0]]
    copy = [list(p) for p in people]
    out = reconstruct_queue(people)
    assert all(isinstance(p, tuple) for p in out), "Return (h, k) tuples, even when the input holds lists."
    assert list(out) == [(4, 0), (5, 0), (2, 2), (3, 2), (1, 4), (6, 0)], f"Wrong queue: {out}."
    assert people == copy, "Do not change the caller's list (use sorted(...), not people.sort())."


def test_random_against_permutations():
    rng = random.Random(30)
    for _ in range(200):
        people, shuffled = make_input(rng, rng.randint(1, 6), 4)
        want = brute(shuffled)
        got = as_tuples(reconstruct_queue(list(shuffled)))
        assert got == want, (
            f"people={shuffled}: expected {want} (found by trying every order), got {got}. Tallest first, "
            "equal heights by k ascending, insert at index k.")


def test_random_larger():
    rng = random.Random(3030)
    for n in (50, 300, 2000):
        people, shuffled = make_input(rng, n, 40)
        got = as_tuples(reconstruct_queue(shuffled))
        assert got == people, f"n={n}: the queue does not match the original (a k count is wrong somewhere)."
