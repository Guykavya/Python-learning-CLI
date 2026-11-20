import itertools
import random
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

from solution import reorganize

HERE = Path(__file__).parent


def possible_by_search(s):
    """True if some ordering of the letters has no equal neighbours (tries every ordering: small strings only)."""
    return any(all(x != y for x, y in zip(p, p[1:])) for p in set(itertools.permutations(s)))


def possible_by_rule(s):
    return not s or max(Counter(s).values()) <= (len(s) + 1) // 2


def check(s):
    got = reorganize(s)
    assert isinstance(got, str), f"return a string, not a {type(got).__name__}."
    if possible_by_rule(s):
        assert got != "" or s == "", (
            f"{s!r} can be arranged (its most frequent letter appears at most (n + 1) // 2 times) but you returned ''. "
            "Check the limit: (n + 1) // 2, not n // 2, and that the letter you hold back comes back into the heap.")
        assert sorted(got) == sorted(s), (
            f"{s!r}: your result {got!r} does not contain exactly the letters of the input (a letter was lost or invented).")
        assert all(x != y for x, y in zip(got, got[1:])), (
            f"{s!r}: your result {got!r} has two equal letters next to each other. "
            "The letter you placed last must wait one round before it can be taken from the heap again.")
    else:
        assert got == "", (
            f"{s!r} cannot be arranged (one letter appears more than (n + 1) // 2 times); the answer is '', you returned {got!r}.")
    return got


def test_the_examples():
    assert check("aab") == "aba", "the only arrangement of a, a, b without equal neighbours is 'aba'."
    assert check("aaab") == "", "three a's in four places: impossible, return ''."
    check("aabbcc")
    assert check("") == "", "an empty string is returned as an empty string."


def test_one_letter_and_two_letters():
    assert check("a") == "a", "one letter has no neighbour: it is already fine."
    assert check("aa") == "", "two equal letters cannot be separated."
    assert check("ab") in ("ab", "ba"), "two different letters: either order."
    assert check("aaa") == "", "three equal letters: impossible."


def test_exactly_on_the_limit():
    assert check("aabb") in ("abab", "baba"), "two a's and two b's: 'abab' or 'baba'."
    assert check("aaabb") == "ababa", "three a's in five places: only 'ababa' works (a on the limit (5 + 1) // 2 = 3)."
    assert check("aaabbbc") != "", "7 letters, three a's, three b's: arrangement exists."


def test_the_limit_for_five_and_six_letters():
    assert check("aaabc") != "", "three a's in five letters: the limit is (5 + 1) // 2 = 3, so 'abaca' works."
    assert check("aaaabc") == "", "four a's in six letters: the limit is (6 + 1) // 2 = 3, so it is impossible."


@pytest.mark.parametrize("seed", range(70))
def test_small_random_strings_against_a_search_of_all_orderings(seed):
    rng = random.Random(seed)
    s = "".join(rng.choice("abcd"[:rng.randint(2, 4)]) for _ in range(rng.randint(0, 7)))
    got = check(s)
    assert (got != "" or s == "") == (possible_by_search(s) or s == ""), (
        f"{s!r}: an arrangement {'exists' if possible_by_search(s) else 'does not exist'}, you returned {got!r}.")


@pytest.mark.parametrize("seed", range(40))
def test_random_longer_strings(seed):
    rng = random.Random(1000 + seed)
    letters = "abcdefghijklmnopqrstuvwxyz"[:rng.randint(2, 26)]
    s = "".join(rng.choice(letters) for _ in range(rng.randint(20, 120)))
    check(s)


BIG = """
import random
from collections import Counter
from solution import reorganize

def ok(original, result):
    if result == "":
        return False
    return sorted(result) == sorted(original) and all(x != y for x, y in zip(result, result[1:]))

rng = random.Random(9)
cases = [
    ("ab" * 50000 + "a", True),                                       # a: 50001 of 100001, exactly the limit
    ("a" * 50001 + "b" * 50000, True),
    ("a" * 50002 + "b" * 49999, False),                               # one over the limit
    ("".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(100001)), True),
    ("".join(rng.choice("abc") for _ in range(100001)), True),
]
out = []
for s, possible in cases:
    got = reorganize(s)
    out.append("OK" if (ok(s, got) if possible else got == "") else "WRONG")
print(" ".join(out))
"""


def test_big_strings_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG], cwd=HERE, capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        pytest.fail(
            "100,001 letters did not finish in 10 seconds. Use a heap of the (at most 26) letters with their counts: "
            "one heap operation per placed letter. Searching the whole result for a place for every letter is too slow.")
    assert r.returncode == 0, "your code crashed on the big case:\n" + r.stderr[-600:]
    assert r.stdout.split() == ["OK"] * 5, (
        f"big cases gave {r.stdout.strip()!r}: they are, in order, a tight 'ab...a', a block 'aaa...bbb', one letter over "
        "the limit (must be ''), 26 random letters, 3 random letters. All must be OK.")
