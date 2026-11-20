import os
import pathlib
import random
import subprocess
import sys

from solution import longest_common_prefix

HERE = pathlib.Path(__file__).parent


def test_examples():
    assert longest_common_prefix(["flower", "flow", "flight"]) == "fl", "Expected 'fl'."
    assert longest_common_prefix(["dog", "racecar", "car"]) == "", "The first letters differ: ''."
    assert longest_common_prefix(["interview", "internet", "interval"]) == "inter", "Expected 'inter'."


def test_a_word_ends():
    got = longest_common_prefix(["abc", "ab"])
    assert got == "ab", (
        f"Expected 'ab', got {got!r}. The word 'ab' ends there, so the prefix cannot grow: stop when a word "
        "ends, not only at a branch.")
    assert longest_common_prefix(["abc", "abd", "ab"]) == "ab"


def test_edges():
    assert longest_common_prefix([]) == "", "An empty list: ''."
    assert longest_common_prefix(["solo"]) == "solo", "One word: the word itself."
    assert longest_common_prefix(["same", "same"]) == "same", "Identical words: the whole word."
    assert longest_common_prefix(["abc", "", "ab"]) == "", "A list with '' has the common prefix ''."
    assert longest_common_prefix(["a b c", "a b d"]) == "a b ", "Any characters, spaces included."


def test_all_words_matter():
    got = longest_common_prefix(["abcd", "abce", "xbcd"])
    assert got == "", f"The third word starts with 'x': expected '', got {got!r}. Compare every word."


def test_random_against_commonprefix():
    rng = random.Random(1506)
    for _ in range(300):
        words = ["ab" + "".join(rng.choice("ab") for _ in range(rng.randint(0, 5))) for _ in range(rng.randint(1, 6))]
        if rng.random() < 0.3:
            words = [w[2:] for w in words]
        want = os.path.commonprefix(words)
        got = longest_common_prefix(list(words))
        assert got == want, f"words={words}: expected {want!r}, got {got!r}."


def test_long_words():
    code = (
        "from solution import longest_common_prefix\n"
        "base = 'x' * 900\n"
        "words = [base + str(i).zfill(100) for i in range(10**4)]\n"
        "print(len(longest_common_prefix(words)), len(longest_common_prefix([base * 10] * 50)))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, "Time limit (30 s) for 10**4 words of 1000 letters: stay linear in the total length."
    assert r.returncode == 0, "Your code crashed on long words:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["996", "9000"], (
        f"Long words: expected lengths 996 and 9000, got {r.stdout.split()}.")
