import random
import subprocess
import sys
from pathlib import Path

import pytest

from solution import ListNode, sort_list

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


@pytest.mark.parametrize("values", [
    [4, 2, 1, 3], [-1, 5, 3, 4, 0], [], [1], [2, 1], [1, 2], [3, 3, 3], [5, 4, 3, 2, 1], [1, 2, 3, 4, 5, 6],
])
def test_cases(values):
    head = build(values)
    before = nodes(head)
    try:
        got = sort_list(head)
    except RecursionError:
        raise AssertionError(
            f"sort_list({values}) recursed without end. For two nodes the split must give two halves of one "
            "node each: start with slow = head and fast = head.next, and cut with slow.next = None.") from None
    assert to_list(got) == sorted(values), f"sort_list({values}) should give {sorted(values)}, got {to_list(got)}."
    check_same_nodes(before, got, f"sort_list({values})")


def test_nodes_keep_their_values_and_order_is_stable():
    values = [3, 1, 2, 1, 3, 2, 1]
    head = build(values)
    before = nodes(head)
    tags = {id(n): (n.val, i) for i, n in enumerate(before)}
    got = nodes(sort_list(head))
    for n in got:
        assert n.val == tags[id(n)][0], (
            "A node's value changed. Move nodes by changing next pointers; do not copy or swap values.")
    order = [tags[id(n)] for n in got]
    assert order == sorted(order), (
        f"Equal values must keep their original order (stable sort). Got (value, original index) = {order}. "
        "In the merge, take from the right half only when its value is strictly smaller.")


def test_random_small():
    rng = random.Random(25)
    for _ in range(200):
        values = [rng.randint(-5, 5) for _ in range(rng.randint(0, 20))]
        got = to_list(sort_list(build(values)))
        assert got == sorted(values), f"sort_list({values}) gave {got}."


def test_fifty_thousand_nodes_in_time():
    code = (
        "import random\n"
        "from solution import ListNode, sort_list\n"
        "rng = random.Random(1)\n"
        "values = [rng.randint(0, 10**6) for _ in range(50000)]\n"
        "head = None\n"
        "for v in values:\n"
        "    head = ListNode(v, head)\n"
        "cur = sort_list(head)\n"
        "out = []\n"
        "while cur is not None and len(out) <= 50000:\n"
        "    out.append(cur.val)\n"
        "    cur = cur.next\n"
        "print(out == sorted(values))\n"
    )
    out = run_code(code, 20, "Sorting 50,000 nodes (insertion sort or selection sort is O(n^2); use merge sort)")
    assert out == "True", "50,000 random values were not sorted correctly."
