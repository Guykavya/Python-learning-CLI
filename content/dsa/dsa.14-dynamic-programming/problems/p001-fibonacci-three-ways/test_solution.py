import pathlib
import subprocess
import sys

from solution import fib_memo, fib_naive, fib_table

HERE = pathlib.Path(__file__).parent


def fib_list(n):
    """F(0) .. F(n) by a simple loop (the test's oracle)."""
    values = [0, 1]
    while len(values) <= n:
        values.append(values[-1] + values[-2])
    return values[: n + 1]


def run_big(code, limit):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=limit, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_base_cases():
    for name, f in [("fib_naive", fib_naive), ("fib_memo", fib_memo), ("fib_table", fib_table)]:
        assert f(0) == 0, f"{name}(0) should be 0. The base case is F(0) = 0, not 1."
        assert f(1) == 1, f"{name}(1) should be 1. The base case is F(1) = 1."
        assert f(2) == 1, f"{name}(2) should be 1 = F(1) + F(0). Check both base cases."


def test_small_values_all_three():
    want = fib_list(25)
    for name, f in [("fib_naive", fib_naive), ("fib_memo", fib_memo), ("fib_table", fib_table)]:
        got = [f(n) for n in range(26)]
        assert got == want, (
            f"{name} for n = 0..25 gave {got[:12]}..., expected {want[:12]}.... "
            "Check the base cases (F(0) = 0, F(1) = 1) and the transition F(n) = F(n-1) + F(n-2).")


def test_memo_is_fast():
    want = fib_list(700)
    code = (
        "from solution import fib_memo\n"
        "print(fib_memo(90))\n"
        "print(fib_memo(400))\n"
        "print(fib_memo(700))\n"
    )
    r = run_big(code, 10)
    assert r is not None, (
        "fib_memo(90) did not finish in 10 s: exponential: add a memo. Each answer must be written in a "
        "notebook (dictionary or functools.cache) and looked up before recomputing.")
    assert r.returncode == 0, (
        "fib_memo crashed on n up to 700 (a memoised recursion 700 deep is allowed):\n" + r.stderr[-800:])
    got = r.stdout.split()
    assert got == [str(want[90]), str(want[400]), str(want[700])], (
        "fib_memo gave wrong values for n = 90, 400, 700. Is the notebook keyed by n alone, "
        "and is the stored value the full answer?")


def test_table_is_big_and_not_recursive():
    want = fib_list(5000)
    code = (
        "from solution import fib_table\n"
        "print(fib_table(5000))\n"
        "print(fib_table(3000))\n"
    )
    r = run_big(code, 10)
    assert r is not None, (
        "fib_table(5000) did not finish in 10 s: exponential: add a memo, or better, fill a list in a loop.")
    if "RecursionError" in r.stderr:
        assert False, (
            "fib_table(5000) raised RecursionError: the table version must not recurse at all. "
            "Fill f[0..n] with a for loop from small i to large i.")
    assert r.returncode == 0, "fib_table crashed on n = 5000:\n" + r.stderr[-800:]
    assert r.stdout.split() == [str(want[5000]), str(want[3000])], (
        "fib_table(5000) or fib_table(3000) is wrong. Is the list of size n + 1, "
        "and do you return f[n] (not f[n - 1])?")
