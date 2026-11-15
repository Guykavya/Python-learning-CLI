import copy

from solution import flatten


def test_example():
    assert flatten([1, [2, [3]], 4]) == [1, 2, 3, 4], "flatten([1, [2, [3]], 4]) is [1, 2, 3, 4]. Did you append an inner result instead of extending?"


def test_already_flat():
    assert flatten([1, 2, 3]) == [1, 2, 3], "A flat list stays the same."


def test_empty():
    assert flatten([]) == [], "The empty list flattens to []."


def test_empty_inner_lists():
    assert flatten([[], [[]], 5]) == [5], "Empty inner lists add nothing."
    assert flatten([[[[]]]]) == [], "Only empty lists inside: the result is []."


def test_order_kept():
    assert flatten([[3, [2]], 1, [[0]]]) == [3, 2, 1, 0], "Keep the left-to-right order; do not sort."


def test_strings_and_tuples_are_atoms():
    assert flatten(["ab", ["c", (1, 2)], None]) == ["ab", "c", (1, 2), None], \
        "Only lists are opened: strings, tuples and None stay as single items."


def test_depth_50():
    xs = [7]
    for i in range(50):
        xs = [i, xs]
    want = list(range(49, -1, -1)) + [7]
    assert flatten(xs) == want, "A list nested 50 levels deep."


def test_input_not_changed():
    xs = [1, [2, [3, []]], [4]]
    before = copy.deepcopy(xs)
    flatten(xs)
    assert xs == before, "flatten must build a new list and leave the input (and inner lists) unchanged."


def test_two_calls_independent():
    flatten([1, [2]])
    assert flatten([3]) == [3], "The second call returned old values: do not keep the result in a default argument or a global."
