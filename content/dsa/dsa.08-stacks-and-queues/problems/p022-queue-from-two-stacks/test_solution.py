import ast
import random
import subprocess
import sys
from collections import deque
from pathlib import Path

from solution import QueueFromStacks

HERE = Path(__file__).parent
SOLUTION = HERE / "solution.py"


def run_code(code, timeout, what):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{what} took more than {timeout} seconds.") from None
    assert r.returncode == 0, f"Your code crashed:\n{r.stderr[-800:]}"
    return r.stdout.strip()


def test_example():
    q = QueueFromStacks()
    for x in (1, 2, 3):
        q.push(x)
    assert q.pop() == 1, "pop() must return the OLDEST item (1). Popping the inbox directly gives the newest."
    q.push(4)
    assert q.peek() == 2, "peek() is the oldest remaining item, 2."
    got = [q.pop(), q.pop(), q.pop()]
    assert got == [2, 3, 4], (
        f"After pushing 4, the queue must give 2, 3, 4, got {got}. If 4 came out too early, you refilled "
        "the outbox while it still held older items.")
    assert q.empty() is True, "Everything was popped: empty() must be True."


def test_new_queue_is_empty():
    q = QueueFromStacks()
    assert q.empty() is True
    q.push(None)
    assert q.empty() is False, "A queue holding None is not empty."


def test_random_against_deque():
    rng = random.Random(22)
    q, model = QueueFromStacks(), deque()
    for step in range(5000):
        op = rng.choice(["push", "push", "pop", "peek", "empty"])
        if op == "push":
            x = rng.randint(0, 999)
            q.push(x)
            model.append(x)
        elif op == "pop" and model:
            assert q.pop() == model.popleft(), f"Step {step}: pop() must return the oldest item {model[0] if model else ''}."
        elif op == "peek" and model:
            assert q.peek() == model[0], f"Step {step}: peek() should be {model[0]}."
        assert q.empty() == (not model), f"Step {step}: empty() is wrong."


def test_only_stack_operations():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {
        n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert "deque" not in names, "Do not use deque here: build the queue from two lists used as stacks."
    assert "insert" not in names, "list.insert is not a stack operation."
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "pop" and n.args:
            raise AssertionError("pop(...) with an argument (like pop(0)) is not a stack operation: use pop() only.")
        if isinstance(n, ast.Slice):
            raise AssertionError("Slicing copies part of a list; use only append, pop(), [-1] and len.")


def test_amortised_time():
    code = (
        "from solution import QueueFromStacks\n"
        "q = QueueFromStacks()\n"
        "for i in range(100000):\n"
        "    q.push(i)\n"
        "total = 0\n"
        "for i in range(100000):\n"
        "    total += q.pop()\n"
        "    q.push(i)\n"
        "print(total)\n"
    )
    out = run_code(code, 20, "300,000 operations on a queue of 100,000 items (each item may move between the stacks "
                   "only once: refill the outbox only when it is empty, and never pour items back)")
    assert out == str(sum(range(100000))), f"The popped items should add up to {sum(range(100000))}, got {out}."
