import pathlib
import random
import subprocess
import sys

from solution import ArrayTrie

HERE = pathlib.Path(__file__).parent


def build(words):
    t = ArrayTrie()
    for w in words:
        t.insert(w)
    return t


def test_examples():
    t = build(["car", "card", "care", "cat", "dog", "dot"])
    assert t.search("care") is True and t.search("ca") is False, (
        "search('care') is True; search('ca') is False because 'ca' is only a prefix (is_end).")
    assert t.starts_with("do") is True and t.starts_with("dx") is False, "starts_with: 'do' yes, 'dx' no."
    assert t.node_count == 11, (
        f"6 words, 20 letters, but only 11 nodes including the root; got node_count={t.node_count}. Count a node "
        "only when you create it.")


def test_slots():
    t = build(["car"])
    assert len(t.root.next) == 26, "Each node has a list of 26 slots."
    assert t.root.next[2] is not None, "'c' goes into slot ord('c') - 97 = 2."
    assert sum(x is not None for x in t.root.next) == 1, "Only one slot of the root is used after inserting 'car'."
    other = t.root.next[2]
    assert other.next is not t.root.next, (
        "Two nodes share the same list object: create a new list [None] * 26 in every node's __init__.")


def test_letters_a_and_z():
    t = build(["az", "za"])
    assert t.search("az") and t.search("za") and not t.search("a"), "Slots 0 ('a') and 25 ('z') must work."


def test_node_count_and_duplicates():
    t = ArrayTrie()
    assert t.node_count == 1, "An empty trie has one node, the root."
    t.insert("abc")
    t.insert("abc")
    t.insert("ab")
    assert t.node_count == 4, f"'abc' twice and 'ab': root + a + b + c = 4 nodes, got {t.node_count}."
    t.insert("")
    assert t.search("") and t.node_count == 4, "insert('') marks the root and adds no node."


def test_random_against_a_set():
    rng = random.Random(1502)
    for _ in range(100):
        words = ["".join(rng.choice("abz") for _ in range(rng.randint(0, 5))) for _ in range(rng.randint(0, 8))]
        t = build(words)
        prefixes = {w[:k] for w in words for k in range(len(w) + 1)}
        assert t.node_count == len(prefixes | {""}), (
            f"words={words}: one node per distinct prefix (the empty prefix is the root) = {len(prefixes | {''})}, "
            f"got {t.node_count}.")
        for _ in range(15):
            q = "".join(rng.choice("abz") for _ in range(rng.randint(0, 6)))
            assert t.search(q) == (q in words), f"words={words}: search({q!r}) should be {q in words}."
            assert t.starts_with(q) == (q in prefixes), f"words={words}: starts_with({q!r}) should be {q in prefixes}."


def test_many_words_in_time():
    code = (
        "import random\n"
        "from solution import ArrayTrie\n"
        "rng = random.Random(152)\n"
        "t = ArrayTrie()\n"
        "for _ in range(5 * 10**4):\n"
        "    t.insert(''.join(rng.choice('abcdefgh') for _ in range(rng.randint(4, 10))))\n"
        "qs = [''.join(rng.choice('abcdefgh') for _ in range(rng.randint(2, 7))) for _ in range(10**5)]\n"
        "print(t.node_count, sum(t.search(q) for q in qs), sum(t.starts_with(q) for q in qs))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, "Time limit (30 s) for 5 * 10**4 words and 2 * 10**5 queries: walk the trie, do not scan."
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["133346", "17507", "64554"], (
        f"Large input: expected 133346 nodes, 17507 and 64554, got {r.stdout.split()}.")
