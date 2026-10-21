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
    assert run("The cat saw the other cat\n") == ["the: 2", "cat: 2", "saw: 1", "other: 1"], (
        "Lowercase every word and print in the order each word first appears.")


def test_empty():
    assert run("\n") == ["No words."], "An empty line has no words."


def test_one_word_many_times():
    assert run("go GO Go go\n") == ["go: 4"], "All case versions count as the same word."


def test_order_is_first_seen():
    assert run("b a b c a b\n") == ["b: 3", "a: 2", "c: 1"], "Do not sort; keep first-seen order."


def test_large_input_is_fast():
    words = " ".join(f"w{i % 5000}" for i in range(200000))
    out = run(words + "\n")
    assert len(out) == 5000 and out[0] == "w0: 40", (
        "Each word appears 40 times. Counting with words.count() inside a loop is O(n^2) and too "
        "slow here; use a dict.")
