import itertools

import pytest

from solution import shares, stats


def no_lists_allowed(items):
    """A plain generator: it can be read only once, like real streamed data."""
    yield from items


def test_stats_on_list():
    assert stats([4, 9, 2]) == (3, 15, 9), "count 3, total 15, largest 9."


def test_stats_on_generator():
    assert stats(x for x in [4, 9, 2]) == (3, 15, 9), (
        "With a generator, list(numbers) uses it up, so sum() and max() see nothing. "
        "Make one loop that updates count, total and largest together."
    )


def test_stats_empty():
    assert stats(iter([])) == (0, 0, None), "No numbers: (0, 0, None). Do not call max() on an empty input."
    assert stats([]) == (0, 0, None), "No numbers: (0, 0, None)."


def test_stats_negative_numbers():
    assert stats(no_lists_allowed([-5, -2, -9])) == (3, -16, -2), (
        "Largest of negative numbers is -2. Do not start 'largest' at 0; start it at None or the first item."
    )


def test_stats_large_lazy_input():
    big = itertools.islice(itertools.count(1), 200_000)
    assert stats(big) == (200_000, 20_000_100_000, 200_000), "One pass over a long iterator should work and be fast."


def test_stats_range():
    assert stats(range(1, 5)) == (4, 10, 4), "Any iterable must work, also range."


def test_shares_on_list():
    assert shares([1, 1, 2]) == [0.25, 0.25, 0.5], "Each number divided by the total 4."


def test_shares_on_generator():
    assert shares(x for x in [1, 1, 2]) == [0.25, 0.25, 0.5], (
        "sum() used up the generator, so the list comprehension saw nothing. "
        "Save the items in a list once, then use that list twice."
    )


def test_shares_zero_total():
    with pytest.raises(ValueError):
        shares([5, -5])
    with pytest.raises(ValueError):
        shares(x for x in [])
