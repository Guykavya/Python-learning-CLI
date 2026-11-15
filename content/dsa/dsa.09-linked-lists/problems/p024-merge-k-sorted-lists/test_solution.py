import random
import subprocess
import sys
from pathlib import Path

import pytest

from solution import ListNode, merge_k

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


def call(lists):
    try:
        return merge_k(lists)
    except TypeError as e:
        if "<" in str(e):
            raise AssertionError(
                "heapq compared two nodes (TypeError: '<' not supported). Two entries had equal values, so the "
                "next item of the tuple was compared. Put a tie-breaker (the list index or a counter) between "
                "the value and the node.") from None
        raise


@pytest.mark.parametrize("groups", [
    [[1, 4, 5], [1, 3, 4], [2, 6]],
    [],
    [[]],
    [[], []],
    [[3]],
    [[], [1], []],
    [[5, 5], [5], [5, 5, 5]],
    [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
])
def test_cases(groups):
    heads = [build(g) for g in groups]
    every = [n for h in heads for n in nodes(h)]
    got = call(heads)
    want = sorted(v for g in groups for v in g)
    assert to_list(got) == want, f"merge_k({groups}) should give {want}, got {to_list(got)}."
    if want:
        check_same_nodes(every, got, f"merge_k({groups})")
    else:
        assert got is None, "No nodes at all: return None."


def test_random():
    rng = random.Random(24)
    for _ in range(200):
        groups = [sorted(rng.randint(0, 5) for _ in range(rng.randint(0, 5))) for _ in range(rng.randint(0, 6))]
        got = to_list(call([build(g) for g in groups]))
        assert got == sorted(v for g in groups for v in g), f"merge_k({groups}) gave {got}."


def test_many_lists_fast():
    code = (
        "from solution import ListNode, merge_k\n"
        "lists = []\n"
        "for i in range(5000):\n"
        "    head = None\n"
        "    for v in (i * 7 % 101 + 300, i * 3 % 89 + 200, i * 5 % 97 + 100, i % 50):\n"
        "        head = ListNode(v, head)\n"
        "    lists.append(head)\n"
        "cur = merge_k(lists)\n"
        "out = []\n"
        "while cur is not None and len(out) <= 20000:\n"
        "    out.append(cur.val)\n"
        "    cur = cur.next\n"
        "print(len(out), out == sorted(out))\n"
    )
    out = run_code(code, 15, "Merging 5,000 lists of 4 nodes (merging them one after another is O(k * N); "
                              "use a heap or merge in pairs for O(N log k))")
    assert out == "20000 True", f"5,000 lists of 4 nodes should give 20,000 sorted values; got {out!r}."
