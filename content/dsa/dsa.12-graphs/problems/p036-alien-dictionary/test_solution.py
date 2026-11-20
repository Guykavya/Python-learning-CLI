import random
from collections import deque

from solution import alien_order


def analyse(words):
    """Return (letters, edges, ok) where ok says whether ANY consistent alphabet exists."""
    letters = {c for w in words for c in w}
    edges = set()
    for w1, w2 in zip(words, words[1:]):
        for a, b in zip(w1, w2):
            if a != b:
                edges.add((a, b))
                break
        else:
            if len(w1) > len(w2):
                return letters, edges, False
    indeg = {c: 0 for c in letters}
    for a, b in edges:
        indeg[b] += 1
    ready = deque(c for c in letters if indeg[c] == 0)
    seen = 0
    while ready:
        c = ready.popleft()
        seen += 1
        for a, b in edges:
            if a == c:
                indeg[b] -= 1
                if indeg[b] == 0:
                    ready.append(b)
    return letters, edges, seen == len(letters)


def is_sorted_by(words, alphabet):
    rank = {c: i for i, c in enumerate(alphabet)}
    keys = [[rank[c] for c in w] for w in words]
    return all(keys[i] <= keys[i + 1] for i in range(len(keys) - 1))


def check(words, got, label):
    letters, edges, ok = analyse(words)
    if not ok:
        assert got == "", (
            f"{label}: no alphabet can sort {words} (a cycle or a longer word before its own prefix); "
            f"expected '', got {got!r}.")
        return
    assert isinstance(got, str), f"{label}: return a string, got {type(got).__name__}."
    assert got != "", (
        f"{label}: an alphabet exists for {words}, but you returned ''. Only the FIRST differing letter of "
        "neighbouring words gives an edge (later letters say nothing); a prefix BEFORE a longer word is fine; "
        "and letters that are in no edge still belong in the answer.")
    assert sorted(got) == sorted(letters) and len(set(got)) == len(got), (
        f"{label}: the answer must contain every letter that appears ({''.join(sorted(letters))}) exactly once, "
        f"got {got!r}. Letters that are in no edge belong in the answer too.")
    for a, b in sorted(edges):
        assert got.index(a) < got.index(b), (
            f"{label}: the sorted words say {a!r} comes before {b!r}, but your order {got!r} has {b!r} first. "
            "Check the direction of the edge (the letter of the EARLIER word comes first).")
    assert is_sorted_by(words, got), f"{label}: the words are not sorted in your alphabet {got!r}."


def test_examples():
    check(["wrt", "wrf", "er", "ett", "rftt"], alien_order(["wrt", "wrf", "er", "ett", "rftt"]), "example 1")
    assert alien_order(["wrt", "wrf", "er", "ett", "rftt"]) == "wertf", "Example 1 has exactly one answer: 'wertf'."
    assert alien_order(["z", "x"]) == "zx", "['z', 'x']: z comes before x."
    assert alien_order(["z", "x", "z"]) == "", "z < x and x < z is a cycle: return ''."
    assert alien_order(["abc", "ab"]) == "", (
        "'abc' before 'ab' is impossible in any alphabet (a longer word before its own prefix): return ''.")
    check(["ab", "abc"], alien_order(["ab", "abc"]), "['ab', 'abc'] (a prefix first is fine)")


def test_only_first_difference_counts():
    words = ["ab", "ba"]
    check(words, alien_order(words), "['ab', 'ba'] only says a < b")
    words = ["abc", "bca", "cab"]
    check(words, alien_order(words), "['abc', 'bca', 'cab'] gives a < b and b < c only")


def test_single_word_and_letters_without_edges():
    got = alien_order(["hello"])
    check(["hello"], got, "one word")
    check(["ba", "bc", "d"], alien_order(["ba", "bc", "d"]), "letters a, c, d and b")
    assert len(alien_order(["xyz"])) == 3, "One word 'xyz': all three letters, in any order."


def test_random_valid_dictionaries():
    rng = random.Random(36)
    for t in range(300):
        k = rng.randint(1, 7)
        alphabet = rng.sample("abcdefghij", k)
        words = ["".join(rng.choice(alphabet) for _ in range(rng.randint(1, 4))) for _ in range(rng.randint(1, 9))]
        rank = {c: i for i, c in enumerate(alphabet)}
        words.sort(key=lambda w: [rank[c] for c in w])
        check(words, alien_order(words), f"random valid #{t}")


def test_random_shuffled_lists():
    rng = random.Random(360)
    for t in range(300):
        words = ["".join(rng.choice("abcd") for _ in range(rng.randint(1, 3))) for _ in range(rng.randint(2, 6))]
        check(words, alien_order(words), f"random #{t} {words}")
