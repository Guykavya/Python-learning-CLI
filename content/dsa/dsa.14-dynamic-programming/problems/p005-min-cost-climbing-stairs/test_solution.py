import pathlib
import random
import subprocess
import sys

from solution import min_cost_climb

HERE = pathlib.Path(__file__).parent


def brute(cost):
    """Try every route: from stair i, pay cost[i] and move 1 or 2. Small inputs only."""
    n = len(cost)

    def from_stair(i):
        if i >= n:
            return 0
        return cost[i] + min(from_stair(i + 1), from_stair(i + 2))

    return min(from_stair(0), from_stair(1))


def run_big(code, limit):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=limit, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_chapter_examples():
    got = min_cost_climb([10, 15, 20])
    assert got != (15, [0, 0, 10, 15]), "Return only the price, not (price, table)."
    assert got == 15, (
        f"Expected 15 (start on stair 1, pay 15, jump 2 to the top), got {got}. The top is index n = len(cost), "
        "one past the last stair.")
    assert min_cost_climb([1, 100, 1, 1, 1, 100, 1, 1, 100, 1]) == 6, "Expected 6, as in chapter section 5."


def test_two_stairs():
    assert min_cost_climb([0, 0]) == 0, "Two free stairs: 0."
    assert min_cost_climb([5, 3]) == 3, (
        "[5, 3]: start on stair 1, pay 3, jump 1 to the top. Starting stairs are free: f[0] = f[1] = 0.")
    assert min_cost_climb([3, 5]) == 3, "[3, 5]: start on stair 0, pay 3, jump 2 straight to the top."


def test_top_is_past_the_last_stair():
    assert min_cost_climb([1, 1, 1000]) == 1, (
        "[1, 1, 1000]: start on 1, pay 1, jump 2 to the top (index 3). If you answered 1001 you made the last "
        "stair the goal; the goal is index len(cost).")


def test_random_against_recursion():
    rng = random.Random(55)
    for _ in range(400):
        cost = [rng.randint(0, 20) for _ in range(rng.randint(2, 14))]
        want = brute(cost)
        got = min_cost_climb(list(cost))
        assert got == want, (
            f"cost={cost}: expected {want} (all routes tried), got {got}. "
            "f(i) = min(f(i-1) + cost[i-1], f(i-2) + cost[i-2]), f(0) = f(1) = 0, answer f(n).")


def test_medium_input_is_not_exponential():
    code = (
        "from solution import min_cost_climb\n"
        "print(min_cost_climb([1, 2] * 100))\n"
    )
    r = run_big(code, 5)
    assert r is not None, (
        "Time limit (5 s) for only 200 stairs: exponential: add a memo. A recursion that tries both moves from "
        "every stair, with no notebook, makes about 1.6**200 calls.")
    assert r.returncode == 0, "Your code crashed on 200 stairs:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["100"], f"[1, 2] * 100: expected 100 (pay every 1), got {r.stdout.split()}."


def test_large_input():
    code = (
        "import random\n"
        "from solution import min_cost_climb\n"
        "rng = random.Random(505)\n"
        "a = [rng.randint(0, 999) for _ in range(10**5)]\n"
        "c = [0 if i % 3 == 0 else 1000 for i in range(99999)]\n"
        "print(min_cost_climb(a), min_cost_climb([1] * 10**5), min_cost_climb(c))\n"
    )
    r = run_big(code, 10)
    assert r is not None, (
        "Time limit (10 s) for 100,000 stairs: exponential: add a memo, or better, fill a table in one loop.")
    if "RecursionError" in r.stderr:
        assert False, "RecursionError on 100,000 stairs: replace the recursion by a table filled in a loop."
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["20573135", "50000", "33333000"], (
        f"Large inputs: expected 20573135 50000 33333000, got {r.stdout.split()}.")
