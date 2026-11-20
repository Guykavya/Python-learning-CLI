import ast
import heapq
import pathlib
import random

from solution import sift_up

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
        "Use a plain loop with the index of the parent; heapq, sorted() and .sort() are not allowed here.")


def is_heap(a):
    return all(a[i] >= a[(i - 1) // 2] for i in range(1, len(a)))


def model(a, i):
    """The expected list: the item at i is moved up, every larger parent on the path moves down one level."""
    a = list(a)
    x = a[i]
    while i > 0 and x < a[(i - 1) // 2]:
        a[i] = a[(i - 1) // 2]
        i = (i - 1) // 2
    a[i] = x
    return a


def test_the_example():
    a = [2, 5, 3, 9, 6, 1]
    sift_up(a, 5)
    assert a == [1, 5, 2, 9, 6, 3], (
        f"Expected [1, 5, 2, 9, 6, 3], got {a}. The item 1 (index 5) swaps with its parent 3 (index 2), "
        "then with its parent 2 (index 0). After each swap the item has a new index.")


def test_nothing_to_do_when_the_parent_is_not_larger():
    a = [1, 3, 2, 7]
    sift_up(a, 3)
    assert a == [1, 3, 2, 7], f"7 is larger than its parent 3: nothing may move, got {a}."
    b = [4, 4, 4]
    sift_up(b, 2)
    assert b == [4, 4, 4], f"Equal items are in order already (strict <): got {b}."


def test_the_root_and_a_single_item():
    a = [5]
    sift_up(a, 0)
    assert a == [5], "A single item is a heap already."
    b = [1, 2, 3]
    sift_up(b, 0)
    assert b == [1, 2, 3], "Index 0 is the root: it has no parent, so nothing moves."


def test_a_new_smallest_item_reaches_the_root():
    a = [2, 5, 3, 9, 6, 4, 8, 12, 10]
    a.append(1)
    sift_up(a, len(a) - 1)
    assert a[0] == 1, f"The new item 1 is the smallest: it must end at index 0, got {a}. Does your loop stop too early (while i > 1, or if instead of while)?"
    assert a == [1, 2, 3, 9, 5, 4, 8, 12, 10, 6], f"Expected [1, 2, 3, 9, 5, 4, 8, 12, 10, 6], got {a}."


def test_the_path_moves_down_and_the_rest_stays():
    a = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]
    a[12] = 5                                           # decrease-key at a leaf: path 12 -> 5 -> 2 -> 0
    sift_up(a, 12)
    assert a == [5, 20, 10, 40, 50, 30, 70, 80, 90, 100, 110, 120, 60, 140, 150], (
        f"Only the items on the path from index 12 to the root move: 60 -> 30 -> 10 down one level each. Got {a}.")


def test_random_push_sequences_against_the_model():
    rng = random.Random(3)
    for _ in range(300):
        values = rng.sample(range(1000), rng.randint(1, 40))
        a = values[:-1]
        heapq.heapify(a)
        a.append(values[-1])
        want = model(a, len(a) - 1)
        sift_up(a, len(a) - 1)
        assert a == want, f"After pushing {values[-1]} onto a heap of {len(values) - 1} items the list should be {want}, got {a}."
        assert is_heap(a), f"{a} is not a min-heap after sift_up."


def test_decrease_key_at_any_index():
    rng = random.Random(4)
    for _ in range(300):
        n = rng.randint(1, 40)
        a = rng.sample(range(10, 1000), n)
        heapq.heapify(a)
        i = rng.randrange(n)
        a[i] = rng.randint(0, 9)                        # smaller than everything: the heap is broken only at i
        want = model(a, i)
        sift_up(a, i)
        assert a == want, f"decrease-key at index {i}: expected {want}, got {a}."


def test_duplicates_keep_the_same_items_and_a_valid_heap():
    rng = random.Random(5)
    for _ in range(300):
        a = [rng.randint(0, 4) for _ in range(rng.randint(1, 30))]
        a_tail = a.pop()
        heapq.heapify(a)
        a.append(a_tail)
        before = sorted(a)
        sift_up(a, len(a) - 1)
        assert sorted(a) == before, f"sift_up must only swap items, never lose or invent one: {before} became {sorted(a)}."
        assert is_heap(a), f"{a} is not a min-heap after sift_up (duplicates are allowed)."


def test_it_works_in_place_and_big():
    a = list(range(1, 1024))                            # a heap with 10 levels
    a.append(0)
    same = a
    sift_up(a, len(a) - 1)
    assert same is a and a[0] == 0 and is_heap(a), "sift_up must change the list you pass in (in place); the new smallest item must reach the root."
