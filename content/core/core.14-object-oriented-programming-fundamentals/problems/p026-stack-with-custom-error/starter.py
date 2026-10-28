class EmptyStackError(Exception):
    pass


class Stack:
    def __init__(self, items=None):
        # TODO: keep your own list of items
        pass

    def push(self, item):
        pass

    def pop(self):
        # TODO: raise EmptyStackError when there is nothing to pop
        return None

    def peek(self):
        return None

    def is_empty(self):
        return True

    def size(self):
        return 0

    def to_list(self):
        return []


def balanced(text):
    # TODO: use a Stack and catch EmptyStackError
    return True
