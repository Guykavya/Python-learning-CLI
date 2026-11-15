import tracemalloc

import pytest

from solution import ListNode, reorder_list


def build(values):
    """Make a chain of ListNode from a Python list and return its head (None if empty)."""
    dummy = ListNode(0)
    tail = dummy
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next


def nodes(head, limit=10**6):
    """The nodes of a chain, in order. A cycle stops the walk with a message instead of hanging."""
    out, seen = [], set()
    cur = head
    while cur is not None:
        if id(cur) in seen:
            raise AssertionError(
                f"your list has a cycle: after {len(out)} nodes the walk reached the node with value {cur.val!r} "
                "again. Some next pointer points back into the list; did the last node keep an old next "
                "instead of None?")
        if len(out) >= limit:
            raise AssertionError(f"your list has more than {limit:,} nodes: the tests never build lists that long.")
        seen.add(id(cur))
        out.append(cur)
        cur = cur.next
    return out


def to_list(head):
    return [n.val for n in nodes(head)]


def check_same_nodes(before, head, what):
    """Nothing lost, nothing new: the chain at head holds exactly the node objects in `before`."""
    after = nodes(head)
    had = {id(n) for n in before}
    has = {id(n) for n in after}
    lost = [n.val for n in before if id(n) not in has]
    new = [n.val for n in after if id(n) not in had]
    assert not lost, (f"{what}: nodes with values {lost[:6]} were lost. A next pointer was overwritten "
                      "before its old value was saved in a variable.")
    assert not new, (f"{what}: the result contains new nodes (values {new[:6]}). Rewire the existing "
                     "nodes instead of creating new ones.")


def expected(values):
    out, i, j = [], 0, len(values) - 1
    while i <= j:
        out.append(values[i])
        if i != j:
            out.append(values[j])
        i += 1
        j -= 1
    return out


@pytest.mark.parametrize("n", range(0, 10))
def test_lengths(n):
    values = list(range(1, n + 1))
    head = build(values)
    before = nodes(head)
    ret = reorder_list(head)
    assert ret is None, "reorder_list changes the list in place and returns None."
    want = expected(values)
    assert to_list(head) == want, (
        f"reorder_list on {values} should give {want}, got {to_list(head)}. The first node stays first. "
        "Cut the list after the first half (slow.next = None) before reversing the second half.")
    check_same_nodes(before, head, f"reorder_list({values})")


def test_example():
    head = build([1, 2, 3, 4, 5])
    reorder_list(head)
    assert to_list(head) == [1, 5, 2, 4, 3], "1 2 3 4 5 becomes 1 5 2 4 3 (first, last, second, second-last, middle)."


def test_long_and_memory():
    values = list(range(10**5))
    head = build(values)
    tracemalloc.start()
    try:
        tracemalloc.reset_peak()
        reorder_list(head)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert to_list(head) == expected(values), "100,000 nodes reordered."
    assert peak < 200_000, (
        f"reorder_list used about {peak:,} bytes of extra memory. A Python list of nodes grows with n; "
        "middle + reverse + weave needs O(1).")
