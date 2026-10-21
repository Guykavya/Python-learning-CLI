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
    assert run("a b c d e f g\n") == [
        "Even positions: a c e g", "Odd positions: b d f", "Reversed: g f e d c b a",
        "Last three: e f g", "Without ends: b c d e f"]


def test_one_word():
    assert run("solo\n") == [
        "Even positions: solo", "Odd positions:", "Reversed: solo",
        "Last three: solo", "Without ends:"], (
        "With one word, the odd slice and words[1:-1] are empty. Slices never raise errors.")


def test_two_words():
    out = run("x y\n")
    assert out[3] == "Last three: x y", "words[-3:] on a 2-word list gives both words."
    assert out[4] == "Without ends:", "With two words there is nothing between the ends."


def test_last_three_includes_last():
    out = run("1 2 3 4 5\n")
    assert out[3] == "Last three: 3 4 5", "Use words[-3:]. words[-3:-1] would miss the last word."
