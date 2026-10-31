import copy

from solution import merge_intervals


def test_the_example_that_always_worked():
    assert merge_intervals([[1, 3], [2, 6], [8, 10]]) == [[1, 6], [8, 10]], (
        "The basic overlapping case is broken. Overlapping intervals must merge into one."
    )


def test_touching_intervals_merge():
    assert merge_intervals([[9, 10], [10, 11]]) == [[9, 11]], (
        "Intervals that TOUCH (10 == 10) must merge. 'start < last_end' is off by one: use <=."
    )


def test_contained_interval_does_not_shrink():
    assert merge_intervals([[9, 17], [10, 11]]) == [[9, 17]], (
        "The end became 11: setting last_end = end shrinks the block when the new interval is "
        "inside it. Keep the larger end: max(last_end, end)."
    )
    assert merge_intervals([[1, 10], [2, 3], [4, 12]]) == [[1, 12]], (
        "A short interval inside a long one must not cut the long one's end."
    )


def test_unsorted_input_is_sorted_in_output():
    assert merge_intervals([[8, 10], [1, 3], [2, 6]]) == [[1, 6], [8, 10]], (
        "Sort by start first, otherwise overlapping intervals are not next to each other."
    )


def test_caller_list_order_is_unchanged():
    bookings = [[8, 10], [1, 3], [2, 6]]
    before = copy.deepcopy(bookings)
    merge_intervals(bookings)
    assert bookings == before, (
        f"The caller's list changed to {bookings}. list.sort() sorts IN PLACE; use sorted(...), "
        "which returns a new list. Also never write into the caller's [start, end] pairs."
    )


def test_caller_pairs_are_not_changed():
    bookings = [[1, 3], [2, 6]]
    merge_intervals(bookings)
    assert bookings == [[1, 3], [2, 6]], (
        f"The caller's pair became {bookings[0]}. merged[0] IS the caller's [1, 3] list (an "
        "alias), so 'last[1] = ...' writes into it. Append a NEW list: [start, end]."
    )


def test_result_does_not_share_lists_with_input():
    bookings = [[1, 2], [5, 6]]
    result = merge_intervals(bookings)
    assert result == [[1, 2], [5, 6]], "Non-overlapping intervals stay as they are."
    assert all(r is not b for r in result for b in bookings), (
        "The result contains the caller's own list objects. Changing the result later would "
        "change the caller's data. Build new [start, end] lists."
    )


def test_empty_and_single():
    assert merge_intervals([]) == [], "No intervals: return [], do not index [0] of an empty list."
    single = [[4, 7]]
    result = merge_intervals(single)
    assert result == [[4, 7]], "One interval comes back as it is."
    assert result[0] is not single[0], "Even a single interval must be a new list in the result."


def test_tuples_are_accepted():
    assert merge_intervals([(1, 2), (2, 4)]) == [[1, 4]], (
        "Tuples cannot be changed in place ('last[1] = ...' raises TypeError). Build your own "
        "[start, end] lists for the result."
    )
    assert merge_intervals([(5, 6)]) == [[5, 6]], "The result is a list of LISTS, even for tuple input."


def test_zero_length_and_duplicates():
    assert merge_intervals([[3, 3], [3, 3], [1, 2]]) == [[1, 2], [3, 3]], (
        "Zero-length and duplicate intervals still merge correctly."
    )
    assert merge_intervals([[1, 5], [1, 2], [6, 7]]) == [[1, 5], [6, 7]], (
        "Same start: the longer one must not be cut short."
    )
