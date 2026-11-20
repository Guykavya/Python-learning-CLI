import pathlib
import random
import subprocess
import sys

from solution import longest_chain

HERE = pathlib.Path(__file__).parent


def brute(pairs):
    """Try every subset (small n only): sorted by start, every link must have b < c."""
    n = len(pairs)
    best = 0
    for mask in range(1 << n):
        chosen = sorted(pairs[i] for i in range(n) if mask >> i & 1)
        if all(chosen[k][1] < chosen[k + 1][0] for k in range(len(chosen) - 1)):
            best = max(best, len(chosen))
    return best


def greedy_by_end(pairs):
    """Activity selection (dsa.13), strict version: an independent oracle for big inputs."""
    count, last_end = 0, None
    for a, b in sorted(pairs, key=lambda p: p[1]):
        if last_end is None or a > last_end:
            count += 1
            last_end = b
    return count


def run_big(code, timeout=10):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=timeout, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def random_pairs(rng, n, lo, hi):
    out = []
    for _ in range(n):
        a = rng.randint(lo, hi - 1)
        out.append((a, rng.randint(a + 1, hi)))
    return out


def test_examples():
    assert longest_chain([(1, 2), (2, 3), (3, 4)]) == 2, (
        "Expected 2. Touching pairs do not chain: (1,2) -> (2,3) needs 2 < 2, which is False. Use b < c, not b <= c.")
    assert longest_chain([(5, 24), (39, 60), (15, 28), (27, 40), (50, 90)]) == 3, (
        "Expected 3: (5,24) -> (27,40) -> (50,90). The input is not sorted: sort the pairs first.")


def test_empty_and_single():
    assert longest_chain([]) == 0, "No pairs: the longest chain is empty, 0. max() of an empty list crashes."
    assert longest_chain([(3, 7)]) == 1, "One pair is a chain of length 1 (base case f[i] = 1)."


def test_earliest_start_is_not_safe():
    assert longest_chain([(1, 10), (2, 3), (4, 5)]) == 2, (
        "Expected 2: (2,3) -> (4,5). Taking the pair that starts first, (1,10), blocks both others. "
        "The DP must try every predecessor j, not only one.")


def test_duplicates():
    assert longest_chain([(1, 2), (1, 2), (3, 4), (3, 4)]) == 2, (
        "Expected 2: equal pairs cannot follow each other (2 < 1 is False). Count each link with b < c only.")


def test_negative_values():
    assert longest_chain([(-10, -5), (-4, -1), (0, 3), (-3, 2)]) == 3, (
        "Expected 3: (-10,-5) -> (-4,-1) -> (0,3). Negative numbers work like any other.")


def test_random_against_brute_force():
    rng = random.Random(22)
    for _ in range(400):
        pairs = random_pairs(rng, rng.randint(0, 9), -5, 12)
        want = brute(pairs)
        got = longest_chain(list(pairs))
        assert got == want, (
            f"pairs={pairs}: expected {want}, got {got}. Sort by first value, let f[i] be the longest chain "
            "ending with pair i, f[i] = 1 + max f[j] over j < i with pairs[j][1] < pairs[i][0], answer max(f).")


def test_big_inputs():
    rng = random.Random(2022)
    nested = [(2 * i, 2 * i + 1) for i in range(400)]
    rng.shuffle(nested)
    many = random_pairs(rng, 1500, 0, 20000)
    code = (
        "from solution import longest_chain\n"
        f"print(longest_chain({nested!r}))\n"
        f"print(longest_chain({many!r}))\n"
    )
    r = run_big(code)
    assert r is not None, (
        "Time limit (10 s) on 400 / 1500 pairs. exponential: add a memo. 'Longest chain starting at pair i' "
        "without a cache recomputes the same i many times; use the table f[i] (O(n^2)).")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    want = ["400", str(greedy_by_end(many))]
    assert r.stdout.split() == want, f"Large inputs: expected {want}, got {r.stdout.split()}."
