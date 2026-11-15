import pytest

from solution import ListNode, middle_node


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


@pytest.mark.parametrize("n", range(1, 12))
def test_every_length(n):
    head = build(list(range(1, n + 1)))
    ns = nodes(head)
    got = middle_node(head)
    want = ns[n // 2]
    assert got is want, (
        f"For {n} nodes the middle is the node with value {want.val} (index {n // 2}), got "
        f"{getattr(got, 'val', got)!r}. "
        + ("For an even length return the SECOND middle: loop while fast and fast.next." if n % 2 == 0 else
           "Move slow one step and fast two steps per round.")
        + " Return the node itself, not its value.")
    assert to_list(head) == list(range(1, n + 1)), "middle_node must not change the list."


def test_even_returns_second_middle():
    got = middle_node(build([1, 2, 3, 4, 5, 6]))
    assert got.val == 4, f"1..6 has middles 3 and 4: return the second one (4), got {got.val}."


def test_long():
    head = build(range(10**5 + 1))
    assert middle_node(head).val == 50_000, "100,001 nodes: the middle is index 50,000."
