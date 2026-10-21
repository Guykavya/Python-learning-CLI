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
    assert run("listen enlist google silent tinsel elgoog cat act listen\n") == [
        "listen enlist silent tinsel", "google elgoog", "cat act"]


def test_empty():
    assert run("\n") == ["No words."]


def test_no_anagrams():
    assert run("one two three\n") == ["one", "two", "three"], "Each word is its own group."


def test_duplicates_once():
    assert run("ab ba ab ab\n") == ["ab ba"], "List each exact word only once."


def test_same_letters_different_counts():
    assert run("aab abb\n") == ["aab", "abb"], (
        "'aab' and 'abb' use the same set of letters but different counts. Sort the letters, "
        "do not use set(word).")
