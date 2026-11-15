import random

import pytest

from solution import ListNode, merge_two


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


@pytest.mark.parametrize("xs, ys", [
    ([1, 2, 4], [1, 3, 4]),
    ([], []),
    ([], [0]),
    ([5], []),
    ([1, 2, 3], [4, 5, 6]),
    ([4, 5, 6], [1, 2, 3]),
    ([2, 2, 2], [2, 2]),
    ([1, 5, 9], [2, 3, 4, 10, 11]),
])
def test_cases(xs, ys):
    a, b = build(xs), build(ys)
    na, nb = nodes(a), nodes(b)
    got = merge_two(a, b)
    want = sorted(xs + ys)
    assert to_list(got) == want, (
        f"merge_two({xs}, {ys}) should give {want}, got {to_list(got)}. "
        "When one list runs out, link the whole rest of the other one.")
    check_same_nodes(na + nb, got, f"merge_two({xs}, {ys})")


def test_stable():
    xs, ys = [1, 2, 2, 3], [2, 2, 4]
    a, b = build(xs), build(ys)
    from_a = {id(n) for n in nodes(a)}
    got = nodes(merge_two(a, b))
    twos = ["a" if id(n) in from_a else "b" for n in got if n.val == 2]
    assert twos == ["a", "a", "b", "b"], (
        f"The 2s come from {twos}; on a tie the node of a must come first. Take from b only when b.val < a.val (strictly).")


def test_random():
    rng = random.Random(23)
    for _ in range(300):
        xs = sorted(rng.randint(0, 9) for _ in range(rng.randint(0, 8)))
        ys = sorted(rng.randint(0, 9) for _ in range(rng.randint(0, 8)))
        got = to_list(merge_two(build(xs), build(ys)))
        assert got == sorted(xs + ys), f"merge_two({xs}, {ys}) gave {got}."


def test_long():
    xs, ys = list(range(0, 2 * 10**5, 2)), list(range(1, 2 * 10**5, 2))
    got = to_list(merge_two(build(xs), build(ys)))
    assert got == list(range(2 * 10**5)), "Two lists of 100,000 nodes; use a loop, not recursion."
