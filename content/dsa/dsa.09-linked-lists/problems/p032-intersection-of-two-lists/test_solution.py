import tracemalloc

import pytest

from solution import get_intersection


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


def shared(xs, ys, zs):
    """Lists xs + zs and ys + zs that share the zs nodes. Returns (a, b, first shared node, all nodes)."""
    tail, _ = chain(zs)
    a, an = chain(xs, tail)
    b, bn = chain(ys, tail)
    return a, b, tail, an + bn + all_nodes(tail)


def chain(values, rest=None):
    head = rest
    made = []
    for v in reversed(values):
        head = SNode(v, head)
        made.append(head)
    return head, made


def all_nodes(head):
    out = []
    while head is not None:
        out.append(head)
        head = head.next
    return out


def call(a, b):
    try:
        return get_intersection(a, b)
    except TypeError as e:
        if "unhashable" in str(e):
            raise AssertionError("Do not put nodes into a set: use two pointers (O(1) memory).") from None
        raise


@pytest.mark.parametrize("xs, ys, zs, why", [
    ([4, 1], [5, 6, 1], [8, 4, 5], "the example: equal values 1 before the shared part are different nodes"),
    ([1, 2, 3], [], [7], "b is only the shared part"),
    ([], [], [1, 2], "both lists are the same list: the head is the answer"),
    ([1], [2, 3, 4, 5, 6], [9], "very different lengths"),
    ([1, 2], [3, 4], [5], "only the last node is shared"),
])
def test_shared(xs, ys, zs, why):
    a, b, want, ns = shared(xs, ys, zs)
    before = [n.next for n in ns]
    got = call(a, b)
    assert got is want, (
        f"a = {xs + zs}, b = {ys + zs} share the nodes from value {zs[0]} on ({why}). Expected that node, got "
        f"{getattr(got, 'val', got)!r}. Compare nodes with `is`, never values.")
    assert all(n.next is m for n, m in zip(ns, before)), "get_intersection must not change any next pointer."


@pytest.mark.parametrize("xs, ys", [([1, 2], [1, 2]), ([1, 2, 3], [9]), ([], [1]), ([], []), ([5], [])])
def test_not_shared(xs, ys):
    a, _ = chain(xs)
    b, _ = chain(ys)
    got = call(a, b)
    assert got is None, (
        f"a = {xs} and b = {ys} are separate lists (equal values are not shared nodes): expected None, got "
        f"{getattr(got, 'val', got)!r}. Both pointers reach None at the same time after switching once.")


def test_long_and_memory():
    a, b, want, _ = shared(list(range(60_000)), list(range(10_000)), list(range(40_000)))
    tracemalloc.start()
    try:
        tracemalloc.reset_peak()
        got = call(a, b)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert got is want, "Long lists of different lengths: wrong node."
    assert peak < 200_000, f"get_intersection used about {peak:,} bytes of extra memory; two pointers need O(1)."
