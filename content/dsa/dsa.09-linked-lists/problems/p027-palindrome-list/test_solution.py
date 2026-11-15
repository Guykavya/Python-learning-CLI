import random
import tracemalloc

import pytest

from solution import ListNode, is_palindrome


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


@pytest.mark.parametrize("values, want", [
    ([1, 2, 2, 1], True), ([1, 2, 3, 2, 1], True), ([1, 2], False), ([], True), ([7], True),
    ([1, 1], True), ([1, 2, 1], True), ([1, 2, 3], False), ([1, 2, 3, 1], False), ([1, 2, 2, 3], False),
    (["a", "b", "a"], True), ([0, 0, 1, 0, 0], True),
])
def test_cases_and_restored(values, want):
    head = build(values)
    before = nodes(head)
    got = is_palindrome(head)
    assert got is want, f"is_palindrome({values}) should be {want}, got {got!r}."
    after = nodes(head)
    assert [n.val for n in after] == values and len(after) == len(before) and all(a is b for a, b in zip(before, after)), (
        f"After is_palindrome({values}) the list is {[n.val for n in after]}: it must be restored exactly "
        "(same nodes, same order). Reverse the second half back and link it after the first half, "
        "also when the answer is False.")


def test_random():
    rng = random.Random(27)
    for _ in range(300):
        half = [rng.randint(0, 2) for _ in range(rng.randint(0, 6))]
        values = half + ([rng.randint(0, 2)] if rng.random() < 0.5 else []) + half[::-1]
        if rng.random() < 0.5 and values:
            values[rng.randrange(len(values))] = rng.randint(0, 2)
        head = build(values)
        got = is_palindrome(head)
        assert got is (values == values[::-1]), f"is_palindrome({values}) should be {values == values[::-1]}."
        assert to_list(head) == values, f"The list {values} was not restored."


@pytest.mark.parametrize("pal", [True, False])
def test_memory(pal):
    half = list(range(50_000))
    values = half + half[::-1] if pal else half + half
    head = build(values)
    tracemalloc.start()
    try:
        tracemalloc.reset_peak()
        got = is_palindrome(head)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert got is pal, f"A list of 100,000 values: expected {pal}."
    assert peak < 200_000, (
        f"is_palindrome used about {peak:,} bytes of extra memory on 100,000 nodes. Copying values or nodes into a "
        "list (or recursion) grows with n; reversing the second half in place needs O(1).")
    assert to_list(head) == values, "The long list must be restored too."
