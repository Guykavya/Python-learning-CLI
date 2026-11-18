import pathlib
import subprocess
import sys

from solution import tribonacci

HERE = pathlib.Path(__file__).parent


def recursive(n):
    """The definition, word for word (small n only)."""
    if n == 0:
        return 0
    if n <= 2:
        return 1
    return recursive(n - 1) + recursive(n - 2) + recursive(n - 3)


def run_big(code, limit):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=limit, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_base_cases():
    assert tribonacci(0) == 0, "T(0) = 0."
    assert tribonacci(1) == 1, "T(1) = 1."
    assert tribonacci(2) == 1, "T(2) = 1 (not 2: the third start value is 1)."
    assert tribonacci(3) == 2, "T(3) = T(2) + T(1) + T(0) = 1 + 1 + 0 = 2."


def test_against_definition():
    for n in range(0, 22):
        got = tribonacci(n)
        assert got == recursive(n), (
            f"tribonacci({n}) = {got}, the definition gives {recursive(n)}. If the values are off by one "
            "position, check how many times the loop runs and which variable you return. If they are too "
            "big, you may be updating a, b, c on separate lines (each line then sees new values).")


def test_not_exponential():
    code = "from solution import tribonacci\nprint(tribonacci(37), tribonacci(60))\n"
    r = run_big(code, 5)
    assert r is not None, (
        "Time limit (5 s) for n = 60: exponential: add a memo. Three recursive calls per value is "
        "about 1.84**n calls. Rolling three variables forward is a single loop.")
    assert r.returncode == 0, "Your code crashed:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["2082876103", "2544489349890656"], (
        f"Expected T(37) = 2082876103 and T(60) = 2544489349890656, got {r.stdout.split()}.")


def test_huge_n():
    code = (
        "from solution import tribonacci\n"
        "x = tribonacci(30000)\n"
        "y = tribonacci(100000)\n"
        "print(x % 1000000007, x.bit_length(), y % 1000000007, y.bit_length())\n"
    )
    r = run_big(code, 15)
    assert r is not None, "Time limit (15 s) for n = 100,000: use one loop with three rolling variables."
    if "RecursionError" in r.stderr:
        assert False, "RecursionError for n = 30,000: no recursion here; roll three variables in a loop."
    assert r.returncode == 0, "Your code crashed for large n:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["250265748", "26373", "30627177", "87914"], (
        f"Large n: the values of T(30000) and T(100000) are wrong (got {r.stdout.split()}, as value mod "
        "10**9+7 and bit length). Return the exact integer, without any modulo.")
