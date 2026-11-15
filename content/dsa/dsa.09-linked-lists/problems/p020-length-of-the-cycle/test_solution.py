import tracemalloc

from solution import cycle_length


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
        return cycle_length(head)
    except TypeError as e:
        if "unhashable" in str(e):
            raise AssertionError("Do not put nodes into a set or dict: use the meeting point and walk once round.") from None
        raise


def test_example():
    head, ns = make(7, 3)
    got = call(head)
    assert got == 4, (
        f"Tail 0 -> 1 -> 2, cycle 3 -> 4 -> 5 -> 6 -> 3: the cycle has 4 nodes, got {got!r}. "
        "Count the steps from the meeting node until you are back on the SAME node.")


def test_no_cycle():
    for n in range(0, 6):
        head, _ = make(n, None)
        got = call(head)
        assert got == 0, f"{n} nodes ending in None: no cycle, so the length is 0, got {got!r}."


def test_self_loop():
    head, _ = make(1, 0)
    got = call(head)
    assert got == 1, f"One node pointing to itself is a cycle of length 1, got {got!r} (off by one in the count?)."


def test_all_shapes():
    for tail in range(0, 6):
        for cycle in range(1, 8):
            head, ns = make(tail + cycle, tail)
            before = links(ns)
            got = call(head)
            assert got == cycle, (
                f"A tail of {tail} and a cycle of {cycle} nodes: expected {cycle}, got {got!r}. "
                "Counting from the head would include the tail; count from the meeting point.")
            assert all(a is b for a, b in zip(links(ns), before)), "cycle_length must not change any next pointer."


def test_long_and_memory():
    head, _ = make(10**5, 30_000)
    tracemalloc.start()
    try:
        tracemalloc.reset_peak()
        got = call(head)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert got == 70_000, f"100,000 nodes, the last points back to index 30,000: cycle length 70,000, got {got!r}."
    assert peak < 200_000, f"cycle_length used about {peak:,} bytes of extra memory; two pointers and a counter need almost none."
