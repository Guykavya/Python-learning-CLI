import random

from solution import merge


def model(intervals):
    """Paint every half-step on a number line and read the blocks back (small integer inputs only)."""
    covered = set()
    for s, e in intervals:
        for k in range(2 * s, 2 * e + 1):       # 2*x marks the point x, odd numbers the gaps between points
            covered.add(k)
    blocks = []
    for k in sorted(covered):
        if blocks and k == blocks[-1][1] + 1:
            blocks[-1][1] = k
        else:
            blocks.append([k, k])
    return [[a // 2, b // 2] for a, b in blocks]


def norm(result):
    return [list(iv) for iv in result]


def test_chapter_examples():
    assert norm(merge([(1, 3), (2, 6), (8, 10), (15, 18)])) == [[1, 6], [8, 10], [15, 18]], (
        "(1,3) and (2,6) overlap and become [1,6]; the others stay. Sort by start, then extend or open a block.")
    assert norm(merge([(1, 4), (4, 5)])) == [[1, 5]], (
        "Touching intervals MERGE here: (1,4) and (4,5) become [1,5]. Use `start <= current end`, not `<`.")
    assert norm(merge([(1, 10), (2, 3), (4, 5)])) == [[1, 10]], (
        "(2,3) lies inside (1,10): the end must stay 10. Extend with max(current end, e), not with e.")


def test_unsorted_input():
    assert norm(merge([(8, 10), (1, 3)])) == [[1, 3], [8, 10]], (
        "The input is not sorted. Sort by start first; the output must be sorted by start too.")
    assert norm(merge([[6, 8], [1, 9], [2, 4], [4, 7]])) == [[1, 9]], (
        "Unsorted lists that all lie inside [1,9]: one block. Did you sort before sweeping?")


def test_edge_cases():
    assert merge([]) == [], "An empty list has no busy periods: return []."
    assert norm(merge([(5, 7)])) == [[5, 7]], "One interval comes back unchanged (as a list [5, 7])."
    assert norm(merge([(3, 3), (3, 3)])) == [[3, 3]], "Two equal empty intervals at 3 merge into [3, 3]."
    assert norm(merge([(1, 2), (3, 4)])) == [[1, 2], [3, 4]], (
        "(1,2) and (3,4) do not touch (there is a gap between 2 and 3): two blocks.")


def test_returns_lists_and_keeps_input():
    data = [(1, 3), (2, 6)]
    copy = list(data)
    result = merge(data)
    assert data == copy, "Do not change the caller's list."
    assert all(isinstance(iv, list) for iv in result), (
        "Return [start, end] LISTS (the chapter's merge builds lists so that out[-1][1] can be changed).")


def test_input_lists_not_aliased():
    data = [[1, 3], [2, 6]]
    merge(data)
    assert data == [[1, 3], [2, 6]], (
        "The inner list [1, 3] of the INPUT was changed to [1, 6]. Append a new list [s, e] to the output, "
        "do not append the input's own list and then edit it.")


def test_random_against_model():
    rng = random.Random(7)
    for _ in range(500):
        n = rng.randint(0, 8)
        intervals = []
        for _ in range(n):
            s = rng.randint(0, 15)
            intervals.append((s, s + rng.randint(0, 4)))
        expected = model(intervals)
        got = norm(merge(list(intervals)))
        assert got == expected, (
            f"intervals={intervals}: expected {expected}, got {got}. Sort by start; if s <= end of the last "
            "block extend it with max(...), otherwise open a new block.")


def test_large_input_is_fast():
    intervals = [(i, i + 1) for i in range(100_000)]
    assert norm(merge(intervals)) == [[0, 100_000]], (
        "100,000 touching intervals merge into one block [0, 100000]. One sort and one pass are enough.")
