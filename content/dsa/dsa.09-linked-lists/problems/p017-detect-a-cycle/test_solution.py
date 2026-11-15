import tracemalloc

import pytest

from solution import has_cycle


class SNode:
    """The tests' node: __slots__ means no extra attributes can be stored on it, and
    __hash__ = None means it cannot go into a set or be a dict key."""
    __slots__ = ("val", "next")
    __hash__ = None

    def __init__(self, val, next=None):
        self.val = val
        self.next = next


def make(n, loop_to):
    """n nodes 0..n-1; the last node points to the node at index loop_to (None: no cycle)."""
    ns = [SNode(i) for i in range(n)]
    for a, b in zip(ns, ns[1:]):
        a.next = b
    if n and loop_to is not None:
        ns[-1].next = ns[loop_to]
    return (ns[0] if ns else None), ns


def links(ns):
    return [n.next for n in ns]


def call(head):
    try:
        return has_cycle(head)
    except TypeError as e:
        if "unhashable" in str(e):
            raise AssertionError(
                "Your function puts nodes into a set or dict. That costs O(n) memory; this problem asks for "
                "two pointers (slow and fast) and O(1) memory.") from None
        raise
    except AttributeError as e:
        if "next" not in str(e) and "val" not in str(e):
            raise AssertionError(
                f"Your function tries to store something on a node ({e}). Do not mark nodes; "
                "let a fast and a slow pointer find the cycle.") from None
        raise


@pytest.mark.parametrize("n, loop_to, want, why", [
    (0, None, False, "the empty list has no cycle"),
    (1, None, False, "one node pointing to None"),
    (1, 0, True, "one node pointing to itself"),
    (2, None, False, "two nodes, no cycle"),
    (2, 0, True, "two nodes pointing at each other"),
    (2, 1, True, "the second node points to itself"),
    (5, None, False, "five nodes, no cycle: fast must stop at the end"),
    (6, None, False, "six nodes, no cycle (even length)"),
    (4, 2, True, "the example: 4 points back to 3"),
    (10, 0, True, "the whole list is the cycle"),
    (10, 9, True, "a cycle of length one at the end"),
])
def test_cases(n, loop_to, want, why):
    head, ns = make(n, loop_to)
    before = links(ns)
    got = call(head)
    assert got is want, (
        f"has_cycle should be {want} ({why}), got {got!r}. Compare nodes with `is`, and check "
        "fast and fast.next before moving fast two steps.")
    assert links(ns) == before or all(a is b for a, b in zip(links(ns), before)), "has_cycle must not change any next pointer."


def test_equal_values_are_not_a_cycle():
    ns = [SNode(7) for _ in range(6)]
    for a, b in zip(ns, ns[1:]):
        a.next = b
    assert call(ns[0]) is False, (
        "Six different nodes that all hold 7 and end in None: no cycle. Compare the nodes (slow is fast), not their values.")


@pytest.mark.parametrize("loop_to", [None, 0, 50_000, 99_999])
def test_long_and_memory(loop_to):
    head, ns = make(10**5, loop_to)
    tracemalloc.start()
    try:
        tracemalloc.reset_peak()
        got = call(head)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert got is (loop_to is not None), f"100,000 nodes, cycle back to index {loop_to}: wrong answer {got!r}."
    assert peak < 200_000, (
        f"has_cycle used about {peak:,} bytes of extra memory on 100,000 nodes. Two pointers need almost "
        "none; a set or list of ids or nodes grows with n. Use slow and fast.")
