import random
from collections import deque

import pytest

from solution import DoublyLinkedList


def check(d, model, where):
    """Walk both directions with step limits and compare with the model."""
    fwd, cur = [], d.head
    for _ in range(len(model) + 1):
        nxt = cur.next
        assert nxt is not None, f"{where}: walking forward from head reached None before the tail sentinel."
        assert nxt.prev is cur, (
            f"{where}: a node's prev does not point back at the node before it (value {getattr(nxt, 'val', None)!r}). "
            "When you link or unlink, set the pointers in BOTH directions.")
        cur = nxt
        if cur is d.tail:
            break
        fwd.append(cur.val)
    assert cur is d.tail, (
        f"{where}: walking forward from head does not reach the tail sentinel after {len(model)} items "
        f"(the list should be {list(model)}).")
    assert fwd == list(model), f"{where}: the values from left to right are {fwd}, should be {list(model)}."
    back, cur = [], d.tail
    for _ in range(len(model) + 1):
        cur = cur.prev
        assert cur is not None, f"{where}: walking backward from tail reached None before the head sentinel."
        if cur is d.head:
            break
        back.append(cur.val)
    assert back == list(model)[::-1], f"{where}: walking backward gives {back}, should be {list(model)[::-1]}."
    assert len(d) == len(model), f"{where}: len() is {len(d)}, should be {len(model)}."
    assert list(d) == list(model), f"{where}: __iter__ yields {list(d)}, should be {list(model)}."


def test_empty():
    d = DoublyLinkedList()
    assert d.head.next is d.tail and d.tail.prev is d.head, (
        "A new list is two sentinels pointing at each other: head.next is tail and tail.prev is head.")
    check(d, [], "a new list")
    with pytest.raises(IndexError):
        d.pop()
    with pytest.raises(IndexError):
        d.popleft()


def test_example():
    d = DoublyLinkedList()
    a = d.append(1)
    d.append(2)
    d.appendleft(0)
    check(d, [0, 1, 2], "after append 1, append 2, appendleft 0")
    assert a is not None and a.val == 1, "append must return the new node, so it can be removed later."
    assert d.remove_node(a) == 1, "remove_node returns the value of the removed node."
    check(d, [0, 2], "after removing the middle node")
    assert a.prev is None and a.next is None, (
        "A removed node should have prev and next set to None (cut it free), so it cannot be used by mistake.")
    assert d.pop() == 2 and d.popleft() == 0, "pop takes from the right, popleft from the left."
    check(d, [], "after removing everything")


def test_remove_first_and_last_nodes():
    d = DoublyLinkedList()
    first = d.append("a")
    d.append("b")
    last = d.append("c")
    d.remove_node(first)
    check(d, ["b", "c"], "after removing the first node")
    d.remove_node(last)
    check(d, ["b"], "after removing the last node")
    d.append("z")
    d.appendleft("y")
    check(d, ["y", "b", "z"], "after adding on both ends again")


def test_random_against_deque():
    rng = random.Random(10)
    d, model = DoublyLinkedList(), deque()
    held = []                                     # [value, node] pairs for items still in the list
    for step in range(4000):
        op = rng.choice(["append", "appendleft", "pop", "popleft", "remove", "remove"])
        if op in ("append", "appendleft"):
            v = step
            node = getattr(d, op)(v)
            getattr(model, op)(v)
            held.append([v, node])
        elif op in ("pop", "popleft"):
            if not model:
                with pytest.raises(IndexError):
                    getattr(d, op)()
                continue
            want = getattr(model, op)()
            got = getattr(d, op)()
            assert got == want, f"step {step}: {op}() returned {got!r}, should be {want!r}."
            held = [p for p in held if p[0] != want]
        else:
            if not held:
                continue
            i = rng.randrange(len(held))
            v, node = held.pop(i)
            got = d.remove_node(node)
            assert got == v, f"step {step}: remove_node returned {got!r}, should be the node's value {v!r}."
            model.remove(v)
        check(d, model, f"step {step} ({op})")
