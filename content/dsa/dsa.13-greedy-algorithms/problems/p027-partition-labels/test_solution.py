import random

from solution import partition_labels


def brute(s):
    """Try every set of cut positions; keep the valid split with the most pieces."""
    n = len(s)
    if n == 0:
        return []
    best = None
    for mask in range(1 << (n - 1)):              # bit i set = cut after index i
        pieces = []
        start = 0
        for i in range(n - 1):
            if mask >> i & 1:
                pieces.append(s[start:i + 1])
                start = i + 1
        pieces.append(s[start:])
        ok = all(not (set(pieces[a]) & set(pieces[b])) for a in range(len(pieces)) for b in range(a + 1, len(pieces)))
        if ok and (best is None or len(pieces) > len(best)):
            best = pieces
    return [len(p) for p in best]


def test_examples():
    assert partition_labels("ababcbacadefegdehijhklij") == [9, 7, 8], (
        "Expected [9, 7, 8]: 'ababcbaca', 'defegde', 'hijhklij'. Each piece must reach the LAST occurrence of "
        "every letter inside it.")
    assert partition_labels("eccbbbbdec") == [10], (
        "Expected [10]: the first 'e' forces the piece to index 8, and the 'c' inside it forces index 9.")


def test_all_different():
    assert partition_labels("abc") == [1, 1, 1], "Every letter appears once: cut after every letter."
    assert partition_labels("z") == [1], "One letter: one piece of length 1."


def test_empty():
    assert partition_labels("") == [], "The empty string has no pieces: []."


def test_keep_the_furthest_end():
    assert partition_labels("abaccbd") == [6, 1], (
        "Expected [6, 1]. 'a' ends at 2, but 'b' (seen at 1) ends at 5: keep end = max(end, last[ch]), "
        "or the cut after 'aba' would split the b's.")
    assert partition_labels("abab") == [4], "'a' and 'b' are interleaved: one piece of length 4."


def test_returns_lengths():
    out = partition_labels("aabbcc")
    assert out == [2, 2, 2], f"Return the LENGTHS of the pieces ('aa', 'bb', 'cc'): [2, 2, 2]; got {out!r}."


def test_random_against_brute_force():
    rng = random.Random(27)
    for _ in range(400):
        s = "".join(rng.choice("abcd") for _ in range(rng.randint(0, 9)))
        want = brute(s)
        got = partition_labels(s)
        assert got == want, (
            f"s={s!r}: expected {want} (every set of cuts tried), got {got}. Cut at i when i equals the furthest "
            "last occurrence of any letter in the current piece.")


def test_large_input():
    rng = random.Random(2727)
    s = "".join(rng.choice("abcdefghij") for _ in range(10**5)) + "xyz"
    out = partition_labels(s)
    assert out[-3:] == [1, 1, 1] and sum(out) == len(s), (
        "100,003 letters: the pieces must cover the whole string, and the last three letters x, y, z (each once) "
        "are pieces of length 1.")
