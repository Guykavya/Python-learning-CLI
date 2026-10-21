import os
import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines.

    Spaces at the end of each line are ignored, and so are blank lines at the very end.
    """
    r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin, capture_output=True,
                       text=True, encoding="utf-8", timeout=10,
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    lines = [line.rstrip() for line in r.stdout.split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return lines


def row(label, value):
    return f"{label:<16}{value:>10}"


def test_example():
    assert run("The quick brown fox jumps over the lazy dog!\nTHE\n") == [
        "Text statistics",
        "==========================",
        "Characters              44",
        "Non-space               36",
        "Words                    9",
        "Average length        3.89",
        "Longest word         quick",
        "Target word            the",
        "Target count             2",
        "Target share         22.2%",
    ], "Compare your report line by line: label width 16, value width 10."


def test_target_is_whole_words_only():
    out = run("There, the other theme.\nthe\n")
    assert out[8] == row("Target count", 1), (
        "Count whole words (words.count), not substrings. 'the' inside 'there' and 'other' must not count.")
    assert out[9] == row("Target share", "25.0%")


def test_punctuation_removed_before_splitting():
    out = run("Hi! Hi? hi... HI\nhi\n")
    assert out[4] == row("Words", 4), "Remove punctuation, casefold, then split() with no argument."
    assert out[8] == row("Target count", 4), "'Hi!', 'Hi?', 'hi...' and 'HI' all become 'hi'."


def test_empty_text_no_crash():
    assert run("\nword\n") == [
        "Text statistics", "=" * 26,
        row("Characters", 0), row("Non-space", 0), row("Words", 0),
        row("Average length", "0.00"), row("Longest word", "-"), row("Target word", "word"),
        row("Target count", 0), row("Target share", "0.0%"),
    ], "With no words, divide by max(len(words), 1) and use default='-' for the longest word."


def test_only_punctuation():
    out = run("... !!! ???\nx\n")
    assert out[2] == row("Characters", 11), "Characters counts the text exactly as typed, punctuation included."
    assert out[4] == row("Words", 0)
    assert out[6] == row("Longest word", "-")


def test_unicode_words():
    out = run("Café, CAFÉ et crème brûlée 🙂\ncafé\n")
    assert out[4] == row("Words", 6), "The emoji is a 'word' too: split() only splits on whitespace."
    assert out[8] == row("Target count", 2), "Casefold makes 'Café' and 'CAFÉ' equal to 'café'."
    assert out[6] == row("Longest word", "brûlée")


def test_longest_first_on_tie():
    assert run("cat dog emu\nx\n")[6] == row("Longest word", "cat"), "On a tie, the first longest word wins (max does this)."


def test_thousands_separators():
    text = " ".join(["word"] * 1500)
    out = run(text + "\nword\n")
    assert out[2] == row("Characters", "7,499"), "Counts use thousands separators: {value:>10,}."
    assert out[4] == row("Words", "1,500")
    assert out[9] == row("Target share", "100.0%")
