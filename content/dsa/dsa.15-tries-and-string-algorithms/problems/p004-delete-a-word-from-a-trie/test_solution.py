import random

from solution import Trie


def build(words):
    t = Trie()
    for w in words:
        t.insert(w)
    return t


def test_chapter_example():
    t = build(["car", "card", "cat"])
    assert t.node_count() == 6, f"root + c, a, r, d, t = 6 nodes, got {t.node_count()}."
    assert t.delete("card") is True, "delete('card') returns True: it was stored."
    assert t.node_count() == 5, (
        f"After deleting 'card' the node 'd' is useless: 5 nodes, got {t.node_count()}. Free childless non-end "
        "nodes from the bottom up.")
    assert t.search("car") and not t.search("card"), "'car' must stay; 'card' must be gone."
    assert t.delete("cat") is True and t.node_count() == 4, "Deleting 'cat' frees 't' only: 4 nodes."
    assert t.starts_with("ca"), "'car' is still there, so 'ca' is still a prefix."


def test_not_stored():
    t = build(["car"])
    assert t.delete("ca") is False, "'ca' is only a prefix, not a stored word: False."
    assert t.delete("dog") is False, "'dog' was never inserted: False."
    assert t.delete("cart") is False, "'cart' goes past the stored path: False."
    assert t.search("car") and t.node_count() == 4, "Failed deletes must change nothing."


def test_delete_all():
    t = build(["car"])
    assert t.delete("car") is True
    assert t.node_count() == 1, f"Deleting the only word leaves just the root, got {t.node_count()} nodes."
    assert t.delete("car") is False, "Deleting the same word twice: the second time it is not there."


def test_stop_at_word_end():
    t = build(["a", "abc"])
    t.delete("abc")
    assert t.search("a") and t.node_count() == 2, (
        "Deleting 'abc' frees 'c' and 'b' but stops at 'a', which ends another word: 2 nodes left.")


def test_empty_word():
    t = build(["", "x"])
    assert t.delete("") is True and not t.search("") and t.search("x"), "The empty word lives on the root."
    assert t.node_count() == 2, "The root is never removed."


def test_random_against_a_set():
    rng = random.Random(1504)
    for _ in range(150):
        t, stored = Trie(), set()
        for _ in range(30):
            w = "".join(rng.choice("ab") for _ in range(rng.randint(0, 4)))
            if rng.random() < 0.55:
                t.insert(w)
                stored.add(w)
            else:
                got = t.delete(w)
                assert got == (w in stored), f"delete({w!r}) with stored={sorted(stored)} should be {w in stored}."
                stored.discard(w)
            prefixes = {s[:k] for s in stored for k in range(len(s) + 1)} | {""}
            assert t.node_count() == len(prefixes), (
                f"stored={sorted(stored)}: the trie should have one node per distinct prefix ({len(prefixes)}), "
                f"got {t.node_count()}. A node may go only if it has no children and is not a word end.")
            for q in ("", "a", "b", "ab", "ba", "aab"):
                assert t.search(q) == (q in stored), f"stored={sorted(stored)}: search({q!r})."


def test_long_word():
    t = build(["a" * 5000, "a" * 2500])
    assert t.delete("a" * 5000) and t.node_count() == 2501, (
        "Deleting a 5000-letter word stops at the end of the 2500-letter one: 2501 nodes. Use loops, not "
        "recursion, so long words do not hit the recursion limit.")
