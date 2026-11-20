import os
import pathlib
import random
import subprocess
import sys

from solution import Trie, kmp_search, prefix_function, z_function

HERE = pathlib.Path(__file__).parent


def find_all(text, pattern):
    if not pattern:
        return list(range(len(text) + 1))
    out, start = [], 0
    while (i := text.find(pattern, start)) != -1:
        out.append(i)
        start = i + 1
    return out


def pi_slow(s):
    return [max((k for k in range(1, i + 1) if s[:k] == s[i + 1 - k:i + 1]), default=0) for i in range(len(s))]


def z_slow(s):
    return [len(os.path.commonprefix([s, s[i:]])) for i in range(len(s))]


# ---------------- Trie ----------------

def test_trie_example():
    t = Trie()
    for w in ["car", "card", "care", "car", "dog"]:
        t.insert(w)
    assert (t.search("car"), t.search("ca"), t.starts_with("ca"), t.count_prefix("car")) == (True, False, True, 4)
    assert t.words_with_prefix("car") == ["car", "card", "care"], "Distinct words, sorted, the prefix word first."
    assert t.words_with_prefix("") == ["car", "card", "care", "dog"] and t.words_with_prefix("x") == []
    assert t.count_prefix("") == 5, "count_prefix('') counts every inserted word, repeats included."


def test_trie_empty_cases():
    t = Trie()
    assert not t.starts_with("") and t.count_prefix("") == 0 and t.words_with_prefix("") == [], (
        "An empty trie: nothing starts with '', count 0, no words.")
    t.insert("")
    assert t.search("") and t.starts_with("") and t.words_with_prefix("") == [""], "The empty word can be stored."


def test_trie_against_a_list():
    rng = random.Random(1530)
    for _ in range(200):
        words = ["".join(rng.choice("ab") for _ in range(rng.randint(0, 4))) for _ in range(rng.randint(0, 10))]
        t = Trie()
        for w in words:
            t.insert(w)
        for _ in range(10):
            p = "".join(rng.choice("ab") for _ in range(rng.randint(0, 4)))
            assert t.search(p) == (p in words), f"words={words}: search({p!r})."
            matching = [w for w in words if w.startswith(p)]
            assert t.starts_with(p) == bool(matching), f"words={words}: starts_with({p!r})."
            assert t.count_prefix(p) == len(matching), f"words={words}: count_prefix({p!r}) = {len(matching)}."
            assert t.words_with_prefix(p) == sorted(set(matching)), (
                f"words={words}: words_with_prefix({p!r}) = {sorted(set(matching))}.")


# ---------------- prefix function, KMP, Z ----------------

def test_tables_examples():
    assert prefix_function("abacaba") == [0, 0, 1, 0, 1, 2, 3]
    assert z_function("abacaba") == [7, 0, 1, 0, 3, 0, 1]
    assert prefix_function("") == [] and z_function("") == []
    assert kmp_search("aaaaa", "aa") == [0, 1, 2, 3] and kmp_search("ab", "") == [0, 1, 2]


def test_tables_against_definitions():
    rng = random.Random(1531)
    for _ in range(800):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 14)))
        assert prefix_function(s) == pi_slow(s), f"prefix_function({s!r}) should be {pi_slow(s)}."
        assert z_function(s) == z_slow(s), f"z_function({s!r}) should be {z_slow(s)}."


def test_search_against_find_and_z():
    rng = random.Random(1532)
    for _ in range(800):
        text = "".join(rng.choice("ab") for _ in range(rng.randint(0, 20)))
        pattern = "".join(rng.choice("ab") for _ in range(rng.randint(0, 5)))
        want = find_all(text, pattern)
        assert kmp_search(text, pattern) == want, f"kmp_search({text!r}, {pattern!r}) should be {want}."
        if pattern:
            z = z_function(pattern + text)
            m = len(pattern)
            via_z = [i for i in range(len(text)) if z[m + i] >= m]
            assert via_z == want, "Your z_function and kmp_search disagree on a pattern search."


# ---------------- speed ----------------

def test_everything_in_time():
    code = (
        "import random\n"
        "from solution import Trie, kmp_search, prefix_function, z_function\n"
        "rng = random.Random(30)\n"
        "t = Trie()\n"
        "for _ in range(10**5):\n"
        "    t.insert(''.join(rng.choice('abcd') for _ in range(rng.randint(3, 10))))\n"
        "t.insert('z' * 10**5)\n"
        "q = sum(t.count_prefix(''.join(rng.choice('abcd') for _ in range(3))) for _ in range(10**5))\n"
        "w = len(t.words_with_prefix('abc'))\n"
        "n = 5 * 10**5\n"
        "s = 'a' * (n - 1) + 'b'\n"
        "print(q, w, len(t.words_with_prefix('zz')), prefix_function(s)[-2], z_function(s)[1],\n"
        "      len(kmp_search(s, 'a' * 1000 + 'b')), len(kmp_search(s, 'aa')))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=60, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (60 s) for the whole toolkit on large inputs. Worst case for the searches: a repeated pattern "
        "like aaaa...b. Check that every part is linear and that nothing recurses on a 10**5-letter word.")
    if "RecursionError" in r.stderr:
        assert False, "RecursionError: a 10**5-letter word was inserted. Use loops (and a stack for the DFS)."
    assert r.returncode == 0, "Your toolkit crashed on large inputs:\n" + r.stderr[-800:]
    want = ["156256981", "806", "1", "499998", "499998", "1", "499998"]
    assert r.stdout.split() == want, f"Large inputs: expected {want}, got {r.stdout.split()}."
