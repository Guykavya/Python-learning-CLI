import ast
import heapq
import pathlib
import random

from solution import sift_down

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
        f"This problem is about writing the step yourself: found {sorted(bad)} in your code. "
        "Use a plain loop with the indexes of the children; heapq, sorted() and .sort() are not allowed here.")


def is_heap(a, n=None):
    n = len(a) if n is None else n
    return all(a[i] >= a[(i - 1) // 2] for i in range(1, n))


def model(a, i, n):
    """Expected list for DISTINCT values: the item sinks along the smaller children."""
    a = list(a)
    while True:
        kids = [c for c in (2 * i + 1, 2 * i + 2) if c < n]
        if not kids:
            return a
        c = min(kids, key=lambda k: a[k])
        if a[c] < a[i]:
            a[i], a[c] = a[c], a[i]
            i = c
        else:
            return a


def test_the_first_example():
    a = [9, 3, 2, 7, 4, 5, 6]
    sift_down(a, 0, 7)
    assert a == [2, 3, 5, 7, 4, 9, 6], (
        f"Expected [2, 3, 5, 7, 4, 9, 6], got {a}. 9 swaps with the SMALLER child 2 (not 3), "
        "then with the smaller child 5 of its new position.")


def test_items_at_index_n_or_later_are_not_part_of_the_heap():
    b = [9, 3, 2, 7, 4, 5, 1]
    sift_down(b, 0, 6)
    assert b == [2, 3, 5, 7, 4, 9, 1], (
        f"Expected [2, 3, 5, 7, 4, 9, 1], got {b}. With n = 6 the item at index 6 is not in the heap: "
        "check child < n (not child < len(a)), so that 1 is never moved up.")


def test_nothing_to_do():
    a = [1, 3, 2, 7, 4, 5, 6]
    sift_down(a, 0, 7)
    assert a == [1, 3, 2, 7, 4, 5, 6], f"The root 1 is not larger than its children: nothing may move, got {a}."
    b = [4, 4, 4]
    sift_down(b, 0, 3)
    assert b == [4, 4, 4], f"Equal items: nothing moves, got {b}."


def test_leaves_and_tiny_heaps():
    a = [7]
    sift_down(a, 0, 1)
    assert a == [7], "One item: nothing to do."
    b = [9, 1, 2, 3, 4]
    sift_down(b, 4, 5)
    assert b == [9, 1, 2, 3, 4], "Index 4 is a leaf when n = 5: it has no children, nothing may move."
    c = [9, 3]
    sift_down(c, 0, 2)
    assert c == [3, 9], f"[9, 3]: the root has only a left child, 3. Expected [3, 9], got {c}."


def test_the_last_parent_has_only_a_left_child():
    a = [1, 9, 2, 3]
    sift_down(a, 1, 4)
    assert a == [1, 3, 2, 9], (
        f"Index 1 has the children at 3 and 4, but with n = 4 only index 3 exists. Expected [1, 3, 2, 9], got {a}. "
        "Check that the right child exists (r < n) before reading it.")


def test_the_smaller_child_is_chosen_on_both_sides():
    a = [10, 2, 3, 20, 21, 22, 23]
    sift_down(a, 0, 7)
    assert a == [2, 10, 3, 20, 21, 22, 23], f"The left child 2 is smaller than the right child 3: 10 goes left. Got {a}."
    b = [10, 3, 2, 20, 21, 22, 23]
    sift_down(b, 0, 7)
    assert b == [2, 3, 10, 20, 21, 22, 23], f"The right child 2 is smaller than the left child 3: 10 goes right. Got {b}."
    c = [10, 2, 5, 3, 4, 22, 23]
    sift_down(c, 0, 7)
    assert c == [2, 3, 5, 10, 4, 22, 23], (
        f"10 swaps with 2, then with the smaller child 3 of its new position (3 < 4). Expected [2, 3, 5, 10, 4, 22, 23], got {c}. "
        "Compare the right child with the best so far, not with the item that is sinking.")


def test_a_middle_index():
    rng = random.Random(21)
    for _ in range(300):
        n = rng.randint(1, 40)
        a = rng.sample(range(10, 1000), n)
        heapq.heapify(a)
        i = rng.randrange(n)
        a[i] = rng.randint(1000, 2000)                  # larger than everything: broken only at i
        want = model(a, i, n)
        sift_down(a, i, n)
        assert a == want, f"sift_down at index {i} with n = {n}: expected {want}, got {a}."


def test_only_the_first_n_items_are_the_heap():
    rng = random.Random(22)
    for _ in range(300):
        m = rng.randint(1, 30)
        heap = rng.sample(range(10, 1000), m)
        heapq.heapify(heap)
        heap[0] = rng.randint(1000, 2000)
        tail = [-5, -6, -7]
        a = heap + tail
        want = model(heap, 0, m) + tail
        sift_down(a, 0, m)
        assert a == want, (
            f"With n = {m} the items {tail} behind the heap are not part of it and must stay: expected {want}, got {a}. "
            "Use n, not len(a), in the tests for the children.")


def test_duplicates_keep_the_same_items_and_a_valid_heap():
    rng = random.Random(23)
    for _ in range(300):
        n = rng.randint(1, 30)
        a = [rng.randint(0, 4) for _ in range(n)]
        heapq.heapify(a)
        a[0] = rng.randint(3, 8)
        before = sorted(a)
        sift_down(a, 0, n)
        assert sorted(a) == before, f"sift_down only swaps: the items must stay the same, {before} became {sorted(a)}."
        assert is_heap(a), f"{a} is not a min-heap after sift_down (duplicates are allowed)."


def test_a_big_heap():
    a = list(range(1, 1024))
    a[0] = 5000
    same = a
    sift_down(a, 0, len(a))
    assert same is a and is_heap(a) and a[0] == 2 and 5000 in a, "sift_down must change the list in place and leave a valid heap (10 levels here)."
