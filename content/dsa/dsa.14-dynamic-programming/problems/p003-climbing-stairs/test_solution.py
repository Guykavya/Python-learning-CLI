import pathlib
import subprocess
import sys

from solution import climb_stairs

HERE = pathlib.Path(__file__).parent


def brute(n):
    """Plain recursion: try a last move of 1 or 2. Fine for n <= 20."""
    if n < 0:
        return 0
    if n == 0:
        return 1
    return brute(n - 1) + brute(n - 2)


def run_big(code, limit):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=limit, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_small_examples():
    assert climb_stairs(1) == 1, "One step: only the move 1. Is f[1] = 1?"
    assert climb_stairs(2) == 2, "Two steps: 1+1 or 2. f[2] = f[1] + f[0] = 2."
    assert climb_stairs(3) == 3, "Three steps: 1+1+1, 1+2, 2+1."
    assert climb_stairs(4) == 5, "Four steps: 5 ways. The sequence is 1, 1, 2, 3, 5, 8, ..."


def test_zero_steps():
    assert climb_stairs(0) == 1, (
        "n = 0 should give 1: there is one way to stay on the ground (do nothing). "
        "Also check the table does not index f[1] when n = 0.")


def test_against_recursion():
    for n in range(0, 21):
        assert climb_stairs(n) == brute(n), (
            f"climb_stairs({n}) = {climb_stairs(n)}, but counting by recursion gives {brute(n)}. "
            "Transition: f(i) = f(i-1) + f(i-2), base f(0) = f(1) = 1.")


def test_modulo():
    assert climb_stairs(44) == 1134903170 % (10**9 + 7), (
        "climb_stairs(44) is the first value above 10**9 + 7. Return the count modulo 1_000_000_007.")


def test_large_n():
    code = (
        "from solution import climb_stairs\n"
        "print(climb_stairs(1000), climb_stairs(54321), climb_stairs(100000))\n"
    )
    r = run_big(code, 10)
    assert r is not None, (
        "Time limit (10 s) for n up to 100,000: exponential: add a memo. Better still, fill a table in a loop, "
        "and take % (10**9 + 7) inside the loop so the numbers stay small.")
    if "RecursionError" in r.stderr:
        assert False, (
            "RecursionError for large n: a recursion 100,000 deep is too deep for Python, even with a memo. "
            "Fill a table (or two variables) from small i to large i.")
    assert r.returncode == 0, "Your code crashed on large n:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["107579939", "180744523", "967618232"], (
        f"Large n: expected 107579939 180744523 967618232, got {r.stdout.split()}. "
        "Did you apply % (10**9 + 7) to every cell?")
