from collections import Counter

from hypothesis import given, settings, strategies as st

from target import reverse, sorted_copy

numbers = st.lists(st.integers(min_value=-50, max_value=50), max_size=20)


@settings(derandomize=True, database=None, max_examples=100)
@given(numbers)
def test_reverse_keeps_the_length(xs):
    assert len(reverse(xs)) == len(xs), "reverse must not add or drop elements."


@settings(derandomize=True, database=None, max_examples=100)
@given(numbers)
def test_reverse_twice_is_the_original(xs):
    assert reverse(reverse(xs)) == xs, "Reversing twice must give the original list."


@settings(derandomize=True, database=None, max_examples=100)
@given(st.lists(st.integers(), min_size=1, max_size=20))
def test_reverse_swaps_the_ends(xs):
    out = reverse(xs)
    assert out[0] == xs[-1] and out[-1] == xs[0], "The last element must come first and the first last."


@settings(derandomize=True, database=None, max_examples=100)
@given(numbers)
def test_sorted_copy_is_ascending(xs):
    out = sorted_copy(xs)
    assert all(a <= b for a, b in zip(out, out[1:])), "Every element must be <= the next one."


@settings(derandomize=True, database=None, max_examples=100)
@given(numbers)
def test_sorted_copy_has_the_same_elements(xs):
    assert Counter(sorted_copy(xs)) == Counter(xs), "Same numbers, same counts (nothing lost, invented or changed)."


@settings(derandomize=True, database=None, max_examples=100)
@given(numbers)
def test_sorted_copy_leaves_the_input_alone(xs):
    before = list(xs)
    sorted_copy(xs)
    assert xs == before, "The caller's list must not change."
