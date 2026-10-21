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
    assert run("red green blue yellow\n") == [
        "First: red", "Last: yellow", "Middle: blue", "Reversed: yellow blue green red"]


def test_odd_count():
    out = run("a b c d e\n")
    assert out[2] == "Middle: c", "With 5 words, 5 // 2 is 2, so the middle is index 2: 'c'."


def test_single_word():
    assert run("solo\n") == ["First: solo", "Last: solo", "Middle: solo", "Reversed: solo"], (
        "With one word, first, last and middle are all the same word. words[-1] still works.")


def test_extra_spaces():
    out = run("  one   two  \n")
    assert out == ["First: one", "Last: two", "Middle: two", "Reversed: two one"], (
        "Use split() with no argument so extra spaces are ignored.")


def test_no_brackets():
    out = run("x y\n")
    assert "[" not in out[3], "Join the reversed words with ' '.join(...), do not print the list."
