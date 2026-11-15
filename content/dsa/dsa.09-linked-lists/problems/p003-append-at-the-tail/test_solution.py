import pytest

from solution import ListNode, append


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


def test_append_to_empty():
    head = append(None, 5)
    assert isinstance(head, ListNode), (
        f"append(None, 5) should return the new node (it is the whole list), got {head!r}.")
    assert to_list(head) == [5], "Appending 5 to the empty list gives the list [5]."


@pytest.mark.parametrize("values", [[1], [1, 2], [4, 4, 4], [0, None]])
def test_append_to_non_empty(values):
    head = build(values)
    before = nodes(head)
    got = append(head, 99)
    assert got is head, (
        "Appending to a non-empty list keeps the same first node: return the head you were given "
        "(if you returned the walking variable, you returned a node near the end).")
    assert to_list(got) == values + [99], (
        f"append({values}, 99) should give {values + [99]}, got {to_list(got)}. "
        "Link the new node after the LAST node (stop when cur.next is None).")
    after = nodes(got)
    assert all(a is b for a, b in zip(before, after)), "The old nodes must stay the same objects, in the same order."


def test_new_node_is_last():
    head = append(build([1, 2]), 3)
    last = nodes(head)[-1]
    assert last.val == 3 and last.next is None, "The new node must be the last one: its next is None."


def test_repeated_appends():
    head = None
    for v in range(2000):
        head = append(head, v)
    assert to_list(head) == list(range(2000)), (
        "2,000 appends in a row should give 0, 1, ..., 1999. Always use the head that append returns.")
