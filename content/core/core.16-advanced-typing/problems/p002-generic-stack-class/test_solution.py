from typing import Generic, TypeVar, get_origin, get_type_hints

import pytest

from solution import Stack


def type_var():
    assert len(getattr(Stack, "__parameters__", ())) == 1, (
        "Stack must be generic in ONE type variable: class Stack(Generic[T]) (or class Stack[T])."
    )
    (t,) = Stack.__parameters__
    assert isinstance(t, TypeVar), "The parameter of Stack must be a TypeVar."
    return t


def test_is_generic():
    t = type_var()
    bases = getattr(Stack, "__orig_bases__", ())
    assert any(get_origin(b) is Generic for b in bases), "Inherit from Generic[T] so that Stack[int] is allowed."
    assert t.__name__ == "T", "Name the TypeVar T."


def test_subscript_works():
    assert get_origin(Stack[int]) is Stack, "Stack[int] must be allowed: the class has to be generic."


def test_method_hints():
    t = type_var()
    assert get_type_hints(Stack.push) == {"item": t, "return": type(None)}, "push(self, item: T) -> None, with the class's TypeVar T."
    assert get_type_hints(Stack.pop) == {"return": t}, "pop returns an item: -> T, the class's TypeVar."
    assert get_type_hints(Stack.peek) == {"return": t}, "peek returns an item: -> T, the class's TypeVar."
    assert get_type_hints(Stack.is_empty) == {"return": bool}, "is_empty -> bool."
    assert get_type_hints(Stack.__len__) == {"return": int}, "__len__ -> int."
    assert get_type_hints(Stack.__init__) == {"return": type(None)}, "__init__(self) -> None."


def test_push_pop_order():
    s = Stack()
    for x in (1, 2, 3):
        s.push(x)
    assert [s.pop(), s.pop(), s.pop()] == [3, 2, 1], "A stack is last in, first out: pop returns the most recently pushed item."


def test_peek_does_not_remove():
    s = Stack()
    s.push("a")
    s.push("b")
    assert s.peek() == "b" and s.peek() == "b", "peek returns the top item without removing it."
    assert len(s) == 2, "peek must not change the size."


def test_len_and_empty():
    s = Stack()
    assert s.is_empty() is True and len(s) == 0, "A new stack is empty."
    s.push(0)
    assert s.is_empty() is False and len(s) == 1, "After one push: not empty, length 1 (0 is a valid item)."
    s.pop()
    assert s.is_empty() is True, "After popping the last item the stack is empty again."


def test_empty_errors():
    s = Stack()
    with pytest.raises(IndexError, match="pop from empty stack"):
        s.pop()
    with pytest.raises(IndexError, match="pop from empty stack"):
        s.peek()


def test_stacks_are_independent():
    a, b = Stack(), Stack()
    a.push(1)
    assert len(b) == 0, "Each Stack needs its own list, created in __init__ (not a shared class attribute)."


def test_subscripted_instance():
    s = Stack[int]()
    s.push(5)
    assert s.pop() == 5, "Stack[int]() creates a normal Stack."
