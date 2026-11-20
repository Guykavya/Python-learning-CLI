import pathlib
import random
import re
import subprocess
import sys

from solution import WordDictionary

HERE = pathlib.Path(__file__).parent


def build(words):
    wd = WordDictionary()
    for w in words:
        wd.add_word(w)
    return wd


def test_examples():
    wd = build(["bad", "dad", "mad", "pad"])
    assert wd.search("pad") and wd.search("bad"), "Plain words that were added: True."
    assert wd.search(".ad") and wd.search("b..") and wd.search("..."), "'.' matches exactly one letter."
    assert wd.search("x..") is False, "No word starts with 'x'."


def test_length_must_match():
    wd = build(["bad", "dad"])
    assert wd.search("b.") is False, (
        "'b.' has 2 letters, every word has 3: False. At the end of the pattern, the node must be a word end.")
    assert wd.search("..d.") is False, "'..d.' has 4 letters: False."
    assert wd.search("....") is False and wd.search("") is False, "Lengths must agree; no empty word was added."


def test_dot_must_try_every_child():
    wd = build(["ab", "cd"])
    assert wd.search(".d") is True, (
        "'.d' matches 'cd', which is under the SECOND child of the root. At a '.', try every child.")


def test_prefix_and_longer_words():
    wd = build(["a", "abc"])
    assert wd.search("a") and wd.search(".") and wd.search("..c")
    assert wd.search("..") is False, "'ab' is only a prefix of 'abc', not a word."


def test_random_against_regex():
    rng = random.Random(1509)
    for _ in range(150):
        words = ["".join(rng.choice("ab") for _ in range(rng.randint(1, 4))) for _ in range(rng.randint(0, 8))]
        wd = build(words)
        for _ in range(15):
            p = "".join(rng.choice("ab.") for _ in range(rng.randint(0, 5)))
            want = any(re.fullmatch(p, w) for w in words)
            assert wd.search(p) == want, f"words={words}: search({p!r}) should be {want}."


def test_many_queries_in_time():
    code = (
        "import random\n"
        "from solution import WordDictionary\n"
        "rng = random.Random(159)\n"
        "wd = WordDictionary()\n"
        "for _ in range(2 * 10**4):\n"
        "    wd.add_word(''.join(rng.choice('abcdef') for _ in range(rng.randint(1, 10))))\n"
        "hits = 0\n"
        "for _ in range(2 * 10**4):\n"
        "    p = [rng.choice('abcdef') for _ in range(rng.randint(1, 10))]\n"
        "    for _ in range(rng.randint(0, 3)):\n"
        "        p[rng.randrange(len(p))] = '.'\n"
        "    hits += wd.search(''.join(p))\n"
        "print(hits)\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (30 s) for 2 * 10**4 patterns on 2 * 10**4 words. Comparing each pattern with every word is "
        "4 * 10**8 comparisons; a trie follows only the edges the pattern allows.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["10843"], f"Large input: expected 10843 matches, got {r.stdout.split()}."
