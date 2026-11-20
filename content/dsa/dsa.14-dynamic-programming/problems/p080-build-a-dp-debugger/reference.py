import functools


class DPError(Exception):
    """Base class for the debugger's own errors."""


class MissingBaseCase(DPError):
    """The recursion went deeper than max_depth: probably a state that never reaches a base case."""


class CyclicState(DPError):
    """A state needs its own value (directly or through other states): the recursion has a cycle."""


def dp_debug(func=None, *, max_depth=200):
    def decorate(f):
        def show(state):
            return f"{f.__name__}({', '.join(map(repr, state))})"

        @functools.wraps(f)
        def wrapper(*args):
            wrapper.calls += 1
            state = args
            if state in wrapper.table:                 # already computed: a memo hit
                wrapper.hits += 1
                return wrapper.table[state]
            if state in wrapper._open:                 # on the stack right now: a cycle
                start = wrapper._stack.index(state)
                path = " -> ".join(show(s) for s in wrapper._stack[start:] + [state])
                raise CyclicState(f"cycle: {path}")
            if len(wrapper._stack) >= max_depth:       # too deep: a missing base case?
                tail = " -> ".join(show(s) for s in wrapper._stack[-4:] + [state])
                raise MissingBaseCase(
                    f"depth limit {max_depth} reached at {show(state)}: missing base case? last states: {tail}")
            wrapper._stack.append(state)
            wrapper._open.add(state)
            wrapper.deepest = max(wrapper.deepest, len(wrapper._stack))
            try:
                value = f(*args)
            finally:                                   # always leave the stack clean, even on an error
                wrapper._stack.pop()
                wrapper._open.discard(state)
            wrapper.table[state] = value
            return value

        def reset():
            wrapper.table = {}
            wrapper.calls = 0
            wrapper.hits = 0
            wrapper.deepest = 0
            wrapper._stack = []
            wrapper._open = set()

        wrapper.reset = reset
        reset()
        return wrapper

    if func is not None:                               # used as @dp_debug
        return decorate(func)
    return decorate                                    # used as @dp_debug(max_depth=...)
