import itertools

import solution
from solution import my_chain, my_enumerate, my_islice, my_zip


def test_chain_basic():
    assert list(my_chain([1, 2], "ab", [])) == [1, 2, "a", "b"], "Yield all items of each iterable in turn."
    assert list(my_chain()) == [], "No iterables: nothing."


def test_chain_lazy():
    got = list(itertools.islice(my_chain([1, 2], itertools.count(3)), 5))
    assert got == [1, 2, 3, 4, 5], "my_chain must be lazy: do not convert the inputs to lists."


def test_chain_iterator_once():
    it = iter([1, 2])
    assert list(my_chain(it, it)) == [1, 2], "The same iterator twice: the second time it is already used up, exactly like itertools.chain."


def test_enumerate():
    assert list(my_enumerate("xy", start=1)) == [(1, "x"), (2, "y")], "Index starts at start."
    assert list(my_enumerate("ab")) == [(0, "a"), (1, "b")], "The default start is 0."
    assert list(my_enumerate([])) == [], "Empty input: nothing."


def test_enumerate_lazy():
    got = list(itertools.islice(my_enumerate(itertools.count(100), 5), 2))
    assert got == [(5, 100), (6, 101)], "my_enumerate must be lazy (infinite input) and count from start."


def test_zip_matches_builtin():
    cases = [([1, 2, 3], "ab"), ("abc", [1, 2, 3]), ([], [1]), ([1], [2], [3, 4])]
    for case in cases:
        assert list(my_zip(*case)) == list(zip(*case)), f"my_zip{case} must stop at the shortest input."


def test_zip_no_arguments():
    assert list(my_zip()) == [], "my_zip() with no iterables yields nothing (not an endless stream of empty tuples)."


def test_zip_lazy():
    got = list(my_zip(itertools.count(), "abc"))
    assert got == [(0, "a"), (1, "b"), (2, "c")], "my_zip with one infinite input must stop when the short one ends."


def test_zip_loses_same_item_as_builtin():
    a = iter([1, 2, 3])
    b = iter(["x"])
    list(my_zip(a, b))
    assert next(a) == 3, "Like the real zip, my_zip asks a first and loses item 2 when b runs out."


def test_zip_does_not_raise_runtime_error():
    assert list(my_zip([1], [])) == [], "End the generator with 'return', not 'raise StopIteration' (that becomes RuntimeError)."


def test_islice_matches_builtin():
    for start, stop in [(2, 5), (0, 3), (0, 0), (4, 2), (5, 100), (0, None), (3, None)]:
        assert list(my_islice("abcdefg", start, stop)) == list(itertools.islice("abcdefg", start, stop)), (
            f"my_islice('abcdefg', {start}, {stop}) must match itertools.islice."
        )


def test_islice_infinite():
    got = list(my_islice(itertools.count(), 10, 13))
    assert got == [10, 11, 12], "my_islice must stop at stop, even on an infinite input."


def test_islice_does_not_over_consume():
    it = iter(range(10))
    assert list(my_islice(it, 1, 3)) == [1, 2], "Positions 1 and 2."
    assert next(it) == 3, "my_islice took one item too many. Stop right after position stop - 1, do not read another item."


def test_islice_stop_zero_consumes_nothing():
    it = iter(range(10))
    assert list(my_islice(it, 0, 0)) == [], "stop 0: nothing."
    assert next(it) == 0, "With stop <= start, do not take any item."


def test_no_itertools_used():
    source = open(solution.__file__, encoding="utf-8").read()
    assert "import itertools" not in source and "from itertools" not in source, "Do not import itertools: build them yourself."
