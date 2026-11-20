import pathlib
import random
import subprocess
import sys

from solution import CountTrie

HERE = pathlib.Path(__file__).parent


def build(words):
    ct = CountTrie()
    for w in words:
        ct.insert(w)
    return ct


def test_examples():
    ct = build(["car", "car", "card", "care", "cat", "dog"])
    assert ct.count_equal("car") == 2, "'car' was logged twice: count_equal('car') is 2. Use a counter, not a flag."
    assert ct.count_equal("ca") == 0, "'ca' is only a prefix: count_equal('ca') is 0."
    assert ct.count_prefix("car") == 4, "Words through 'car': car, car, card, care = 4."
    assert ct.count_prefix("ca") == 5, "Words through 'ca': the four above plus cat = 5."
    assert ct.count_prefix("z") == 0, "No word starts with 'z': 0 (the path breaks)."


def test_empty_prefix_counts_everything():
    ct = build(["a", "b", "b"])
    assert ct.count_prefix("") == 3, (
        "count_prefix('') is the number of logged words (3). Every word passes through the root: add 1 to the "
        "root's pass_count in insert.")
    assert CountTrie().count_prefix("") == 0, "An empty log: 0."


def test_empty_word():
    ct = build(["", "", "x"])
    assert ct.count_equal("") == 2, "The empty word was logged twice: count_equal('') is 2."
    assert ct.count_prefix("x") == 1


def test_random_against_counting():
    rng = random.Random(1503)
    for _ in range(100):
        words = ["".join(rng.choice("ab") for _ in range(rng.randint(0, 4))) for _ in range(rng.randint(0, 10))]
        ct = build(words)
        for _ in range(15):
            q = "".join(rng.choice("ab") for _ in range(rng.randint(0, 5)))
            assert ct.count_equal(q) == words.count(q), f"words={words}: count_equal({q!r}) = {words.count(q)}."
            want = sum(w.startswith(q) for w in words)
            assert ct.count_prefix(q) == want, f"words={words}: count_prefix({q!r}) = {want}."


def test_many_queries_in_time():
    code = (
        "import random\n"
        "from solution import CountTrie\n"
        "rng = random.Random(153)\n"
        "ct = CountTrie()\n"
        "for _ in range(10**5):\n"
        "    ct.insert(''.join(rng.choice('abc') for _ in range(rng.randint(1, 8))))\n"
        "qs = [''.join(rng.choice('abc') for _ in range(rng.randint(0, 3))) for _ in range(10**5)]\n"
        "print(sum(ct.count_prefix(q) for q in qs), sum(ct.count_equal(q) for q in qs))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (30 s) for 10**5 short prefix queries. Counting the subtree (or scanning all words) on every "
        "query is too slow: keep pass_count on the nodes.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["3639199005", "150946233"], f"Large input: expected 3639199005 150946233, got {r.stdout.split()}."
