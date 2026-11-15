import tracemalloc

import pytest

from solution import detect_cycle


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
        return detect_cycle(head)
    except TypeError as e:
        if "unhashable" in str(e):
            raise AssertionError(
                "Your function puts nodes into a set or dict (O(n) memory). Use the two phases of Floyd's method.") from None
        raise


def test_example_tail_3_cycle_4():
    head, ns = make(7, 3)
    got = call(head)
    assert got is ns[3], (
        f"Tail 0 -> 1 -> 2, cycle 3 -> 4 -> 5 -> 6 -> 3: the cycle starts at the node holding 3, got "
        f"{getattr(got, 'val', got)!r}. Slow and fast meet at node 4; then move p from the head and slow from "
        "the meeting point ONE step each: they meet at 3.")


def test_no_cycle():
    for n in range(0, 7):
        head, ns = make(n, None)
        got = call(head)
        assert got is None, f"{n} nodes ending in None have no cycle: return None, got {got!r}."


def test_all_shapes():
    for tail in range(0, 7):
        for cycle in range(1, 7):
            head, ns = make(tail + cycle, tail)
            before = links(ns)
            got = call(head)
            assert got is ns[tail], (
                f"A tail of {tail} nodes and a cycle of {cycle} nodes: the cycle starts at the node holding {tail}, "
                f"got {getattr(got, 'val', got)!r}. "
                + ("When the head is inside the cycle, the answer is the head itself. " if tail == 0 else "")
                + "Return the node where p and slow meet in phase 2, not the phase-1 meeting point.")
            assert all(a is b for a, b in zip(links(ns), before)), "detect_cycle must not change any next pointer."


@pytest.mark.parametrize("loop_to", [None, 0, 12_345, 99_999])
def test_long_and_memory(loop_to):
    head, ns = make(10**5, loop_to)
    tracemalloc.start()
    try:
        tracemalloc.reset_peak()
        got = call(head)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    want = None if loop_to is None else ns[loop_to]
    assert got is want, f"100,000 nodes, cycle back to index {loop_to}: wrong node returned."
    assert peak < 200_000, (
        f"detect_cycle used about {peak:,} bytes of extra memory on 100,000 nodes; Floyd's method needs almost none.")
