import random
import subprocess
import sys
from collections import deque
from pathlib import Path

import pytest

from solution import Queue

HERE = Path(__file__).parent


def run_code(code, timeout, what):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{what} took more than {timeout} seconds.") from None
    assert r.returncode == 0, f"Your code crashed:\n{r.stderr[-800:]}"
    return r.stdout.strip()


def test_example():
    q = Queue()
    for name in ("Asha", "Ben", "Chitra"):
        q.enqueue(name)
    assert q.front() == "Asha", "front() is the OLDEST item (the first one enqueued). Did you look at the back?"
    assert len(q) == 3, "len(q) must count the items; define __len__."
    assert q.dequeue() == "Asha", "dequeue() removes the oldest item first (FIFO). pop() would give the newest: use popleft()."
    assert q.dequeue() == "Ben"
    assert q.dequeue() == "Chitra"
    assert q.is_empty() is True, "After removing everything, is_empty() must be True."


def test_errors_on_empty():
    q = Queue()
    with pytest.raises(IndexError) as info:
        q.dequeue()
    assert str(info.value) == "dequeue from empty queue", (
        f"dequeue() on an empty queue must raise IndexError('dequeue from empty queue'), got {str(info.value)!r}.")
    with pytest.raises(IndexError) as info:
        q.front()
    assert str(info.value) == "front of empty queue", (
        f"front() on an empty queue must raise IndexError('front of empty queue'), got {str(info.value)!r}.")


def test_items_live_in_a_deque():
    q = Queue()
    q.enqueue(1)
    stores = [v for v in vars(q).values() if isinstance(v, deque)]
    assert stores, "Store the items in a collections.deque (for example self._items = deque()), not in a list."


def test_none_is_an_item():
    q = Queue()
    q.enqueue(None)
    assert q.is_empty() is False and len(q) == 1, "A queue holding None is not empty."
    assert q.dequeue() is None


def test_random_operations_against_a_model():
    rng = random.Random(3)
    q, model = Queue(), deque()
    for step in range(3000):
        op = rng.choice(["enq", "enq", "deq", "front", "len"])
        if op == "enq":
            x = rng.randint(0, 99)
            q.enqueue(x)
            model.append(x)
        elif op == "deq" and model:
            assert q.dequeue() == model.popleft(), f"Step {step}: dequeue() must return the oldest item."
        elif op == "front" and model:
            assert q.front() == model[0], f"Step {step}: front() should be {model[0]}."
        elif op == "len":
            assert len(q) == len(model), f"Step {step}: len should be {len(model)}."
        assert q.is_empty() == (not model), f"Step {step}: is_empty() is wrong."


def test_100000_operations_in_time():
    code = (
        "from solution import Queue\n"
        "q = Queue()\n"
        "for i in range(100000):\n"
        "    q.enqueue(i)\n"
        "total = 0\n"
        "for i in range(100000):\n"
        "    q.enqueue(i)\n"
        "    total += q.dequeue()\n"
        "while not q.is_empty():\n"
        "    total += q.dequeue()\n"
        "print(total)\n"
    )
    out = run_code(code, 20, "200,000 enqueues and 200,000 dequeues on a queue of 100,000 items "
                   "(each operation must be O(1): use deque.popleft(), not list.pop(0))")
    assert out == str(2 * sum(range(100000))), f"Every enqueued number must come out exactly once; the total was {out}."
