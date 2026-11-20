import pathlib
import random
import subprocess
import sys

from solution import find_max_form

HERE = pathlib.Path(__file__).parent


def brute(strs, m, n):
    """Try every subset (only for short lists)."""
    best = 0
    k = len(strs)
    for mask in range(1 << k):
        zeros = ones = size = 0
        for i in range(k):
            if mask >> i & 1:
                zeros += strs[i].count("0")
                ones += strs[i].count("1")
                size += 1
        if zeros <= m and ones <= n and size > best:
            best = size
    return best


def table(strs, m, n):
    f = [[0] * (n + 1) for _ in range(m + 1)]
    for s in strs:
        z, o = s.count("0"), s.count("1")
        for i in range(m, z - 1, -1):
            for j in range(n, o - 1, -1):
                f[i][j] = max(f[i][j], f[i - z][j - o] + 1)
    return f[m][n]


def test_examples():
    assert find_max_form(["10", "0001", "111001", "1", "0"], 5, 3) == 4, (
        'Expected 4: "10", "0001", "1", "0" use 5 zeros and 3 ones.')
    assert find_max_form(["10", "0", "1"], 1, 1) == 2, 'Expected 2: "0" and "1".'
    assert find_max_form(["0", "0", "1", "1"], 2, 2) == 4, "All four fit: 2 zeros and 2 ones."


def test_each_string_once():
    assert find_max_form(["0"], 3, 0) == 1, (
        'There is only one string "0". If you got 3, a capacity loop goes upwards and the same string '
        "is taken again. Both loops must go from high to low.")
    assert find_max_form(["11"], 0, 6) == 1, (
        'One string "11" (no zeros). Got more than 1? The ones loop goes upwards.')


def test_two_separate_budgets():
    assert find_max_form(["00", "000"], 1, 10) == 0, (
        "Both strings need at least 2 zeros, and only 1 is allowed. The ones budget cannot be used for zeros.")
    assert find_max_form(["1", "1", "0"], 0, 0) == 0, "Budgets of 0: nothing fits."
    assert find_max_form(["01"], 1, 1) == 1, "One zero and one one: fits exactly."


def test_greedy_shortest_first_is_wrong():
    assert find_max_form(["00", "01", "01"], 2, 2) == 2, (
        'Expected 2 ("01" and "01"). Taking "00" first uses both zeros and leaves room for nothing else. '
        "Do not choose greedily; take or leave each string in the table.")


def test_random_against_brute_force():
    rng = random.Random(44)
    for _ in range(300):
        strs = ["".join(rng.choice("01") for _ in range(rng.randint(1, 4)))
                for _ in range(rng.randint(1, 9))]
        m = rng.randint(0, 6)
        n = rng.randint(0, 6)
        want = brute(strs, m, n)
        got = find_max_form(list(strs), m, n)
        assert got == want, (
            f"strs={strs}, m={m}, n={n}: expected {want} (tried every subset), got {got}. "
            "Each string is worth 1 and weighs (zeros, ones); both loops go downwards.")


def test_big_input_is_fast():
    rng = random.Random(4444)
    strs = ["".join(rng.choice("0011") if k % 2 else rng.choice("01") for _ in range(rng.randint(1, 10)))
            for k in range(300)]
    want = table(strs, 60, 60)
    code = (
        "from solution import find_max_form\n"
        f"print(find_max_form({strs!r}, 60, 60))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on 300 strings with m = n = 60. Trying every subset is 2**300: exponential: "
        "add a memo, or fill the (m + 1) x (n + 1) table.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == [str(want)], f"Large input: expected {want}, got {r.stdout.split()}."
