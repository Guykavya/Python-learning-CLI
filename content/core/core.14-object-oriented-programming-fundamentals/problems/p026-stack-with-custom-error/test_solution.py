import pytest

from solution import EmptyStackError, Stack, balanced


def test_error_is_an_exception_class():
    assert issubclass(EmptyStackError, Exception), "EmptyStackError must be a subclass of Exception."


def test_push_pop_order():
    s = Stack()
    s.push("a")
    s.push("b")
    s.push("c")
    assert s.pop() == "c", "pop returns the LAST item pushed (last in, first out)."
    assert s.pop() == "b", "Then the one below it."
    assert s.size() == 1, "One item is left."


def test_peek_does_not_remove():
    s = Stack([1, 2, 3])
    assert s.peek() == 3, "peek returns the top item (the last one in the starting list)."
    assert s.peek() == 3, "peek must not remove the item."
    assert s.size() == 3, "peek must not change the size."


def test_push_returns_none():
    s = Stack()
    assert s.push(5) is None, "push only changes the stack; it returns None."


def test_is_empty_and_size():
    s = Stack()
    assert s.is_empty() is True, "A new stack is empty."
    assert s.size() == 0, "A new stack has size 0."
    s.push(0)
    assert s.is_empty() is False, "A stack holding the item 0 is not empty. Check the number of items, not the item."


def test_to_list_bottom_first_and_a_copy():
    s = Stack([1, 2])
    s.push(3)
    out = s.to_list()
    assert out == [1, 2, 3], "to_list gives the items bottom first."
    out.append(99)
    assert s.size() == 3, "to_list must return a NEW list, so changing it does not change the stack."


def test_starting_items_are_copied():
    start = [1, 2]
    s = Stack(start)
    start.append(3)
    assert s.to_list() == [1, 2], "Keep your own copy of the starting items: list(items), not the same list."
    s.push(4)
    assert start == [1, 2, 3], "Pushing onto the stack must not change the caller's list."
    assert Stack(range(3)).to_list() == [0, 1, 2], "items can be any iterable, like range(3)."


def test_stacks_do_not_share_items():
    a = Stack()
    b = Stack()
    a.push("x")
    assert b.is_empty(), (
        "Pushing to one stack changed another. Do not use a mutable default like items=[]; "
        "use None and make a new list in __init__."
    )


def test_pop_empty_raises_custom_error():
    s = Stack()
    with pytest.raises(EmptyStackError, match="empty"):
        s.pop()


def test_pop_empty_is_not_indexerror():
    raised = None
    try:
        Stack().pop()
    except Exception as e:
        raised = e
    assert type(raised) is EmptyStackError, (
        f"pop() on an empty stack raised {type(raised).__name__}. Check for an empty list first and raise EmptyStackError."
    )


def test_peek_empty_raises_custom_error():
    s = Stack([1])
    s.pop()
    with pytest.raises(EmptyStackError, match="empty"):
        s.peek()


def test_balanced_true():
    assert balanced("") is True, "No brackets at all is balanced."
    assert balanced("f(a[0]) + {x}") is True, "Every bracket closes in the right order."
    assert balanced("{[()()]}") is True, "Nested brackets close inside out."


def test_balanced_wrong_kind_or_order():
    assert balanced("(]") is False, "')' must match '(' and ']' must match '['."
    assert balanced("([)]") is False, "The inner '[' must close before the outer '('."


def test_balanced_extra_closing():
    assert balanced("())") is False, "The second ')' has nothing to pop: catch EmptyStackError and return False."
    assert balanced(")(") is False, "A closing bracket first has nothing to match."


def test_balanced_unclosed():
    assert balanced("((") is False, "At the end the stack must be empty; two brackets were never closed."
