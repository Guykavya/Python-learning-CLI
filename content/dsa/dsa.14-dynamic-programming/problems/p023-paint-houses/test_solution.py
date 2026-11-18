import itertools
import pathlib
import random
import subprocess
import sys

from solution import min_paint_cost

HERE = pathlib.Path(__file__).parent


def brute(costs):
    """Every colouring with no equal neighbours (3**n of them; small n only)."""
    best = None
    for colours in itertools.product(range(3), repeat=len(costs)):
        if any(colours[i] == colours[i + 1] for i in range(len(colours) - 1)):
            continue
        total = sum(costs[i][colours[i]] for i in range(len(costs)))
        if best is None or total < best:
            best = total
    return best if best is not None else 0


def run_big(code, timeout=10):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=timeout, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_examples():
    assert min_paint_cost([[17, 2, 17], [16, 16, 5], [14, 3, 19]]) == 10, "Expected 10: green 2, blue 5, green 3."
    assert min_paint_cost([[1, 2, 100], [1, 100, 100]]) == 3, (
        "Expected 3: house 0 takes colour 1 (2) so house 1 can take colour 0 (1). Picking the cheapest colour "
        "house by house gives 1 + 100. Keep the best cost for EACH colour of the last house.")


def test_small_edges():
    assert min_paint_cost([]) == 0, "No houses cost nothing."
    assert min_paint_cost([[7, 6, 2]]) == 2, "One house: its cheapest colour."
    assert min_paint_cost([[5, 1, 9], [5, 1, 9]]) == 6, (
        "Expected 6 (5 + 1 or 1 + 5). Two neighbours may not both take colour 1: 1 + 1 = 2 is not allowed.")


def test_random_against_brute_force():
    rng = random.Random(23)
    for _ in range(300):
        costs = [[rng.randint(0, 20) for _ in range(3)] for _ in range(rng.randint(0, 7))]
        want = brute(costs)
        got = min_paint_cost([row[:] for row in costs])
        assert got == want, (
            f"costs={costs}: expected {want}, got {got}. f[i][c] = costs[i][c] + min of f[i-1] over the OTHER "
            "two colours; the answer is the min over the three colours of the last house.")


def test_big_needs_memo_or_table():
    rng = random.Random(2023)
    costs = [[rng.randint(0, 1000) for _ in range(3)] for _ in range(400)]
    code = (
        "from solution import min_paint_cost\n"
        f"costs = {costs!r}\n"
        "print(min_paint_cost(costs))\n"
        "print(min_paint_cost([[1, 1, 1]] * 400))\n"
    )
    r = run_big(code)
    assert r is not None, (
        "Time limit (10 s) on 400 houses. exponential: add a memo. A recursion that tries every colour for every "
        "house is 3 * 2**399 colourings; the table has only 400 * 3 states.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    red, green, blue = costs[0]
    for c0, c1, c2 in costs[1:]:
        red, green, blue = c0 + min(green, blue), c1 + min(red, blue), c2 + min(red, green)
    want = [str(min(red, green, blue)), "400"]
    assert r.stdout.split() == want, f"Large inputs: expected {want}, got {r.stdout.split()}."
