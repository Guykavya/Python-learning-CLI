import ast
import pathlib
import random

import pytest

from solution import MaxHeap

SOLUTION = pathlib.Path(__file__).with_name("solution.py")


def test_uses_heapq_and_no_python_3_14_functions():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            used.add(node.attr)
        if isinstance(node, ast.Name):
            used.add(node.id)
    new_only = sorted(name for name in used if name in ("heappush_max", "heappop_max", "heapify_max", "heapreplace_max", "heappushpop_max"))
    assert not new_only, (
        f"You used {new_only}: these functions exist only in Python 3.14 and later, and this course supports 3.11. "
        "Store the negated numbers in a normal heapq min-heap instead.")
    assert "heappush" in used and "heappop" in used, (
        "This exercise is about heapq: use heapq.heappush and heapq.heappop on a list of negated numbers.")


def drain(h):
    return [h.pop() for _ in range(len(h))]


def test_an_empty_heap():
    h = MaxHeap()
    assert len(h) == 0, "A new MaxHeap has no items."
    with pytest.raises(IndexError):
        h.pop()
    with pytest.raises(IndexError):
        h.peek()


def test_the_example():
    h = MaxHeap([5, 1, 8, 3])
    assert (h.peek(), len(h)) == (8, 4), f"MaxHeap([5, 1, 8, 3]): the largest is 8 and len is 4, got peek {h.peek()}, len {len(h)}. Do you negate on the way out in peek?"
    h.push(10)
    assert drain(h) == [10, 8, 5, 3, 1], "The pops must give the items from largest to smallest: [10, 8, 5, 3, 1]."


def test_negative_numbers_zero_and_floats_come_out_unchanged():
    g = MaxHeap()
    for x in (-2.5, 0, -7):
        g.push(x)
    assert g.peek() == 0, f"peek must give 0 (the largest of -2.5, 0, -7), got {g.peek()}."
    assert drain(g) == [0, -2.5, -7], "Order must be 0, -2.5, -7: largest first, values unchanged (not negated)."
    h = MaxHeap([-3])
    assert h.peek() == -3, f"A stored -3 must be returned as -3, got {h.peek()}: negate on the way in and again on the way out, not twice in one place."
    assert h.pop() == -3, "pop must return -3 for a heap that holds only -3."


def test_peek_does_not_remove():
    h = MaxHeap([2, 9, 4])
    assert h.peek() == 9 and h.peek() == 9 and len(h) == 3, "peek must not remove the item: two peeks give 9 and the length stays 3."
    assert h.pop() == 9 and len(h) == 2, "pop returns the largest and shrinks the heap."


def test_big_integers_and_mixed_numbers():
    big = 10 ** 30
    h = MaxHeap([big + 1, big, 3, 2.5, 3.5])
    assert drain(h) == [big + 1, big, 3.5, 3, 2.5], "Big ints and floats must keep their exact values and the right order."


def test_duplicates():
    h = MaxHeap([4, 4, 1, 4, 1])
    assert drain(h) == [4, 4, 4, 1, 1], "Equal numbers are all kept."


def test_the_input_is_not_changed():
    data = [5, 1, 8, 3]
    h = MaxHeap(data)
    assert data == [5, 1, 8, 3], "MaxHeap(items) must not change the list it receives: build a new list of negated numbers."
    assert drain(h) == [8, 5, 3, 1], "The heap built from the list pops in descending order."
    t = (3, 9, 4)
    assert drain(MaxHeap(t)) == [9, 4, 3], "Any iterable must work (a tuple here)."
    assert drain(MaxHeap(x for x in (1, 2))) == [2, 1], "Any iterable must work (a generator here)."


def test_random_operations_against_a_sorted_model():
    rng = random.Random(10)
    for _ in range(100):
        start = [rng.randint(-20, 20) for _ in range(rng.randint(0, 10))]
        h = MaxHeap(start)
        model = sorted(start)
        for step in range(60):
            if model and rng.random() < 0.45:
                assert h.pop() == model.pop(), f"After starting from {start}, step {step}: pop must return the largest item."
            else:
                x = rng.choice([rng.randint(-20, 20), rng.random() * 10 - 5])
                h.push(x)
                model.append(x)
                model.sort()
            assert len(h) == len(model), f"Step {step}: len is {len(h)}, it should be {len(model)}."
            if model:
                assert h.peek() == model[-1], f"Step {step}: peek is {h.peek()}, the largest is {model[-1]}."
