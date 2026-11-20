import pathlib
import random
import subprocess
import sys

from solution import replace_words

HERE = pathlib.Path(__file__).parent


def slow(roots, sentence):
    out = []
    for w in sentence.split():
        best = w
        for r in roots:
            if w.startswith(r) and len(r) < len(best):
                best = r
        out.append(best)
    return " ".join(out)


def test_examples():
    assert replace_words(["cat", "bat", "rat"], "the cattle was rattled by the battery") == \
        "the cat was rat by the bat", "Expected 'the cat was rat by the bat'."
    got = replace_words(["a", "aa", "aaa"], "aadsfasf absbs bbab cadsfafs")
    assert got == "a a bbab cadsfafs", f"The shortest root 'a' wins over 'aa'; got {got!r}."
    assert replace_words(["ab", "abc"], "abcd ab a") == "ab ab a", (
        "'a' is shorter than every root: it stays 'a'. 'ab' is itself a root.")


def test_shortest_not_first_in_list():
    got = replace_words(["aa", "a"], "aab")
    assert got == "a", (
        f"Roots ['aa', 'a'] for 'aab': the SHORTEST root 'a' wins, got {got!r}. Do not take the first match "
        "in list order.")


def test_no_roots():
    assert replace_words([], "nothing changes") == "nothing changes"
    assert replace_words(["xyz"], "abc") == "abc"


def test_random_against_slow():
    rng = random.Random(1507)
    for _ in range(300):
        roots = ["".join(rng.choice("ab") for _ in range(rng.randint(1, 3))) for _ in range(rng.randint(0, 4))]
        sentence = " ".join("".join(rng.choice("ab") for _ in range(rng.randint(1, 5)))
                            for _ in range(rng.randint(1, 5)))
        want = slow(roots, sentence)
        got = replace_words(list(roots), sentence)
        assert got == want, f"roots={roots}, sentence={sentence!r}: expected {want!r}, got {got!r}."


def test_large_input():
    code = (
        "import random\n"
        "from solution import replace_words\n"
        "rng = random.Random(157)\n"
        "roots = [''.join(rng.choice('abcd') for _ in range(rng.randint(3, 8))) for _ in range(10**4)]\n"
        "words = [''.join(rng.choice('abcd') for _ in range(rng.randint(1, 30))) for _ in range(10**5)]\n"
        "out = replace_words(roots, ' '.join(words)).split()\n"
        "print(len(out), sum(a != b for a, b in zip(out, words)), sum(map(len, out)))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (30 s) for 10**4 roots and 10**5 words. Trying every root for every word is 10**9 checks; "
        "a trie walk costs at most the length of the longest root per word.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["100000", "90057", "290076"], f"Large input: expected 100000 words, 90057 replaced, total length 290076, got {r.stdout.split()}."
