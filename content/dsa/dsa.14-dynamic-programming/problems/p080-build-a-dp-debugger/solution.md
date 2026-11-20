## Approach

A memoising decorator (chapter section 3, "A dictionary you manage yourself") plus a record of the states **in progress**. That record is the call stack of the DP, and it answers both debugging questions:

- a state that is already in progress is needed by itself: a **cycle**, so no order of evaluation can work;
- a stack that keeps growing past any sensible depth almost always means a state that never reaches a **base case** (`bad(-1)`, `bad(-2)`, ...).

Raising at `max_depth = 200` gives a short message naming the state, instead of Python's `RecursionError` with about 1,000 lines of traceback. It also keeps the program far from the real recursion limit, so the error is raised cleanly.

```python
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
```

**Reading the numbers for `fib(30)`.** 31 states (0 to 30) are computed. Each computed state from 2 to 30 makes two calls, 58 in all, plus the first call: 59. Of those, 31 computed something and 28 were hits. `deepest = 30`: the first path goes `fib(30) → fib(29) → … → fib(1)` before anything finishes, which is also why `(1,)` is the first state in the table.

**Using it.** On a wrong DP, print `wrapper.table` for a small input and check a few cells by hand (chapter section 23, step 1). A surprising `calls` count shows a memo that is not working (calls grow exponentially), and `deepest` tells you whether a top-down solution will survive a large input.

## Complexity

Each call costs `O(1)` on average (dict and set lookups, a list push and pop), so the debugger adds a constant factor to the DP. The cycle path costs `O(depth)`, but only when the error is raised.

## Another way

Keep the stack in a separate object (a class `DPTracer` with `__call__`), which makes the state easy to inspect and lets one tracer watch several mutually recursive functions with one shared stack. A cycle that goes `even(3) → odd(2) → even(3)` through two functions can only be found that way: per-function stacks see each function alone.
