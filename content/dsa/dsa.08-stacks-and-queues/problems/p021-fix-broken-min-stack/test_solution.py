import random

from solution import MinStack


def test_the_bug_report():
    m = MinStack()
    m.push(5)
    m.push(3)
    m.push(3)
    assert m.pop() == 3
    assert m.get_min() == 3, (
        "After push 5, 3, 3 and one pop, the stack is [5, 3]: the minimum is 3. The second 3 was never "
        "recorded in mins, so the pop removed the only copy. Record equal values too (<=).")
    assert m.pop() == 3
    assert m.get_min() == 5, "After popping both 3s, the minimum is 5 again."


def test_crash_case():
    m = MinStack()
    m.push(2)
    m.push(2)
    m.pop()
    m.pop()
    m.push(9)
    try:
        got = m.get_min()
    except IndexError:
        raise AssertionError("push 2, push 2, pop, pop, push 9: get_min() crashed because mins is out of step with items.") from None
    assert got == 9, "Only 9 is left, so the minimum is 9."


def test_many_equal_minimums():
    m = MinStack()
    for _ in range(5):
        m.push(1)
    for left in range(4, 0, -1):
        m.pop()
        assert m.get_min() == 1, f"{left} copies of 1 are still on the stack: the minimum is 1."


def test_random_against_list():
    rng = random.Random(21)
    m, model = MinStack(), []
    for step in range(5000):
        if model and rng.random() < 0.45:
            assert m.pop() == model.pop(), f"Step {step}: pop() returned the wrong value."
        else:
            x = rng.randint(0, 6)                      # small range: many equal values
            m.push(x)
            model.append(x)
        if model:
            assert m.top() == model[-1], f"Step {step}: top() is wrong."
            assert m.get_min() == min(model), (
                f"Step {step}: get_min() should be {min(model)}, got {m.get_min()}. "
                "Equal values must be recorded in mins too.")


def test_design_kept():
    m = MinStack()
    for x in range(1, 1001):
        m.push(x)
    assert hasattr(m, "mins") and isinstance(m.mins, list), "Keep the two-list design with self.mins."
    assert len(m.mins) <= 2, (
        f"After pushing 1, 2, ..., 1000, mins has {len(m.mins)} entries; it should hold only the minimum 1. "
        "Fix the comparison instead of pushing every value onto mins.")
    assert m.get_min() == 1
