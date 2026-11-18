import pathlib
import random
import subprocess
import sys

from solution import max_envelopes

HERE = pathlib.Path(__file__).parent


def quadratic(envelopes):
    """O(n^2) DP with a strict check on both sides: correct whatever the tie order."""
    env = sorted(map(tuple, envelopes))
    if not env:
        return 0
    f = [1] * len(env)
    for i in range(len(env)):
        for j in range(i):
            if env[j][0] < env[i][0] and env[j][1] < env[i][1] and f[j] + 1 > f[i]:
                f[i] = f[j] + 1
    return max(f)


def test_examples():
    assert max_envelopes([(5, 4), (6, 4), (6, 7), (2, 3)]) == 3, "Expected 3: (2,3) -> (5,4) -> (6,7)."
    assert max_envelopes([(4, 5), (4, 6), (6, 7), (2, 3), (1, 1)]) == 4, (
        "Expected 4. (4, 5) and (4, 6) have the same width and cannot both be in the chain. If you got 5, "
        "sort equal widths by height DESCENDING.")


def test_equal_width_trap():
    assert max_envelopes([(3, 3), (3, 4)]) == 1, (
        "Same width: (3, 3) does not fit in (3, 4). Sorting by (width, height) and taking the LIS of heights "
        "counts 2. Use the key (width, -height).")
    assert max_envelopes([(1, 1), (1, 1), (1, 1)]) == 1, "Equal envelopes do not nest: 1."


def test_equal_height_trap():
    assert max_envelopes([(1, 2), (2, 2)]) == 1, (
        "Equal heights do not nest. If you got 2, you used bisect_right; heights must strictly increase.")


def test_empty_single_and_lists():
    assert max_envelopes([]) == 0, "No envelopes: 0."
    assert max_envelopes([(7, 7)]) == 1, "One envelope: 1."
    assert max_envelopes([[1, 1], [2, 2], [3, 3]]) == 3, "Envelopes may be given as lists: [1,1] in [2,2] in [3,3]."


def test_area_is_not_the_order():
    assert max_envelopes([(2, 9), (4, 5)]) == 1, "(2, 9) has the smaller area but is taller than (4, 5): 1."


def test_random_against_quadratic_dp():
    rng = random.Random(54)
    for _ in range(400):
        env = [(rng.randint(1, 6), rng.randint(1, 6)) for _ in range(rng.randint(0, 14))]
        want = quadratic(env)
        got = max_envelopes(list(env))
        assert got == want, (
            f"envelopes={env}: expected {want} (O(n^2) DP checking both sides), got {got}. "
            "Sort by (width, -height), then a strictly increasing LIS (bisect_left) on the heights.")


def test_big_input_is_n_log_n():
    code = (
        "import random\n"
        "from solution import max_envelopes\n"
        "rng = random.Random(5454)\n"
        "env = [(rng.randint(1, 10**5), rng.randint(1, 10**5)) for _ in range(10**5)]\n"
        "same = [(k // 10, k) for k in range(10**5)]\n"
        "print(max_envelopes(env), max_envelopes(same))\n"
    )
    from bisect import bisect_left
    rng = random.Random(5454)
    env = [(rng.randint(1, 10**5), rng.randint(1, 10**5)) for _ in range(10**5)]
    tails = []
    for _, h in sorted(env, key=lambda e: (e[0], -e[1])):
        k = bisect_left(tails, h)
        if k == len(tails):
            tails.append(h)
        else:
            tails[k] = h
    want = [len(tails), 10**4]
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on 100,000 envelopes. The O(n^2) DP is too slow; sort once, then the "
        "bisect LIS on heights.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == [str(w) for w in want], (
        f"Large inputs: expected {want}, got {r.stdout.split()}. In the second input 10 envelopes share each "
        "width, so at most one per width: 10,000.")
