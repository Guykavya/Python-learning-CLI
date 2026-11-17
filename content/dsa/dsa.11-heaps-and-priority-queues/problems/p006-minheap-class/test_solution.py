import ast
import heapq
import pathlib
import random

import pytest

from solution import MinHeap

SOLUTION = pathlib.Path(__file__).with_name("solution.py")


def test_no_library_heap_or_sort():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    bad = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in ("sorted", "heapq"):
            bad.add(node.id)
        if isinstance(node, ast.Attribute) and node.attr == "sort":
            bad.add(".sort")
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [alias.name for alias in node.names] + [getattr(node, "module", None) or ""]
            if any(name.split(".")[0] == "heapq" for name in names):
                bad.add("heapq")
    assert not bad, (
        f"This problem is about building the heap yourself: found {sorted(bad)} in your code. "
        "Write the sift up / sift down loops by hand; heapq, sorted() and .sort() are not allowed here.")


class Counted:
    """A number that counts every comparison made with it (any of < <= > >=)."""
    comparisons = 0

    def __init__(self, v):
        self.v = v

    def __lt__(self, other):
        Counted.comparisons += 1
        return self.v < other.v

    def __le__(self, other):
        Counted.comparisons += 1
        return self.v <= other.v

    def __gt__(self, other):
        Counted.comparisons += 1
        return self.v > other.v

    def __ge__(self, other):
        Counted.comparisons += 1
        return self.v >= other.v


def drain(h):
    return [h.pop() for _ in range(len(h))]


def test_an_empty_heap():
    h = MinHeap()
    assert len(h) == 0, "A new heap has no items: len(MinHeap()) must be 0."
    with pytest.raises(IndexError):
        h.pop()
    with pytest.raises(IndexError):
        h.peek()


def test_the_example():
    h = MinHeap()
    for x in (4, 1, 7, 3):
        h.push(x)
    assert h.peek() == 1 and len(h) == 4, f"After pushing 4, 1, 7, 3 the smallest is 1 and len is 4; got peek {h.peek()}, len {len(h)}."
    assert drain(h) == [1, 3, 4, 7], "Popping must return the items from smallest to largest: [1, 3, 4, 7]."
    assert len(h) == 0, "After popping every item the heap is empty."


def test_peek_does_not_remove_and_pop_shrinks():
    h = MinHeap()
    for x in (5, 2, 9):
        h.push(x)
    assert h.peek() == 2 and h.peek() == 2, "peek must not remove the item: a second peek gives the same answer."
    assert len(h) == 3, "peek must not change len."
    assert h.pop() == 2 and len(h) == 2, "pop returns the smallest and shrinks the heap by one."
    assert h.peek() == 5, "After popping 2 the smallest is 5."


def test_one_item_heap_pop_leaves_it_empty_and_usable():
    h = MinHeap()
    h.push(7)
    assert h.pop() == 7, "pop of a one-item heap returns that item."
    assert len(h) == 0, "The heap is empty again."
    with pytest.raises(IndexError):
        h.pop()
    h.push(3)
    assert h.peek() == 3, "An emptied heap must be usable again."


def test_duplicates():
    h = MinHeap()
    for x in (3, 1, 3, 1, 2, 2):
        h.push(x)
    assert drain(h) == [1, 1, 2, 2, 3, 3], "Equal items are allowed and must all come out."


def test_strings_and_tuples():
    h = MinHeap(["pear", "apple", "fig", "mango"])
    assert drain(h) == ["apple", "fig", "mango", "pear"], "Strings compare with <: the heap must work for them too."
    t = MinHeap()
    for item in [(2, "b"), (1, "z"), (2, "a"), (1, "a")]:
        t.push(item)
    assert drain(t) == [(1, "a"), (1, "z"), (2, "a"), (2, "b")], "Tuples compare element by element."


def test_build_from_a_list():
    data = [5, 3, 8, 1, 9, 2]
    h = MinHeap(data)
    assert len(h) == 6 and h.peek() == 1, f"MinHeap([5, 3, 8, 1, 9, 2]) has 6 items and the smallest is 1; got len {len(h)}, peek {h.peek() if len(h) else None}."
    assert data == [5, 3, 8, 1, 9, 2], "The list you were given must stay as it was: copy it (list(items)), do not heapify it in place."
    assert drain(h) == [1, 2, 3, 5, 8, 9], "A heap built from a list must pop its items in sorted order. Did you sift down from the last parent back to the root?"


def test_build_from_other_iterables():
    assert drain(MinHeap((4, 2, 3))) == [2, 3, 4], "Any iterable must work: a tuple here."
    assert drain(MinHeap(range(10, 0, -1))) == list(range(1, 11)), "Any iterable must work: a range here."
    assert drain(MinHeap(x * 2 for x in (3, 1, 2))) == [2, 4, 6], "Any iterable must work: a generator here."
    assert drain(MinHeap([])) == [], "An empty list gives an empty heap."


def test_build_then_push_and_pop():
    rng = random.Random(9)
    for _ in range(200):
        data = [rng.randint(0, 30) for _ in range(rng.randint(0, 25))]
        h = MinHeap(data)
        model = sorted(data)
        for _ in range(10):
            x = rng.randint(0, 30)
            h.push(x)
            model.append(x)
            model.sort()
            if rng.random() < 0.5:
                assert h.pop() == model.pop(0), f"After building from {data} and some pushes, pop returned the wrong item."
        assert drain(h) == model, f"Building from {data} and then pushing: the pops come out in the wrong order."


def test_2000_random_operations_against_heapq():
    rng = random.Random(11)
    mine, model = MinHeap(), []
    for step in range(2000):
        if model and rng.random() < 0.45:
            got, want = mine.pop(), heapq.heappop(model)
            assert got == want, f"Step {step}: pop returned {got}, the smallest item is {want}. Is your sift_down picking the smaller child?"
        else:
            x = rng.randint(0, 40)                      # many equal values
            mine.push(x)
            heapq.heappush(model, x)
        assert len(mine) == len(model), f"Step {step}: len is {len(mine)}, it should be {len(model)}."
        if model:
            assert mine.peek() == model[0], f"Step {step}: peek returned {mine.peek()}, the smallest item is {model[0]}."


def test_building_from_a_list_is_bottom_up():
    n = 1000
    items = [Counted(v) for v in range(n, 0, -1)]       # descending: the worst case for n pushes
    Counted.comparisons = 0
    MinHeap(items)
    used = Counted.comparisons
    assert used <= 2 * n, (
        f"Building a heap from {n} items used {used} comparisons; the bottom-up method (sift_down from the last parent "
        f"back to the root) needs fewer than {2 * n}. Pushing the items one by one costs about {8 * n} here, "
        "because every new item climbs to the root.")


def test_push_and_pop_are_logarithmic():
    n = 1000
    rng = random.Random(5)
    values = list(range(n))
    rng.shuffle(values)
    h = MinHeap()
    Counted.comparisons = 0
    for v in values:
        h.push(Counted(v))
    for _ in range(n):
        h.pop()
    used = Counted.comparisons
    assert used <= 40 * n, (
        f"{n} pushes and {n} pops used {used} comparisons; a heap needs about {17 * n}. "
        "Do you search the whole list for the smallest item (min, or a scan) instead of sifting?")


def test_popped_items_are_the_pushed_objects():
    a, b = Counted(1), Counted(2)
    h = MinHeap([b, a])
    assert h.pop() is a and h.pop() is b, "pop must return the stored objects themselves, smallest first."
