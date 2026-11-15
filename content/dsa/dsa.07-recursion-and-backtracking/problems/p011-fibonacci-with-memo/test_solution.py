import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent


def slow_fib_values(count):
    a, b = 0, 1
    out = []
    for _ in range(count):
        out.append(a)
        a, b = b, a + b
    return out


def run_fib(n, timeout=10):
    code = f"from solution import fib\nprint(fib({n}))\n"
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"fib({n}) took more than {timeout} seconds. Without a memo the same sub-problems are re-computed "
            "again and again (about 1.6^n calls). Store each answer in a dictionary and look it up first.") from None
    assert r.returncode == 0, f"fib({n}) crashed:\n{r.stderr[-800:]}"
    return int(r.stdout.strip())


def test_small_values():
    from solution import fib
    want = slow_fib_values(21)
    got = [fib(i) for i in range(21)]
    assert got == want, f"fib(0..20) should be {want}, got {got}. Check the base cases fib(0) = 0 and fib(1) = 1."


def test_any_order():
    from solution import fib
    assert fib(30) == 832040, "fib(30) is 832040."
    assert fib(5) == 5, "fib(5) after fib(30) must still be 5: the memo must store the right value for every n."
    assert fib(31) == 1346269, "fib(31) is 1346269."


def test_fib_300_is_fast():
    want = slow_fib_values(301)[300]
    assert run_fib(300) == want, "fib(300) has the wrong value."


def test_fib_500():
    want = slow_fib_values(501)[500]
    assert run_fib(500) == want, "fib(500) is wrong or crashed. The depth is about 500, which is fine with a memo."
