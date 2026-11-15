import pytest

from solution import ListNode, find


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


@pytest.mark.parametrize("values, target, want, why", [
    ([4, 7, 1, 7], 7, 1, "return the FIRST match, not the last one"),
    ([4, 7, 1, 7], 4, 0, "the head is index 0"),
    ([4, 7, 1, 7], 1, 2, "count every node you pass"),
    ([4, 7, 1, 7], 9, -1, "a value that is not there gives -1"),
    ([], 4, -1, "the empty list (None) contains nothing"),
    ([3], 3, 0, "a single matching node is index 0"),
    ([1, 2, 3, 4, 5], 5, 4, "the last node is index len - 1"),
    ([0, None, ""], None, 1, "None is a value you can look for"),
    ([5, 0, 6], 0, 1, "a value 0 must be found too: stop at a None NODE, not a falsy value"),
    (["a", "b"], "b", 1, "strings work the same way"),
])
def test_find(values, target, want, why):
    head = build(values)
    got = find(head, target)
    assert got == want, f"find({values}, {target!r}) should be {want}, got {got!r}: {why}."
    assert to_list(head) == values, "find must not change the list."


def test_long():
    head = build(range(10**5))
    assert find(head, 99_999) == 99_999, "The last of 100,000 nodes is index 99,999."
    assert find(head, -5) == -1
