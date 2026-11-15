import ast
import random
import subprocess
import sys
from collections import deque
from pathlib import Path

import pytest

from solution import LinkedQueue, LinkedStack

HERE = Path(__file__).parent
SOLUTION = Path(__file__).with_name("solution.py")


def run_code(code, timeout, what):
    """Run code in a fresh Python process, so an endless loop fails cleanly instead of hanging."""
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{what}: still running after {timeout} seconds.") from None
    assert r.returncode == 0, f"Your code crashed:\n{r.stderr[-800:]}"
    return r.stdout.strip()


def test_stack_example():
    s = LinkedStack()
    for x in (1, 2, 3):
        s.push(x)
    assert len(s) == 3, "Three pushes: length 3."
    assert s.pop() == 3, "A stack returns the LAST value pushed first (LIFO). Push and pop at the head."
    assert s.peek() == 2 and len(s) == 2, "peek returns the top without removing it."
    assert s.pop() == 2 and s.pop() == 1
    with pytest.raises(IndexError):
        s.pop()
    with pytest.raises(IndexError):
        s.peek()


def test_queue_example():
    q = LinkedQueue()
    for x in (1, 2, 3):
        q.enqueue(x)
    assert q.dequeue() == 1, "A queue returns the FIRST value enqueued first (FIFO): add at the tail, remove at the head."
    assert q.peek() == 2 and len(q) == 2
    with pytest.raises(IndexError):
        LinkedQueue().dequeue()
    with pytest.raises(IndexError):
        LinkedQueue().peek()


def test_queue_refill_after_empty():
    q = LinkedQueue()
    q.enqueue("a")
    assert q.dequeue() == "a"
    q.enqueue("b")
    q.enqueue("c")
    msg = ("After the queue became empty, new items got lost: when the last item is dequeued, set the tail to None "
           "too, so the next enqueue starts a new chain (otherwise it links after the removed node).")
    try:
        got = [q.dequeue(), q.dequeue()]
    except IndexError:
        raise AssertionError(msg) from None
    assert len(q) == 0 and got == ["b", "c"], msg


def test_falsy_values():
    s, q = LinkedStack(), LinkedQueue()
    for v in (0, None, ""):
        s.push(v)
        q.enqueue(v)
    assert len(s) == 3 and len(q) == 3, "0, None and '' are values; count them."
    assert [s.pop() for _ in range(3)] == ["", None, 0]
    assert [q.dequeue() for _ in range(3)] == [0, None, ""]


def test_random_against_deque():
    rng = random.Random(35)
    s, q, ms, mq = LinkedStack(), LinkedQueue(), deque(), deque()
    for step in range(5000):
        op = rng.choice(["push", "push", "pop", "peek", "enq", "enq", "deq", "qpeek"])
        v = rng.randint(0, 50)
        if op == "push":
            s.push(v)
            ms.append(v)
        elif op == "enq":
            q.enqueue(v)
            mq.append(v)
        elif op in ("pop", "peek"):
            if ms:
                want = ms.pop() if op == "pop" else ms[-1]
                assert getattr(s, op)() == want, f"step {step}: stack {op}() should be {want}."
            else:
                with pytest.raises(IndexError):
                    getattr(s, op)()
        else:
            if mq:
                want = mq.popleft() if op == "deq" else mq[0]
                got = q.dequeue() if op == "deq" else q.peek()
                assert got == want, f"step {step}: queue {'dequeue' if op == 'deq' else 'peek'}() should be {want}."
            else:
                with pytest.raises(IndexError):
                    q.dequeue() if op == "deq" else q.peek()
        assert len(s) == len(ms) and len(q) == len(mq), f"step {step}: a length is wrong."


def test_built_from_nodes_only():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    containers = [n for n in ast.walk(tree) if isinstance(n, (ast.List, ast.ListComp, ast.Dict))]
    calls = {n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert "deque" not in names and "list" not in names and not containers, (
        "Build both classes from ListNode objects only: no Python list, deque or dict inside.")
    assert not calls & {"append", "pop", "popleft", "insert"}, (
        "Your classes call append/pop/insert on some container. Link nodes instead.")


def test_constant_time():
    code = (
        "from solution import LinkedStack, LinkedQueue\n"
        "s, q = LinkedStack(), LinkedQueue()\n"
        "for i in range(100000):\n"
        "    s.push(i)\n"
        "    q.enqueue(i)\n"
        "a = sum(s.pop() for _ in range(50000))\n"
        "b = sum(q.dequeue() for _ in range(50000))\n"
        "print(a, b, len(s), len(q))\n"
    )
    out = run_code(code, 20, "300,000 stack and queue operations (each must be O(1): no walking to the end)")
    want = f"{sum(range(50000, 100000))} {sum(range(50000))} 50000 50000"
    assert out == want, f"Expected {want!r}, got {out!r}."
