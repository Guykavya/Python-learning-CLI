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
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or a loop that does far more work than needed.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]


def lines(*nums):
    return "".join(f"{x}\n" for x in nums)


def test_example():
    got = run(lines(42, 50, 0, 25, 42))
    exp = ["lower", "out of range", "higher", "correct in 3 guesses"]
    assert got == exp, f"Secret 42, guesses 50 0 25 42.\nExpected: {exp}\nGot: {got}"


def test_first_guess_correct_with_extra_lines():
    got = run(lines(7, 7, 100, 3))
    assert got == ["correct in 1 guesses"], (
        f"The first guess is correct, so print only 'correct in 1 guesses' and stop. Got {got}. "
        "If you see more lines, you did not stop reading after the correct guess.")


def test_out_of_range_not_counted():
    got = run(lines(10, 0, -5, 101, 1000, 10))
    exp = ["out of range"] * 4 + ["correct in 1 guesses"]
    assert got == exp, (
        f"0, -5, 101 and 1000 are out of range and must not be counted.\nExpected: {exp}\nGot: {got}")


def test_boundaries_are_valid():
    got = run(lines(100, 1, 100))
    exp = ["higher", "correct in 2 guesses"]
    assert got == exp, (
        f"1 and 100 are valid guesses (in range).\nExpected: {exp}\nGot: {got}")
    got = run(lines(1, 100, 1, 50))
    exp = ["lower", "correct in 2 guesses"]
    assert got == exp, f"Secret 1, guesses 100 then 1.\nExpected: {exp}\nGot: {got}"


def test_binary_search_style():
    got = run(lines(73, 50, 75, 62, 68, 71, 73, 99, 1))
    exp = ["higher", "lower", "higher", "higher", "higher", "correct in 6 guesses"]
    assert got == exp, f"Secret 73.\nExpected: {exp}\nGot: {got}"


def test_extra_lines_ignored():
    got = run(lines(30, 20, 30, 40, 0, 30))
    exp = ["higher", "correct in 2 guesses"]
    assert got == exp, (
        f"Stop after the correct guess and ignore the lines after it.\nExpected: {exp}\nGot: {got}")


def test_many_guesses():
    guesses = [1] * 300 + [500] * 10 + [99] * 200 + [64]
    got = run(lines(64, *guesses))
    exp = ["higher"] * 300 + ["out of range"] * 10 + ["lower"] * 200 + ["correct in 501 guesses"]
    assert got == exp, (
        f"300 low guesses, 10 out of range, 200 high, then correct. Expected last line {exp[-1]!r}, "
        f"got {got[-1] if got else 'nothing'!r} ({len(got)} lines in total, expected {len(exp)}).")
