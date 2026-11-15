import random
import subprocess
import sys
from pathlib import Path

import pytest

from solution import LinkedList

HERE = Path(__file__).parent


def run_code(code, timeout, what):
    """Run code in a fresh Python process, so an endless loop fails cleanly instead of hanging."""
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{what}: still running after {timeout} seconds.") from None
    assert r.returncode == 0, f"Your code crashed:\n{r.stderr[-800:]}"
    return r.stdout.strip()


def walk(lst, limit=10**5):
    out, cur = [], lst.head
    while cur is not None:
        assert len(out) < limit, "your list has a cycle: walking from head never reaches a node whose next is None."
        out.append(cur)
        cur = cur.next
    return out


def check(lst, model, where):
    ns = walk(lst)
    assert [n.val for n in ns] == model, f"{where}: walking from head gives {[n.val for n in ns]}, should be {model}."
    assert len(lst) == len(model), f"{where}: len() is {len(lst)}, should be {len(model)}. Update the size in every method."
    assert list(lst) == model, f"{where}: iterating gives {list(lst)}, should be {model}. __iter__ must yield the values."
    if not model:
        assert lst.head is None and lst.tail is None, (
            f"{where}: the list is empty, so head and tail must both be None (tail still points at a removed node?).")
    else:
        assert lst.tail is ns[-1], (
            f"{where}: tail should be the last node (value {model[-1]!r}), but it is "
            f"{getattr(lst.tail, 'val', None)!r}. Move the tail when you add at the back, remove the last node, "
            "or add to an empty list.")
        assert lst.tail.next is None, f"{where}: tail.next must be None."


def test_example():
    lst = LinkedList()
    lst.push_back(2)
    lst.push_back(3)
    lst.push_front(1)
    check(lst, [1, 2, 3], "after push_back 2, push_back 3, push_front 1")
    assert lst.remove(3) is True and lst.remove(9) is False, "remove returns True if a node was removed, else False."
    check(lst, [1, 2], "after remove(3)")
    assert lst.pop_front() == 1 and lst.pop_front() == 2, "pop_front returns the values from the front."
    check(lst, [], "after popping everything")


def test_empty():
    lst = LinkedList()
    check(lst, [], "a new list")
    with pytest.raises(IndexError):
        lst.pop_front()
    assert lst.remove(1) is False, "remove on an empty list finds nothing and returns False."


def test_push_front_on_empty_sets_tail():
    lst = LinkedList()
    lst.push_front(5)
    check(lst, [5], "push_front on an empty list (the new node is also the tail)")
    lst.push_back(6)
    check(lst, [5, 6], "push_back after push_front on an empty list")


def test_remove_cases():
    lst = LinkedList()
    for v in (1, 2, 1, 3):
        lst.push_back(v)
    assert lst.remove(1)
    check(lst, [2, 1, 3], "remove(1) removes only the FIRST 1 (the head here)")
    assert lst.remove(3)
    check(lst, [2, 1], "remove(3) removes the tail: the tail moves back")
    lst.push_back(4)
    check(lst, [2, 1, 4], "push_back after removing the tail")
    assert lst.remove(2) and lst.remove(1) and lst.remove(4)
    check(lst, [], "after removing every node")
    lst.push_back(7)
    check(lst, [7], "push_back on a list that was emptied by remove")


def test_random_against_list():
    rng = random.Random(7)
    lst, model = LinkedList(), []
    for step in range(3000):
        op = rng.choice(["front", "back", "back", "pop", "remove", "remove_missing"])
        if op == "front":
            v = rng.randint(0, 9)
            lst.push_front(v)
            model.insert(0, v)
        elif op == "back":
            v = rng.randint(0, 9)
            lst.push_back(v)
            model.append(v)
        elif op == "pop":
            if model:
                assert lst.pop_front() == model.pop(0), f"step {step}: pop_front returned the wrong value."
            else:
                with pytest.raises(IndexError):
                    lst.pop_front()
        elif op == "remove":
            v = rng.randint(0, 9)
            want = v in model
            if want:
                model.remove(v)
            assert lst.remove(v) is want, f"step {step}: remove({v}) should return {want}."
        else:
            assert lst.remove(100) is False
        check(lst, model, f"step {step} ({op})")


def test_push_back_is_constant_time():
    code = (
        "from solution import LinkedList\n"
        "lst = LinkedList()\n"
        "for i in range(200000):\n"
        "    lst.push_back(i)\n"
        "print(len(lst), lst.tail.val)\n"
    )
    out = run_code(code, 15, "200,000 push_back calls (push_back must use the tail, not walk the list)")
    assert out == "200000 199999", f"After 200,000 push_back calls, expected length 200000 and tail 199999, got {out!r}."
