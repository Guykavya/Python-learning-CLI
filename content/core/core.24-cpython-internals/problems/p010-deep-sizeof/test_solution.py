import sys

from solution import deep_size


class Box:
    def __init__(self):
        self.payload = "x" * 10_000


def test_leaf_object():
    n = int("123456789")
    assert deep_size(n) == sys.getsizeof(n), "A non-container counts with its own getsizeof only."


def test_list_adds_its_items():
    a, b = int("1000"), int("2000")
    data = [a, b]
    assert deep_size(data) == sys.getsizeof(data) + sys.getsizeof(a) + sys.getsizeof(b), (
        "deep_size of a list = the list itself plus each item."
    )


def test_bigger_than_shallow():
    text = "".join(["word"] * 2000)
    holder = [text]
    assert deep_size(holder) > sys.getsizeof(holder) + 7000, (
        "getsizeof([text]) does not include the 8,000-character string; deep_size must add it."
    )


def test_same_object_counted_once():
    s = "".join(["ab"] * 100)
    data = [s, s, s]
    assert deep_size(data) == sys.getsizeof(data) + sys.getsizeof(s), (
        "The same object reached three times takes memory once. Track the ids you have already counted."
    )


def test_equal_but_separate_objects_counted_twice():
    a = int("1000")
    b = int("1000")
    data = [a, b]
    assert deep_size(data) == sys.getsizeof(data) + sys.getsizeof(a) + sys.getsizeof(b), (
        "a == b, but they are two objects in memory. Compare by id(), not by value (a set of values merges them)."
    )


def test_nested_dict_keys_and_values():
    inner = [float("1.5"), float("2.5")]
    data = {"prices": inner, "count": int("70000")}
    expected = (sys.getsizeof(data) + sys.getsizeof("prices") + sys.getsizeof("count")
                + sys.getsizeof(inner) + sys.getsizeof(inner[0]) + sys.getsizeof(inner[1])
                + sys.getsizeof(data["count"]))
    assert deep_size(data) == expected, "Count the dict, every key, every value, and look inside nested containers."


def test_tuple_set_frozenset():
    x, y = float("0.25"), float("0.75")
    for container in [(x, y), {x, y}, frozenset([x, y])]:
        assert deep_size(container) == sys.getsizeof(container) + sys.getsizeof(x) + sys.getsizeof(y), (
            f"Look inside {type(container).__name__} objects too."
        )


def test_shared_inner_list():
    inner = [float("9.5")]
    outer = [inner, inner]
    assert deep_size(outer) == sys.getsizeof(outer) + sys.getsizeof(inner) + sys.getsizeof(inner[0]), (
        "Lists are unhashable, so you cannot put them in a set; put their id() in the set instead."
    )


def test_cycle_terminates():
    loop = []
    loop.append(loop)
    assert deep_size(loop) == sys.getsizeof(loop), "A list containing itself is counted once, and the function must stop."
    a, b = [], []
    a.append(b)
    b.append(a)
    assert deep_size(a) == sys.getsizeof(a) + sys.getsizeof(b), "A two-list cycle: each list once."


def test_other_objects_not_opened():
    box = Box()
    assert deep_size(box) == sys.getsizeof(box), "Only the five container types are opened; a Box counts by itself."
    assert deep_size([box]) == sys.getsizeof([box]) + sys.getsizeof(box), "A Box inside a list: list plus box."
