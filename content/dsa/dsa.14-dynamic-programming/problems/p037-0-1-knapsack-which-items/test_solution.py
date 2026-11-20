import itertools
import pathlib
import random
import subprocess
import sys

from solution import pack_van

HERE = pathlib.Path(__file__).parent


def brute(wt, val, W):
    """The best value over every subset of items (small inputs only)."""
    best = 0
    n = len(wt)
    for r in range(n + 1):
        for combo in itertools.combinations(range(n), r):
            if sum(wt[i] for i in combo) <= W:
                best = max(best, sum(val[i] for i in combo))
    return best


def check(wt, val, W, result, want):
    """Validate (best, items). Returns an error message or None."""
    if not (isinstance(result, tuple) and len(result) == 2):
        return f"return a tuple (best, items); got {result!r}"
    best, items = result
    if best != want:
        return f"best should be {want}, got {best}"
    if not isinstance(items, list):
        return f"items should be a list, got {type(items).__name__}"
    if items != sorted(items):
        return f"items should be sorted, got {items} (the walk back finds them last-first: reverse the list)"
    if len(set(items)) != len(items):
        return f"items {items} repeats an index: each parcel can go only once"
    if any(not (0 <= i < len(wt)) for i in items):
        return f"items {items} has an index outside 0..{len(wt) - 1} (row i is about item i - 1)"
    weight = sum(wt[i] for i in items)
    if weight > W:
        return f"items {items} weigh {weight}, more than W = {W} (did you subtract the weight after taking one?)"
    value = sum(val[i] for i in items)
    if value != best:
        return f"items {items} are worth {value}, but you said best = {best}"
    return None


def test_examples():
    for wt, val, W, want in [([1, 3, 4, 5], [1, 4, 5, 7], 7, 9),
                             ([5, 4, 6, 3], [10, 40, 30, 50], 10, 90),
                             ([3], [5], 2, 0)]:
        error = check(wt, val, W, pack_van(wt, val, W), want)
        assert error is None, f"pack_van({wt}, {val}, {W}): {error}."


def test_empty():
    assert pack_van([], [], 5) == (0, []), "No parcels: (0, [])."
    assert pack_van([2, 3], [4, 5], 0) == (0, []), "A van with capacity 0 takes nothing: (0, [])."


def test_all_fit():
    error = check([1, 2, 3], [4, 5, 6], 10, pack_van([1, 2, 3], [4, 5, 6], 10), 15)
    assert error is None, f"Everything fits, so take all three: {error}."


def test_random_validated():
    rng = random.Random(3737)
    for _ in range(300):
        n = rng.randint(0, 8)
        wt = [rng.randint(1, 10) for _ in range(n)]
        val = [rng.randint(0, 20) for _ in range(n)]
        W = rng.randint(0, 25)
        want = brute(wt, val, W)
        error = check(wt, val, W, pack_van(list(wt), list(val), W), want)
        assert error is None, (
            f"pack_van({wt}, {val}, {W}): {error}. Walk back from f[n][W]: if f[i][w] != f[i-1][w], item i-1 "
            "was taken; record it and subtract its weight.")


def test_large_input():
    code = (
        "import random\n"
        "from solution import pack_van\n"
        "rng = random.Random(37)\n"
        "wt = [rng.randint(1, 1000) for _ in range(100)]\n"
        "val = [rng.randint(0, 10**6) for _ in range(100)]\n"
        "best, items = pack_van(wt, val, 5000)\n"
        "print(best, sum(wt[i] for i in items) <= 5000, sum(val[i] for i in items) == best,\n"
        "      len(set(items)) == len(items), items == sorted(items))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=20, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, "Time limit (20 s) for 100 parcels and W = 5000: fill the table, do not try every subset."
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["16932707", "True", "True", "True", "True"], (
        "Large input: expected best 16932707 and a valid list (fits, worth best, no repeats, sorted); "
        f"got {r.stdout.split()}.")
