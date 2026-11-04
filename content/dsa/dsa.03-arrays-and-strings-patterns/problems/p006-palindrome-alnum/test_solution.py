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

import random


def expected(s):
    c = [ch.lower() for ch in s if ch.isalnum()]
    return "yes" if c == c[::-1] else "no"


def ask(lines, timeout=10):
    return run(f"{len(lines)}\n" + "".join(line + "\n" for line in lines), timeout=timeout)


def test_example():
    lines = ["A man, a plan, a canal: Panama", "race a car", "No 'x' in Nixon", ",.!"]
    got = ask(lines)
    assert got == ["yes", "no", "yes", "yes"], f"Expected yes no yes yes for the example, got {got}."


@pytest.mark.parametrize("line, why", [
    ("abba", "a plain palindrome"),
    ("abca", "not a palindrome: b and c differ"),
    ("Aa", "case does not matter"),
    ("ab", "two different letters"),
    ("1a1", "digits count: 1a1 is a palindrome"),
    ("12", "digits count: 1 and 2 differ. If you print yes you skipped digits (isalpha instead of isalnum)"),
    ("0P", "0 and p are different: digits are not ignored"),
    ("", "an empty line reads the same both ways"),
    ("   ", "only spaces: nothing left to compare, so yes"),
    ("a.", "punctuation at the end is skipped"),
    (".,a,b.", "after cleaning, ab: no"),
    ("Was it a car or a cat I saw?", "a classic palindrome sentence"),
    ("Step on no pets!", "punctuation and spaces skipped, case ignored"),
    ("Never odd; or even.", "the semicolon and the dot must be skipped, not only spaces"),
])
def test_single(line, why):
    got = ask([line])
    assert got == [expected(line)], f"Line {line!r}: expected {expected(line)}, got {got} ({why})."


def test_random():
    rng = random.Random(8)
    lines = []
    for _ in range(60):
        half = "".join(rng.choice("abAB12 ,.") for _ in range(rng.randint(0, 6)))
        if rng.random() < 0.5:
            line = half + rng.choice(["", "x", "?"]) + half[::-1].swapcase()
        else:
            line = half + "".join(rng.choice("abc1 ,") for _ in range(rng.randint(1, 4)))
        lines.append(line)
    got = ask(lines)
    want = [expected(s) for s in lines]
    for line, g, w in zip(lines, got + [""] * len(lines), want):
        assert g == w, f"Line {line!r}: expected {w}, got {g!r}."
    assert len(got) == len(want), f"Print exactly one answer per line: expected {len(want)} lines, got {len(got)}."


def test_long_lines():
    rng = random.Random(9)
    half = "".join(rng.choice("abcXYZ019 ,;") for _ in range(100000))
    yes_line = half + half[::-1].upper()
    no_line = half + "q" + half[::-1].upper() + "Q!"
    no_line = no_line[:-3] + "w" + no_line[-2:]
    got = ask([yes_line, no_line], timeout=10)
    assert got == [expected(yes_line), expected(no_line)], (
        f"Two lines of 200000 characters: expected {[expected(yes_line), expected(no_line)]}, got {got}. "
        "Move each pointer only inwards; never rebuild the string inside the loop.")
