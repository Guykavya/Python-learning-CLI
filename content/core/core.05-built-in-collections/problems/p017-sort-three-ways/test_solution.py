import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program did not finish within {timeout} seconds. Look for an infinite loop, "
            "an input() that waits for more lines than the test gives, or a slow step such as "
            "`in` on a long list inside a loop (use a set or dict instead).") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]


def test_example():
    assert run("pear Fig apple kiwi date\n") == [
        "Plain: Fig apple date kiwi pear",
        "Ignoring case: apple date Fig kiwi pear",
        "By length: Fig pear kiwi date apple",
        "Longest first: apple pear kiwi date Fig"]


def test_ties_keep_input_order_when_reversed():
    out = run("bb aa cc d\n")
    assert out[3] == "Longest first: bb aa cc d", (
        "With reverse=True, tied words keep input order. Reversing the shortest-first list "
        "would give 'cc aa bb', which is wrong.")


def test_case_ties():
    out = run("b B a A\n")
    assert out[1] == "Ignoring case: a A b B", (
        "With key=str.lower, 'a' and 'A' tie, so they keep input order.")
    assert out[0] == "Plain: A B a b", "Uppercase letters sort before lowercase ones."


def test_single_word():
    assert run("x\n") == ["Plain: x", "Ignoring case: x", "By length: x", "Longest first: x"]
