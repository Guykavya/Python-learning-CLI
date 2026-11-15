import pytest

from solution import ListNode, remove_nth_from_end


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


@pytest.mark.parametrize("values, n, why", [
    ([1, 2, 3, 4, 5], 2, "the example"),
    ([1, 2, 3, 4, 5], 1, "n = 1 removes the last node"),
    ([1, 2, 3, 4, 5], 5, "n = length removes the head: use a dummy"),
    ([7], 1, "removing the only node leaves None"),
    ([1, 2], 1, "two nodes, remove the last"),
    ([1, 2], 2, "two nodes, remove the first"),
])
def test_cases(values, n, why):
    head = build(values)
    before = nodes(head)
    got = remove_nth_from_end(head, n)
    i = len(values) - n
    want = values[:i] + values[i + 1:]
    assert to_list(got) == want, (
        f"remove_nth_from_end({values}, {n}) should give {want}, got {to_list(got)}: {why}. "
        "Off by one? fast must be n nodes ahead of slow, and slow starts on a dummy before the head.")
    kept = before[:i] + before[i + 1:]
    assert all(a is b for a, b in zip(kept, nodes(got))), "Keep the original nodes; only unlink one."


def test_all_positions():
    for size in range(1, 9):
        values = list(range(size))
        for n in range(1, size + 1):
            i = size - n
            got = to_list(remove_nth_from_end(build(values), n))
            assert got == values[:i] + values[i + 1:], f"remove_nth_from_end({values}, {n}) gave {got}."


def test_long():
    values = list(range(10**5))
    got = to_list(remove_nth_from_end(build(values), 50_000))
    assert got == values[:50_000] + values[50_001:], "100,000 nodes, remove the 50,000th from the end."
