import random

import pytest

from solution import Stack


def test_example():
    s = Stack()
    s.push(10)
    s.push(20)
    assert s.peek() == 20, "peek() returns the item pushed LAST (the top)."
    assert len(s) == 2, "len(s) is the number of items; define __len__."
    assert s.pop() == 20, "pop() returns the newest item first (LIFO). Did you pop from the front?"
    assert s.pop() == 10, "The second pop returns the older item."
    assert s.is_empty() is True, "After popping everything, is_empty() must be True."


def test_new_stack_is_empty():
    s = Stack()
    assert s.is_empty() is True, "A new Stack is empty."
    assert len(s) == 0, "A new Stack has length 0."


def test_peek_does_not_remove():
    s = Stack()
    s.push("a")
    s.peek()
    s.peek()
    assert len(s) == 1 and s.pop() == "a", "peek() must not remove the item."


def test_pop_empty_raises_with_message():
    s = Stack()
    with pytest.raises(IndexError) as info:
        s.pop()
    assert str(info.value) == "pop from empty stack", (
        f"pop() on an empty stack must raise IndexError('pop from empty stack'), the message was {str(info.value)!r}. "
        "Check for emptiness first and raise your own error.")


def test_peek_empty_raises_with_message():
    s = Stack()
    with pytest.raises(IndexError) as info:
        s.peek()
    assert str(info.value) == "peek at empty stack", (
        f"peek() on an empty stack must raise IndexError('peek at empty stack'), the message was {str(info.value)!r}.")


def test_pop_after_emptied_raises():
    s = Stack()
    s.push(1)
    s.pop()
    with pytest.raises(IndexError):
        s.pop()


def test_falsy_values_are_real_items():
    s = Stack()
    s.push(None)
    s.push(0)
    assert s.is_empty() is False, "A stack holding 0 and None is NOT empty: test len, not the value on top."
    assert s.pop() == 0 and s.pop() is None, "0 and None are ordinary items."
    assert s.is_empty() is True


def test_random_operations_against_a_list():
    rng = random.Random(2)
    s, model = Stack(), []
    for step in range(3000):
        op = rng.choice(["push", "push", "pop", "peek", "len"])
        if op == "push":
            x = rng.randint(-50, 50)
            s.push(x)
            model.append(x)
        elif op == "pop":
            if model:
                assert s.pop() == model.pop(), f"Step {step}: pop() returned the wrong item; the top is the END of the list."
            else:
                with pytest.raises(IndexError):
                    s.pop()
        elif op == "peek":
            if model:
                assert s.peek() == model[-1], f"Step {step}: peek() should be {model[-1]}."
        else:
            assert len(s) == len(model), f"Step {step}: len should be {len(model)}, got {len(s)}."
        assert s.is_empty() == (not model), f"Step {step}: is_empty() is wrong."
