class EmptyStackError(Exception):
    """Raised when you pop or peek at an empty stack."""


class Stack:
    def __init__(self, items=None):
        self._items = [] if items is None else list(items)

    def push(self, item):
        self._items.append(item)

    def pop(self):
        if not self._items:
            raise EmptyStackError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        if not self._items:
            raise EmptyStackError("peek at empty stack")
        return self._items[-1]

    def is_empty(self):
        return not self._items

    def size(self):
        return len(self._items)

    def to_list(self):
        return list(self._items)


PAIRS = {")": "(", "]": "[", "}": "{"}


def balanced(text):
    stack = Stack()
    for ch in text:
        if ch in "([{":
            stack.push(ch)
        elif ch in PAIRS:
            try:
                top = stack.pop()
            except EmptyStackError:
                return False
            if top != PAIRS[ch]:
                return False
    return stack.is_empty()
