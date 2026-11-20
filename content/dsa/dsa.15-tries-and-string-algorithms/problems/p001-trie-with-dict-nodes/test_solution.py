import pathlib
import random
import subprocess
import sys

from solution import Trie

HERE = pathlib.Path(__file__).parent


def build(words):
    t = Trie()
    for w in words:
        t.insert(w)
    return t


def test_examples():
    t = build(["car", "card", "cat"])
    assert t.search("car") is True, "search('car'): 'car' was inserted."
    assert t.search("ca") is False, (
        "search('ca') must be False: 'ca' is only a prefix. Check the is_end flag of the last node.")
    assert t.search("cards") is False, "search('cards'): the path breaks after 'card'."
    assert t.starts_with("ca") is True, "starts_with('ca'): 'car' starts with it."
    assert t.starts_with("cb") is False, "starts_with('cb'): no 'b' child under 'c'."
    assert t.starts_with("") is True, "starts_with(''): every word starts with the empty string."


def test_tree_shape():
    t = build(["car", "cat", "dog"])
    assert sorted(t.root.children) == ["c", "d"], (
        f"The root should have the children 'c' and 'd', got {sorted(t.root.children)}. Each node's children "
        "is a dict letter -> TrieNode.")
    a = t.root.children["c"].children["a"]
    assert sorted(a.children) == ["r", "t"], "The node for 'ca' should have the children 'r' and 't' (shared prefix)."
    assert a.is_end is False and a.children["r"].is_end is True, "Only the node for 'car' ends a word, not 'ca'."


def test_inserting_more_keeps_old_words():
    t = build(["card"])
    t.insert("cat")
    assert t.search("card"), (
        "After inserting 'cat', 'card' must still be found. Create a child only if it is missing; never "
        "replace an existing child.")


def test_empty_word_and_case():
    t = Trie()
    assert t.search("") is False, "An empty trie contains nothing, not even ''."
    t.insert("")
    assert t.search("") is True, "After insert(''), search('') is True: the root is marked as a word end."
    t.insert("Car")
    assert t.search("car") is False and t.search("Car") is True, "The trie is case sensitive: 'Car' is not 'car'."
    t.insert("a b")
    assert t.search("a b") and t.starts_with("a "), "Any character may appear, spaces included."


def test_duplicates():
    t = build(["to", "to"])
    assert t.search("to") and not t.search("t"), "Inserting a word twice is harmless."


def test_random_against_a_set():
    rng = random.Random(1501)
    for _ in range(100):
        words = ["".join(rng.choice("ab") for _ in range(rng.randint(0, 5))) for _ in range(rng.randint(0, 8))]
        t = build(words)
        for _ in range(20):
            q = "".join(rng.choice("ab") for _ in range(rng.randint(0, 6)))
            assert t.search(q) == (q in words), f"words={words}: search({q!r}) should be {q in words}."
            want = any(w.startswith(q) for w in words)
            assert t.starts_with(q) == want, f"words={words}: starts_with({q!r}) should be {want}."


def test_many_words_in_time():
    code = (
        "import random\n"
        "from solution import Trie\n"
        "rng = random.Random(15)\n"
        "words = [''.join(rng.choice('abcde') for _ in range(rng.randint(5, 12))) for _ in range(10**5)]\n"
        "t = Trie()\n"
        "for w in words:\n"
        "    t.insert(w)\n"
        "qs = [''.join(rng.choice('abcde') for _ in range(rng.randint(3, 9))) for _ in range(10**5)]\n"
        "print(sum(t.search(q) for q in qs), sum(t.starts_with(q) for q in qs))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (30 s) for 10**5 words and 2 * 10**5 queries. Scanning all words for every question is "
        "10**10 steps; walking the trie costs only the length of the query.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["24498", "68258"], f"Large input: expected 24498 68258, got {r.stdout.split()}."
