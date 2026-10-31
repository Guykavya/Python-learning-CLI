import random

import pytest

from solution import TaskQueue

TIE_HINT = (
    "Two tasks with the same priority made Python compare the tasks themselves (TypeError). "
    "Push (priority, counter, task): the always-different counter breaks every tie."
)


def safe(action):
    try:
        return action()
    except TypeError as e:
        pytest.fail(f"{TIE_HINT} Error was: {e}", pytrace=False)


def test_example():
    q = TaskQueue()
    q.push({"job": "email"}, 2)
    q.push({"job": "backup"}, 1)
    safe(lambda: q.push({"job": "report"}, 2))
    assert safe(q.pop) == {"job": "backup"}, "The lowest priority number comes out first."
    assert safe(q.pop) == {"job": "email"}, (
        "Equal priority: the task pushed first wins. If you got a TypeError, the dicts were compared: "
        "push (priority, counter, task) so the counter breaks ties."
    )
    assert len(q) == 1, "One task left."


def test_dicts_with_equal_priority_never_compared():
    q = TaskQueue()
    for i in range(10):
        safe(lambda: q.push({"i": i}, 5))
    assert [safe(q.pop)["i"] for _ in range(10)] == list(range(10)), (
        "Ten tasks with the same priority come out in push order (first come, first served)."
    )


def test_fifo_even_when_items_compare():
    q = TaskQueue()
    q.push("zebra", 1)
    q.push("apple", 1)
    q.push("mango", 1)
    assert [q.pop(), q.pop(), q.pop()] == ["zebra", "apple", "mango"], (
        "Strings CAN be compared, but ties must still follow push order, not alphabetical order. "
        "(priority, task) tuples would give 'apple' first."
    )


def test_many_random():
    rng = random.Random(42)
    q = TaskQueue()
    pushed = []
    for n in range(300):
        p = rng.randint(0, 9)
        safe(lambda: q.push({"n": n}, p))
        pushed.append((p, n))
    expected = [n for p, n in sorted(pushed)]
    got = [safe(q.pop)["n"] for _ in range(300)]
    assert got == expected, "Order must be: by priority, then by push order."
    assert len(q) == 0 and not q, "All popped: the queue is empty and falsy."


def test_peek():
    q = TaskQueue()
    q.push("later", 3)
    q.push("now", 0)
    assert q.peek() == "now", "peek returns the most urgent task."
    assert len(q) == 2, "peek must not remove anything."
    assert q.pop() == "now", "pop returns the same task peek showed."


def test_empty_errors():
    q = TaskQueue()
    with pytest.raises(IndexError):
        q.pop()
    with pytest.raises(IndexError):
        q.peek()


def test_len_and_bool():
    q = TaskQueue()
    assert len(q) == 0 and not q, "A new queue is empty and falsy."
    q.push(None, 1)
    assert len(q) == 1 and q, "One task: len 1 and truthy. (None is a valid task!)"
    assert q.pop() is None, "pop returns the task itself, not the (priority, count, task) tuple."
    assert not q, "Empty again."


def test_negative_priorities_and_interleaving():
    q = TaskQueue()
    q.push("a", 0)
    q.push("b", -5)
    assert q.pop() == "b", "-5 is more urgent than 0."
    q.push("c", 0)
    q.push("d", -1)
    assert [q.pop(), q.pop(), q.pop()] == ["d", "a", "c"], "Pops and pushes can interleave; 'a' was pushed before 'c'."


def test_queues_are_independent():
    q1 = TaskQueue()
    q2 = TaskQueue()
    q1.push("x", 1)
    assert len(q2) == 0, "Each queue needs its own list: create it in __init__."
