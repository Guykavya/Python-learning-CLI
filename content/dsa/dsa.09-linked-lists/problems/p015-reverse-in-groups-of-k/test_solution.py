import pytest

from solution import ListNode, reverse_k_group


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


def expected(values, k):
    out = []
    for i in range(0, len(values), k):
        part = values[i:i + k]
        out += part[::-1] if len(part) == k else part
    return out


@pytest.mark.parametrize("values, k, why", [
    ([1, 2, 3, 4, 5], 2, "two full pairs, the last node stays"),
    ([1, 2, 3, 4, 5], 3, "one full group, the last two nodes stay in their order"),
    ([1, 2, 3, 4, 5, 6], 3, "two full groups, nothing left over"),
    ([1, 2, 3], 1, "k = 1: every group has one node, nothing changes"),
    ([1, 2, 3], 3, "one group that is the whole list"),
    ([1, 2], 3, "k larger than the list: nothing changes"),
    ([], 2, "the empty list"),
])
def test_cases(values, k, why):
    head = build(values)
    before = nodes(head)
    got = reverse_k_group(head, k)
    want = expected(values, k)
    assert to_list(got) == want, (
        f"reverse_k_group({values}, {k}) should give {want}, got {to_list(got)}: {why}. "
        "Check that each reversed group is connected to the group before it AND to the rest after it.")
    check_same_nodes(before, got, f"reverse_k_group({values}, {k})")


def test_brute_force_compare():
    for n in range(0, 13):
        values = list(range(1, n + 1))
        for k in range(1, 7):
            got = to_list(reverse_k_group(build(values), k))
            assert got == expected(values, k), (
                f"reverse_k_group({values}, {k}) gave {got}, should be {expected(values, k)}. "
                "If only the tail is wrong: a last group shorter than k must not be reversed.")


def test_long():
    values = list(range(10**5))
    got = to_list(reverse_k_group(build(values), 7))
    assert got == expected(values, 7), "100,000 nodes in groups of 7; use loops, not recursion."
