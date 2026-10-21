import subprocess
import sys
from pathlib import Path

import pytest

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or a loop that does far more work than needed.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

def ask(values, timeout=10):
    return run(f"{len(values)}\n" + " ".join(map(str, values)) + "\n", timeout=timeout)


def expected_for(values):
    d = len(set(values))
    return [f"served {len(values)}", f"new users {d}", f"repeat visits {len(values) - d}"]


@pytest.mark.parametrize("values, why", [
    ([5, 3, 5, 5, 9, 3], "the example"),
    ([42], "a single visit"),
    ([7, 7, 7, 7], "one user visiting four times: 1 new user, 3 repeats"),
    ([1, 2, 3, 4], "all different: no repeats"),
])
def test_examples(values, why):
    got = ask(values)
    assert got == expected_for(values), (
        f"Log {values}: expected {expected_for(values)}, got {got} ({why}). The output format must stay exactly the same.")


def test_large_few_users():
    values = [1 + (i * 31) % 10 for i in range(300000)]      # only 10 different users
    got = ask(values, timeout=6)
    assert got == expected_for(values), (
        "300000 visits by only 10 users: wrong output or too slow. With 10 users, `user in seen` is cheap, so "
        "the slow part here is `queue.pop(0)`: removing the FIRST item shifts all the remaining items one place "
        "left, O(n) each time. Loop over the list instead of emptying it from the front.")


def test_large_all_different():
    values = [(i * 7919) % 1000003 + 1 for i in range(100000)]   # 100000 different users
    got = ask(values, timeout=6)
    assert got == expected_for(values), (
        "100000 different users: wrong output or too slow. Here `user in seen` scans a list that grows to "
        "100000 items. Store the users you have seen in a set.")
