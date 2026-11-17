import ast
import pathlib
import random

import pytest

from solution import TaskQueue

SOLUTION = pathlib.Path(__file__).with_name("solution.py")


def test_it_is_a_heapq_exercise():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            used.add(node.attr)
        if isinstance(node, ast.Name):
            used.add(node.id)
    assert "heappush" in used and "heappop" in used, "Use heapq.heappush and heapq.heappop with tuples (priority, counter, task)."


def add_all(q, entries):
    for priority, task in entries:
        try:
            q.add(priority, task)
        except TypeError as error:
            pytest.fail(
                f"TypeError: {error}. Two entries with the same priority made Python compare the tasks, which cannot be compared. "
                "Put a counter that grows with every add between the priority and the task: (priority, counter, task).")


def drain(q):
    return [q.pop() for _ in range(len(q))]


def test_the_example_with_dictionaries():
    q = TaskQueue()
    add_all(q, [(2, {"name": "backup"}), (1, {"name": "email"}), (2, {"name": "report"}), (1, {"name": "call"})])
    popped = drain(q)
    assert all(isinstance(t, dict) for t in popped), (
        f"pop must return the task itself (a dict here), not the whole heap entry; got {popped[0]!r}.")
    got = [t["name"] for t in popped]
    assert got == ["email", "call", "backup", "report"], (
        f"Expected ['email', 'call', 'backup', 'report'], got {got}. Smallest priority first, and among equal priorities the task added first.")


def test_tasks_that_cannot_be_compared_at_all():
    a, b, c = object(), object(), object()
    q = TaskQueue()
    add_all(q, [(1, a), (1, b), (0, c)])
    out = drain(q)
    assert out[0] is c and out[1] is a and out[2] is b, "pop must return the task objects themselves: c (priority 0), then a, then b (same priority, added in this order)."
    f, g = (lambda: 1), (lambda: 2)
    q.add(5, f)
    q.add(5, g)
    assert q.pop() is f and q.pop() is g, "Functions cannot be compared either: the counter must decide."


def test_the_same_task_object_can_be_added_twice():
    task = {"n": 1}
    q = TaskQueue()
    add_all(q, [(3, task), (3, task), (1, task)])
    assert len(q) == 3 and drain(q) == [task, task, task], "The same object added three times must come out three times."


def test_pop_returns_the_task_not_the_tuple():
    q = TaskQueue()
    add_all(q, [(1, "x")])
    got = q.pop()
    assert got == "x", f"pop must return the task itself, 'x', not the entry; got {got!r}."


def test_an_empty_queue():
    q = TaskQueue()
    assert len(q) == 0, "A new queue is empty."
    with pytest.raises(IndexError):
        q.pop()


def test_priorities_can_be_negative_or_floats():
    q = TaskQueue()
    add_all(q, [(0.5, "half"), (-3, "minus three"), (2, "two"), (-3.5, "minus three and a half"), (0, "zero")])
    assert drain(q) == ["minus three and a half", "minus three", "zero", "half", "two"], "Smaller numbers are more urgent, also negative ones and floats."


def test_many_equal_priorities_keep_the_order_of_adding():
    q = TaskQueue()
    tasks = [{"id": i} for i in range(60)]
    add_all(q, [(7, t) for t in tasks])
    got = drain(q)
    assert [t["id"] for t in got] == list(range(60)), (
        "60 tasks with the same priority must come out in the order they were added (0, 1, 2, ...). "
        "A random or id-based tie-breaker is not first in, first out.")


def test_the_counter_is_not_before_the_priority():
    q = TaskQueue()
    add_all(q, [(5, "late"), (1, "urgent")])
    assert q.pop() == "urgent", "A smaller priority must win even if it was added later: the order is (priority, counter, task), not (counter, priority, task)."


def test_the_counter_never_repeats_after_pops():
    q = TaskQueue()
    add_all(q, [(1, {"n": "a"}), (1, {"n": "b"})])
    assert q.pop()["n"] == "a"
    add_all(q, [(1, {"n": "c"}), (1, {"n": "d"})])
    assert [t["n"] for t in drain(q)] == ["b", "c", "d"], (
        "After a pop, new tasks must still come after the older ones with the same priority. "
        "A counter based on len(heap) repeats numbers; use a counter that only goes up.")


def test_random_operations_against_a_model():
    rng = random.Random(12)
    for _ in range(150):
        q = TaskQueue()
        model = []                                   # entries (priority, sequence number, task)
        seq = 0
        for step in range(80):
            if model and rng.random() < 0.4:
                best = min(model, key=lambda e: (e[0], e[1]))
                model.remove(best)
                got = q.pop()
                assert got is best[2], f"Step {step}: pop returned {got!r}, expected the task with the smallest priority, oldest first: {best[2]!r}."
            else:
                task = {"seq": seq}
                priority = rng.randint(0, 4)
                add_all(q, [(priority, task)])
                model.append((priority, seq, task))
                seq += 1
            assert len(q) == len(model), f"Step {step}: len is {len(q)}, it should be {len(model)}."
