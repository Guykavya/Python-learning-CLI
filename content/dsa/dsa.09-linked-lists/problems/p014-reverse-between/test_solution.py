import pytest

from solution import ListNode, reverse_between


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


def expected(values, left, right):
    i, j = left - 1, right
    return values[:i] + values[i:j][::-1] + values[j:]


@pytest.mark.parametrize("values, left, right, why", [
    ([1, 2, 3, 4, 5], 2, 4, "the example: the middle three nodes"),
    ([1, 2, 3], 1, 3, "the whole list: left = 1 changes the head"),
    ([1, 2, 3, 4], 1, 2, "a range at the front"),
    ([1, 2, 3, 4], 3, 4, "a range at the end: the reversed part must end with next = None"),
    ([1, 2, 3], 2, 2, "a range of one node changes nothing"),
    ([9], 1, 1, "a list of one node"),
])
def test_cases(values, left, right, why):
    head = build(values)
    before = nodes(head)
    got = reverse_between(head, left, right)
    want = expected(values, left, right)
    assert to_list(got) == want, (
        f"reverse_between({values}, {left}, {right}) should give {want}, got {to_list(got)}: {why}. "
        "After reversing, connect the node before the range to the new first node, and the old first node to the node after the range.")
    check_same_nodes(before, got, f"reverse_between({values}, {left}, {right})")


def test_every_range():
    for n in range(1, 8):
        values = list(range(1, n + 1))
        for left in range(1, n + 1):
            for right in range(left, n + 1):
                got = to_list(reverse_between(build(values), left, right))
                assert got == expected(values, left, right), (
                    f"reverse_between({values}, {left}, {right}) gave {got}, should be {expected(values, left, right)}.")


def test_long():
    values = list(range(10**5))
    got = to_list(reverse_between(build(values), 2, 10**5 - 1))
    assert got == expected(values, 2, 10**5 - 1), "A long range in a list of 100,000 nodes; use loops."
