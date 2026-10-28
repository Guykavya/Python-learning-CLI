import itertools

from solution import merge_sorted


def limited(items, limit, name):
    """Yield items, but fail loudly if more than `limit` items are taken."""
    for i, item in enumerate(items):
        if i >= limit:
            raise AssertionError(f"merge_sorted took too many items from input {name}: it is not lazy enough.")
        yield item


def test_basic():
    assert list(merge_sorted([1, 4, 7], [2, 3, 9], [5])) == [1, 2, 3, 4, 5, 7, 9], "Always yield the smallest waiting item."


def test_empty_inputs():
    assert list(merge_sorted()) == [], "No inputs: nothing."
    assert list(merge_sorted([], [])) == [], "Only empty inputs: nothing."
    assert list(merge_sorted([], [1, 1], [1])) == [1, 1, 1], "Skip empty inputs; keep duplicates."


def test_uneven_lengths():
    assert list(merge_sorted([1, 2, 3, 4, 5, 6], [0])) == [0, 1, 2, 3, 4, 5, 6], (
        "When one input ends, keep going with the others. Remove a finished input, do not stop everything."
    )


def test_strings_and_generators():
    got = list(merge_sorted("adg", (c for c in "beh"), iter("cf")))
    assert got == list("abcdefgh"), "Any iterables work: strings, generators, iterators."


def test_key_and_ties():
    a = [{"t": 1, "src": "a"}, {"t": 5, "src": "a"}]
    b = [{"t": 1, "src": "b"}, {"t": 2, "src": "b"}]
    got = [r["src"] for r in merge_sorted(a, b, key=lambda r: r["t"])]
    assert got == ["a", "b", "b", "a"], (
        "Compare key(item). On equal keys the earlier input wins: use < (strict), and scan inputs in order."
    )


def test_ties_stable_many():
    a = [(1, "a1"), (1, "a2")]
    b = [(1, "b1")]
    c = [(1, "c1")]
    got = [name for _, name in merge_sorted(a, b, c, key=lambda p: p[0])]
    assert got == ["a1", "a2", "b1", "c1"], "All keys equal: every item of a, then b, then c."


def test_infinite_inputs():
    streams = [itertools.count(0, 3), itertools.count(1, 3), itertools.count(2, 3)]
    got = list(itertools.islice(merge_sorted(*streams), 10))
    assert got == list(range(10)), "merge_sorted must work on infinite inputs: never call list() or sorted() on them."


def test_holds_one_item_per_input():
    a = limited([1, 4, 7, 10], 2, "a")
    b = limited([2, 3, 8, 11], 3, "b")
    g = merge_sorted(a, b)
    got = [next(g), next(g), next(g), next(g)]
    assert got == [1, 2, 3, 4], "The first four merged items are 1, 2, 3, 4 (from a: 1, 4; from b: 2, 3, 8 waiting)."


def test_nothing_read_before_first_next():
    a = limited([1, 2], 0, "a")
    merge_sorted(a)
    # Creating the generator must not read anything; the limited input would raise.
