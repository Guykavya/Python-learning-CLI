import subprocess
import sys
from pathlib import Path

import pytest

from solution import ListNode, rotate_right

HERE = Path(__file__).parent


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


def run_code(code, timeout, what):
    """Run code in a fresh Python process, so an endless loop fails cleanly instead of hanging."""
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{what}: still running after {timeout} seconds.") from None
    assert r.returncode == 0, f"Your code crashed:\n{r.stderr[-800:]}"
    return r.stdout.strip()


def expected(values, k):
    if not values:
        return []
    k %= len(values)
    return values[len(values) - k:] + values[:len(values) - k]


@pytest.mark.parametrize("values, k, why", [
    ([1, 2, 3, 4, 5], 2, "the example"),
    ([0, 1, 2], 4, "k larger than the length: only k % n matters"),
    ([1, 2], 0, "k = 0 changes nothing"),
    ([1, 2, 3], 3, "k = n changes nothing"),
    ([1, 2, 3], 1, "the last node moves to the front"),
    ([1, 2, 3], 2, "two nodes move to the front"),
    ([], 5, "the empty list stays empty"),
    ([9], 7, "one node stays the same"),
])
def test_cases(values, k, why):
    head = build(values)
    before = nodes(head)
    got = rotate_right(head, k)
    want = expected(values, k)
    assert to_list(got) == want, (
        f"rotate_right({values}, {k}) should give {want}, got {to_list(got)}: {why}. "
        "The new tail is node n - k (1-based); its next must become None, and the old tail must point at the old head.")
    if values:
        check_same_nodes(before, got, f"rotate_right({values}, {k})")


def test_all_small():
    for n in range(0, 7):
        values = list(range(n))
        for k in range(0, 15):
            got = to_list(rotate_right(build(values), k))
            assert got == expected(values, k), f"rotate_right({values}, {k}) gave {got}."


def test_huge_k():
    code = (
        "from solution import ListNode, rotate_right\n"
        "head = None\n"
        "for v in range(1000, 0, -1):\n"
        "    head = ListNode(v, head)\n"
        "h = rotate_right(head, 10**12 + 3)\n"
        "print(h.val)\n"
    )
    out = run_code(code, 10, "rotate_right with k = 10**12 + 3 (do not step k times; use k % n)")
    assert out == "998", f"1..1000 rotated by 10**12 + 3 (k % 1000 = 3) starts with 998, got {out!r}."
