import ast
from pathlib import Path

import pytest

from solution import ListNode, reverse_rec

SOLUTION = Path(__file__).with_name("solution.py")


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


@pytest.mark.parametrize("values", [[], [1], [1, 2], [1, 2, 3], [1, 2, 3, 4], [7, 7, 8]])
def test_reverse(values):
    head = build(values)
    before = nodes(head)
    got = reverse_rec(head)
    assert to_list(got) == values[::-1], (
        f"reverse_rec({values}) should give {values[::-1]}, got {to_list(got)}. Every level must return "
        "the new head that the deepest call found, not its own head.")
    check_same_nodes(before, got, f"reverse_rec({values})")


def test_old_head_becomes_tail():
    head = build([1, 2, 3])
    reverse_rec(head)
    assert head.next is None, (
        "The old head is the new tail: set head.next = None after attaching it, or 1 and 2 point at each other (a cycle).")


def test_800_nodes():
    values = list(range(800))
    try:
        got = reverse_rec(build(values))
    except RecursionError:
        raise AssertionError(
            "800 nodes need about 800 nested calls, which fits under Python's limit of about 1,000. "
            "RecursionError here means your recursion does not stop: check the base case "
            "(head is None or head.next is None) and that each call gets head.next, a shorter list.") from None
    assert to_list(got) == values[::-1], "800 nodes reversed recursively."


def test_is_recursive_without_loops():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "reverse_rec"]
    assert funcs, "Keep the function name reverse_rec."
    body = funcs[0]
    calls = [n for n in ast.walk(body) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "reverse_rec"]
    loops = [n for n in ast.walk(body) if isinstance(n, (ast.For, ast.While))]
    assert calls, "reverse_rec must call itself: this problem practises the recursive version."
    assert not loops, "No for or while loop in reverse_rec: let the recursion do the walking."
