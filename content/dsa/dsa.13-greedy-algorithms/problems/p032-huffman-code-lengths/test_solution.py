import heapq
import pathlib
import random
import string
import subprocess
import sys
from fractions import Fraction
from functools import lru_cache

from solution import code_lengths, total_bits

HERE = pathlib.Path(__file__).parent


@lru_cache(maxsize=None)
def best_merge_cost(ws):
    """Brute force from chapter section 13: the cheapest total over every order of joining pairs."""
    if len(ws) == 1:
        return 0
    best = float("inf")
    for i in range(len(ws)):
        for j in range(i + 1, len(ws)):
            merged = ws[i] + ws[j]
            rest = [ws[k] for k in range(len(ws)) if k != i and k != j] + [merged]
            best = min(best, merged + best_merge_cost(tuple(sorted(rest))))
    return best


def chapter_codes(freq):
    """The chapter's huffman_codes (section 13), used as a second reference."""
    heap = []
    tie = 0
    for letter in sorted(freq):
        heap.append((freq[letter], tie, letter))
        tie += 1
    heapq.heapify(heap)
    while len(heap) > 1:
        w1, _, t1 = heapq.heappop(heap)
        w2, _, t2 = heapq.heappop(heap)
        heapq.heappush(heap, (w1 + w2, tie, (t1, t2)))
        tie += 1
    if len(freq) == 1:
        return {next(iter(freq)): "0"}
    codes = {}
    stack = [(heap[0][2], "")]
    while stack:
        tree, prefix = stack.pop()
        if isinstance(tree, str):
            codes[tree] = prefix
        else:
            stack.append((tree[0], prefix + "0"))
            stack.append((tree[1], prefix + "1"))
    return codes


def optimal_bits(freq):
    if len(freq) == 1:
        return next(iter(freq.values()))
    return best_merge_cost(tuple(sorted(freq.values())))


def check(freq, where):
    lengths = code_lengths(dict(freq))
    assert set(lengths) == set(freq), f"{where}: code_lengths must have one entry per letter; got {lengths}."
    assert all(isinstance(v, int) and v >= 1 for v in lengths.values()), (
        f"{where}: every code length must be a whole number >= 1; got {lengths}.")
    kraft = sum(Fraction(1, 2 ** lengths[x]) for x in freq)
    assert kraft <= 1, (
        f"{where}: lengths {lengths} cannot all fit in a binary tree (sum of 2**-length = {kraft} > 1). "
        "Is the root counted as depth 0?")
    want = optimal_bits(freq)
    got_from_lengths = sum(freq[x] * lengths[x] for x in freq)
    assert got_from_lengths == want, (
        f"{where}: freq={freq}: your lengths {lengths} cost {got_from_lengths} bits, the optimum is {want}. "
        "Join the two LIGHTEST trees each round.")
    got = total_bits(dict(freq))
    assert got == want, f"{where}: freq={freq}: total_bits should be {want}, got {got}."


def test_chapter_example():
    freq = {"a": 45, "b": 13, "c": 12, "d": 16, "e": 9, "f": 5}
    assert code_lengths(freq) == {"a": 1, "b": 3, "c": 3, "d": 3, "e": 4, "f": 4}, (
        "The chapter's table (no ties here, so the lengths are fixed): a 1 bit, b c d 3 bits, e f 4 bits.")
    assert total_bits(freq) == 224, "The chapter's table costs 224 bits."


def test_one_letter():
    assert code_lengths({"z": 7}) == {"z": 1}, "One letter still gets a 1-bit code (the chapter's '0'), not 0 bits."
    assert total_bits({"z": 7}) == 7, "One letter, 7 times: 7 bits (1 bit each), not 0."


def test_two_letters():
    assert code_lengths({"x": 1, "y": 100}) == {"x": 1, "y": 1}, "Two letters: one bit each."


def test_equal_weights_do_not_crash():
    freq = {"a": 1, "b": 1, "c": 2, "d": 2}
    try:
        code_lengths(dict(freq))
    except TypeError as err:
        raise AssertionError(
            f"TypeError on equal counts ({err}). With heap entries (weight, tree), equal weights make Python "
            "compare the trees. Use (weight, tie, tree) with a unique integer tie (chapter section 13).") from None
    check(freq, "equal weights")
    freq = {ch: 3 for ch in "abcdefgh"}
    check(freq, "eight equal weights")
    assert total_bits(freq) == 72, (
        "Eight letters of count 3: a balanced tree, 3 bits each, 72 bits. If you got a TypeError, your heap entries "
        "need a unique tie-breaker between the weight and the tree.")


def test_chain_of_doubling_counts():
    freq = {ch: 2 ** i for i, ch in enumerate("abcdef")}
    check(freq, "doubling counts")
    lengths = code_lengths(freq)
    assert lengths["f"] == 1 and lengths["a"] == lengths["b"] == 5, (
        f"Counts 1, 2, 4, 8, 16, 32 give a chain: f has 1 bit, a and b have 5 bits; got {lengths}.")


def test_random_against_brute_force():
    rng = random.Random(32)
    for _ in range(150):
        k = rng.randint(1, 6)
        letters = rng.sample(string.ascii_lowercase, k)
        freq = {x: rng.randint(1, 8) for x in letters}
        check(freq, "random")
        want = sum(freq[x] * len(c) for x, c in chapter_codes(freq).items())
        assert total_bits(freq) == want, f"freq={freq}: the chapter's Huffman codes cost {want} bits."


def test_many_letters_need_a_heap():
    code = (
        "import random\n"
        "from solution import total_bits\n"
        "rng = random.Random(3232)\n"
        "freq = {'L' + str(i): rng.randint(1, 10**6) for i in range(10**4)}\n"
        "print(total_bits(freq))\n"
    )
    rng = random.Random(3232)
    freq = {"L" + str(i): rng.randint(1, 10**6) for i in range(10**4)}
    heap = list(freq.values())
    heapq.heapify(heap)
    want = 0
    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        want += a + b
        heapq.heappush(heap, a + b)
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=15, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (15 s) with 10,000 letters. Re-sorting the whole list after every join is O(k^2 log k); "
        "use heapq.")
    assert r.returncode == 0, "Your code crashed with 10,000 letters:\n" + r.stderr[-800:]
    assert r.stdout.split() == [str(want)], f"10,000 letters: expected {want} bits, got {r.stdout.split()}."
