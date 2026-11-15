import pytest

from solution import ListNode, reverse_list


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


@pytest.mark.parametrize("values", [[], [1], [1, 2], [1, 2, 3], [1, 2, 3, 4], [5, 5, 1], list(range(10))])
def test_reverse(values):
    head = build(values)
    before = nodes(head)
    got = reverse_list(head)
    assert to_list(got) == values[::-1], (
        f"reverse_list({values}) should give {values[::-1]}, got {to_list(got)}. "
        "Return prev (the new head), not the old head.")
    check_same_nodes(before, got, f"reverse_list({values})")
    if values:
        assert got is before[-1], "The new head must be the old LAST node (the same object)."
        assert before[0].next is None, "The old head is now the tail: its next must be None."


def test_values_not_swapped():
    head = build([1, 2, 3])
    first = head
    got = reverse_list(head)
    assert first.val == 1, (
        "The node that held 1 must still hold 1: reverse the arrows, do not swap values between nodes.")
    assert got.val == 3


def test_two_nodes_no_cycle():
    head = build([1, 2])
    got = reverse_list(head)
    assert to_list(got) == [2, 1], (
        "Two nodes reversed: 2 -> 1 -> None. A cycle here usually means the old head kept its next.")


def test_long():
    values = list(range(10**5))
    got = reverse_list(build(values))
    assert to_list(got) == values[::-1], (
        "100,000 nodes must be reversed. If this raised RecursionError, use the loop version.")
