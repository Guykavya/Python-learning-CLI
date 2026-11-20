import pathlib
import random
import subprocess
import sys
from collections import deque

from solution import ladder_length

HERE = pathlib.Path(__file__).parent


def run_limited(code, seconds):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=seconds, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None
    return r


def brute(begin, end, words):
    if end not in words:
        return 0
    nodes = list(dict.fromkeys([begin] + list(words)))

    def close(a, b):
        return sum(x != y for x, y in zip(a, b)) == 1

    dist = {begin: 1}
    queue = deque([begin])
    while queue:
        w = queue.popleft()
        if w == end:
            return dist[w]
        for v in nodes:
            if v not in dist and close(w, v):
                dist[v] = dist[w] + 1
                queue.append(v)
    return 0


def test_the_examples():
    words = ["hot", "dot", "dog", "lot", "log", "cog"]
    got = ladder_length("hit", "cog", words)
    assert got == 5, f"hit -> hot -> dot -> dog -> cog has 5 WORDS (4 changes); got {got}."
    assert ladder_length("hit", "cog", words[:-1]) == 0, "cog is not in the list: no ladder, return 0."


def test_shortest_not_first_found():
    words = ["aab", "abb", "bbb", "bba", "baa", "aaa", "caa", "cba"]
    got = ladder_length("aaa", "bba", words)
    assert got == brute("aaa", "bba", words), f"Expected {brute('aaa', 'bba', words)} words, got {got}. Use BFS: a DFS finds a ladder, not the shortest."


def test_edge_cases():
    assert ladder_length("abc", "abc", ["abc"]) == 1, "begin == end: a ladder of one word."
    assert ladder_length("abc", "abd", ["abd"]) == 2, "One change: two words."
    assert ladder_length("abc", "xyz", ["xyz"]) == 0, "No ladder through the list: 0."
    assert ladder_length("hit", "hot", ["hit", "hot"]) == 2, "begin may also be in the list."


def test_random_against_brute_force():
    rng = random.Random(1223)
    for _ in range(200):
        length = rng.randint(1, 3)
        words = sorted({"".join(rng.choice("abc") for _ in range(length)) for _ in range(rng.randint(1, 15))})
        begin = "".join(rng.choice("abc") for _ in range(length))
        end = rng.choice(words + ["zz"[:length]])
        want = brute(begin, end, words)
        got = ladder_length(begin, end, words)
        assert got == want, f"ladder_length({begin!r}, {end!r}, {words}) should be {want}, got {got}."


def test_twelve_thousand_words_is_fast():
    code = (
        "import random\n"
        "from solution import ladder_length\n"
        "rng = random.Random(23)\n"
        "words = sorted({''.join(rng.choice('abcdefgh') for _ in range(6)) for _ in range(12000)})\n"
        "a = ladder_length(words[0], 'zzzzzz', words + ['zzzzzz'])\n"
        "b = ladder_length('aaaaaa', 'aaaaab', ['aaaaab'] + words)\n"
        "print(a, b, len(words))\n"
    )
    r = run_limited(code, 10)
    assert r is not None, (
        "About 12,000 words took more than 10 seconds. Do you compare every pair of words (O(N^2))? Generate the one-letter "
        "changes of a word (25 per position) and look them up in a SET.")
    assert r.returncode == 0, "The big run crashed:\n" + r.stderr[-800:]
    a, b = r.stdout.split()[:2]
    assert a == "0", f"'zzzzzz' shares no ladder with the other words: the answer is 0, got {a}."
    assert b == "2", f"'aaaaaa' -> 'aaaaab' is one change: 2 words, got {b}."
