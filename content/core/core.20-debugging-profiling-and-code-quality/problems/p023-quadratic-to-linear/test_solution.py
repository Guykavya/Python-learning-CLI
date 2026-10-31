from solution import common_items


class Item:
    """A value that counts how often it is compared with ==."""

    eq_calls = 0

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        Item.eq_calls += 1
        return isinstance(other, Item) and self.value == other.value

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return f"Item({self.value})"


def items(values):
    return [Item(v) for v in values]   # new objects, so equal items are never the same object


def values(result):
    return [x.value for x in result]


def test_example():
    assert common_items([3, 1, 3, 2, 5], [5, 3, 3, 9]) == [3, 5], "Keep a's order (3 before 5) and list each item once."


def test_empty_inputs():
    assert common_items(["a", "b"], []) == [], "Nothing is common with an empty b."
    assert common_items([], [1, 2]) == [], "An empty a gives an empty result."
    assert common_items([], []) == [], "Two empty lists give an empty list."


def test_returns_list():
    got = common_items((1, 2, 3), {2, 3})
    assert got == [2, 3] and isinstance(got, list), f"Return a list in a's order even when the inputs are a tuple and a set; got {got!r}."


def test_duplicates_once_in_first_order():
    got = common_items(["x", "y", "x", "z", "y"], ["y", "x", "y"])
    assert got == ["x", "y"], f"Got {got}. Each common item appears once, at the place it FIRST appears in a."


def test_inputs_not_changed():
    a, b = [1, 2, 2, 3], [3, 2]
    common_items(a, b)
    assert a == [1, 2, 2, 3] and b == [3, 2], "Do not change a or b (no sorting or removing in place)."


def test_mixed_types():
    assert common_items([1, "1", 1.5, None], ["1", None, 2]) == ["1", None], "1 and '1' are different items; None is a normal item too."


def test_counted_items_correct():
    a = items([4, 1, 4, 7, 2, 9])
    b = items([2, 4, 4, 8])
    assert values(common_items(a, b)) == [4, 2], "With equal-but-different objects the result is the items 4 and 2, in a's order."


def test_work_is_linear():
    n = 400
    a = items(range(n))
    b = items(range(n // 2, n + n // 2))           # half of a is common
    Item.eq_calls = 0
    got = common_items(a, b)
    used = Item.eq_calls
    assert values(got) == list(range(n // 2, n)), "The common items are n//2 .. n-1, in order."
    limit = 4 * (len(a) + len(b))
    assert used <= limit, (
        f"common_items made {used:,} == comparisons for two lists of {n} items; a linear solution needs at most "
        f"about {limit:,}. `x in some_list` compares x with every item: build set(b) once and keep a set of "
        "items already added. (sorted(..., key=a.index) or result.count(x) are hidden list scans too.)"
    )


def test_work_scales_linearly():
    def work(n):
        a = items(range(n))
        b = items(range(n))
        Item.eq_calls = 0
        common_items(a, b)
        return Item.eq_calls

    small, big = work(200), work(800)
    assert big <= 6 * max(small, 1), (
        f"4x more input made {big:,} comparisons instead of {small:,} (x{big / max(small, 1):.1f}). Linear work "
        "grows about 4x; a quadratic solution grows about 16x."
    )
