import random
from collections import deque

from solution import StackFromQueue

FORBIDDEN = ["pop", "appendleft", "extendleft", "rotate", "reverse", "insert", "remove", "index", "count",
             "copy", "__reversed__", "__setitem__", "__delitem__", "__iter__", "__contains__"]


class QueueOnly(deque):
    """A deque that records every operation a plain queue does not have."""

    created = []

    def __init__(self, *args):
        super().__init__(*args)
        self.bad = []
        QueueOnly.created.append(self)

    def __getitem__(self, i):
        if i != 0:
            self.bad.append(f"q[{i}]")
        return deque.__getitem__(self, i)


def _forbidden(name):
    def method(self, *args, **kwargs):
        self.bad.append(name)
        return getattr(deque, name)(self, *args, **kwargs)
    return method


for _name in FORBIDDEN:
    setattr(QueueOnly, _name, _forbidden(_name))


def make():
    QueueOnly.created.clear()
    return StackFromQueue(QueueOnly)


def forbidden_calls():
    return sorted({b for q in QueueOnly.created for b in q.bad})


def test_example():
    s = make()
    for x in (1, 2, 3):
        s.push(x)
    got = (s.pop(), s.pop(), s.top())
    assert got == (3, 2, 1), f"Push 1, 2, 3 then pop, pop, top should give (3, 2, 1), got {got}."
    assert s.empty() is False


def test_uses_the_factory():
    s = make()
    s.push(1)
    assert QueueOnly.created, ("Create your queue with queue_factory() (the constructor argument), "
                               "not with deque() directly, so the tests can watch the operations.")


def test_only_queue_operations():
    s = make()
    for x in range(10):
        s.push(x)
    s.top()
    s.pop()
    s.push(99)
    s.top()
    s.pop()
    s.empty()
    bad = forbidden_calls()
    assert not bad, (f"You used {bad}, which a queue does not have. Allowed: append (back), popleft (front), "
                     "q[0], len and truth tests. Rotate items with q.append(q.popleft()).")


def test_random_against_list():
    rng = random.Random(23)
    s, model = make(), []
    for step in range(3000):
        op = rng.choice(["push", "push", "pop", "top", "empty"])
        if op == "push":
            x = rng.randint(0, 99)
            s.push(x)
            model.append(x)
        elif op == "pop" and model:
            assert s.pop() == model.pop(), f"Step {step}: pop() must return the newest item."
        elif op == "top" and model:
            assert s.top() == model[-1], f"Step {step}: top() should be {model[-1]}."
        assert s.empty() == (not model), f"Step {step}: empty() is wrong."
    assert not forbidden_calls(), f"Forbidden queue operations were used: {forbidden_calls()}."


def test_default_factory_works():
    s = StackFromQueue()
    s.push("a")
    s.push("b")
    assert s.pop() == "b" and s.pop() == "a" and s.empty(), "With the default factory (deque) it must work too."
