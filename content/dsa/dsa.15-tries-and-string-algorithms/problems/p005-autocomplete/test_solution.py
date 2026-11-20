import bisect
import pathlib
import random
import subprocess
import sys

from solution import Autocomplete

HERE = pathlib.Path(__file__).parent


def slow(words, prefix, k):
    return sorted({w for w in words if w.startswith(prefix)})[:k]


def test_examples():
    ac = Autocomplete(["mobile", "mouse", "moneypot", "monitor", "mousepad"])
    assert ac.suggest("m") == ["mobile", "moneypot", "monitor"], (
        f"suggest('m'): the first 3 names in alphabetical order, got {ac.suggest('m')}. Visit children sorted.")
    assert ac.suggest("mou") == ["mouse", "mousepad"], (
        f"suggest('mou'): 'mouse' comes before 'mousepad', got {ac.suggest('mou')}. Record a node's own name "
        "before its children.")
    assert ac.suggest("mouse", k=1) == ["mouse"]
    assert ac.suggest("x") == [], "No name starts with 'x': []."


def test_empty_prefix_and_k():
    ac = Autocomplete(["bat", "bar", "bark", "ball"])
    assert ac.suggest("") == ["ball", "bar", "bark"], "suggest(''): the first 3 names overall, alphabetically."
    assert ac.suggest("ba", k=10) == ["ball", "bar", "bark", "bat"], "k larger than the matches: all of them."
    assert ac.suggest("ba", k=0) == [], "k = 0: no suggestions."


def test_duplicates_and_prefix_is_a_name():
    ac = Autocomplete(["app", "app", "apple", "apply", "ape"])
    assert ac.suggest("app") == ["app", "apple", "apply"], "Each name once; the prefix itself is a name."
    assert ac.suggest("apple") == ["apple"]
    assert ac.suggest("apples") == []


def test_random_against_sorting():
    rng = random.Random(1505)
    for _ in range(100):
        words = ["".join(rng.choice("abc") for _ in range(rng.randint(1, 4))) for _ in range(rng.randint(0, 15))]
        ac = Autocomplete(words)
        for _ in range(10):
            p = "".join(rng.choice("abc") for _ in range(rng.randint(0, 3)))
            k = rng.randint(0, 5)
            want = slow(words, p, k)
            assert ac.suggest(p, k) == want, f"words={words}: suggest({p!r}, {k}) should be {want}."


def test_many_queries_in_time():
    code = (
        "import bisect, random\n"
        "from solution import Autocomplete\n"
        "rng = random.Random(155)\n"
        "words = [''.join(rng.choice('abcdefghij') for _ in range(rng.randint(3, 12))) for _ in range(5 * 10**4)]\n"
        "names = sorted(set(words))\n"
        "queries = [''.join(rng.choice('abcdefghij') for _ in range(rng.randint(0, 4))) for _ in range(2 * 10**4)]\n"
        "def want(p):\n"
        "    i = bisect.bisect_left(names, p)\n"
        "    return [w for w in names[i:i + 3] if w.startswith(p)]\n"
        "expected = [want(p) for p in queries]\n"
        "import time\n"
        "t0 = time.perf_counter()\n"
        "ac = Autocomplete(words)\n"
        "got = [ac.suggest(p) for p in queries]\n"
        "print(sum(g != e for g, e in zip(got, expected)), round(time.perf_counter() - t0, 1))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (30 s) for 2 * 10**4 queries on 5 * 10**4 names. Do not scan the whole list, and stop the "
        "DFS as soon as k names are found (a 1-letter prefix matches thousands of names).")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    wrong = r.stdout.split()[0]
    assert wrong == "0", f"Large input: {wrong} of 2 * 10**4 answers differ from the 3 alphabetically first matches."
