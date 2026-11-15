import ast
import random
from pathlib import Path

import pytest

from solution import ListNode, add_two_numbers

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


def digits(n):
    return [int(d) for d in str(n)][::-1]


@pytest.mark.parametrize("x, y, why", [
    (342, 465, "the example"),
    (99, 1, "a carry that runs to a new last digit: 99 + 1 = 100"),
    (0, 0, "0 + 0 is the single digit 0"),
    (5, 5, "10: the final carry needs its own node"),
    (1, 9999, "lists of different lengths with a long carry"),
    (12345, 0, "adding 0"),
    (999999999, 999999999, "carries everywhere"),
])
def test_cases(x, y, why):
    a, b = build(digits(x)), build(digits(y))
    na, nb = nodes(a), nodes(b)
    got = add_two_numbers(a, b)
    want = digits(x + y)
    assert to_list(got) == want, (
        f"{x} + {y} = {x + y} should be the list {want}, got {to_list(got)}: {why}. "
        "Keep looping while a, b OR the carry is left.")
    assert to_list(a) == digits(x) and to_list(b) == digits(y), "The input lists must not change."
    ids = {id(n) for n in na + nb}
    assert not any(id(n) in ids for n in nodes(got)), "Build the result from new nodes; do not reuse input nodes."


def test_random():
    rng = random.Random(31)
    for _ in range(300):
        x, y = rng.randint(0, 10**rng.randint(1, 15)), rng.randint(0, 10**rng.randint(1, 15))
        got = to_list(add_two_numbers(build(digits(x)), build(digits(y))))
        assert got == digits(x + y), f"{x} + {y}: got {got}, should be {digits(x + y)}."


def test_long():
    xs = [7] * 10**4                                  # 77...7 with 10,000 digits (ones digit first)
    ys = [5] * 9_000                                  # 55...5 with 9,000 digits
    want = [2] + [3] * 8_999 + [8] + [7] * 999        # 7+5=12, then 7+5+1=13 ..., then 7+1=8, then 7s
    got = to_list(add_two_numbers(build(xs), build(ys)))
    assert got == want, "Two numbers with 10,000 and 9,000 digits: the carry must run through the whole sum."


def test_digit_by_digit():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    assert "int" not in names and "str" not in names, (
        "Do not convert the lists to Python integers (int/str): add digit by digit with a carry. Real numbers in "
        "such lists can be far longer than you would want to convert.")
