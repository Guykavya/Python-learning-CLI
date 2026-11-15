import random

import pytest

from solution import ListNode, remove_all


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


@pytest.mark.parametrize("values, target, why", [
    ([6, 6, 1, 6, 2, 6], 6, "matches at the head, in the middle, next to each other and at the end"),
    ([7, 7], 7, "every node matches: the result is None"),
    ([], 6, "the empty list stays empty"),
    ([1, 2, 3], 9, "nothing matches: the list is unchanged"),
    ([5], 5, "the only node matches"),
    ([1, 5, 5, 5, 2], 5, "a run of matches in the middle: after an unlink, check the new prev.next too"),
    ([1, 2, 5], 5, "the last node matches"),
    ([0, 1, 0], 0, "target 0 is a real value"),
])
def test_cases(values, target, why):
    head = build(values)
    before = nodes(head)
    got = remove_all(head, target)
    want = [v for v in values if v != target]
    assert to_list(got) == want, (
        f"remove_all({values}, {target}) should leave {want}, got {to_list(got)}: {why}. "
        "If one of two neighbouring matches survived, you moved prev forward after unlinking.")
    kept = [n for n in before if n.val != target]
    after = nodes(got)
    assert all(a is b for a, b in zip(kept, after)), (
        "The nodes you keep must be the original node objects: unlink the matches instead of building a new list.")


def test_random():
    rng = random.Random(8)
    for _ in range(300):
        values = [rng.randint(0, 3) for _ in range(rng.randint(0, 12))]
        target = rng.randint(0, 3)
        got = to_list(remove_all(build(values), target))
        assert got == [v for v in values if v != target], f"remove_all({values}, {target}) gave {got}."


def test_long_run_of_matches():
    values = [1] * 50_000 + [2] + [1] * 50_000
    assert to_list(remove_all(build(values), 1)) == [2], (
        "100,000 matches around one survivor: use a loop (not recursion) and do not restart from the head after each removal.")
