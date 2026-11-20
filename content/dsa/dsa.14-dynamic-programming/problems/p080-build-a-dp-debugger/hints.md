## Hint 1

Start with a plain memoising decorator: a `wrapper(*args)` that looks `args` up in a dict `wrapper.table`, and otherwise calls `f(*args)` and stores the result. Functions are objects, so the counters can be attributes: `wrapper.calls = 0` after defining it. Inside `fib`, the name `fib` refers to the **wrapper**, so the recursive calls also go through it.

For the two ways of using it: `dp_debug(func=None, *, max_depth=200)`. With `@dp_debug`, Python passes the function; with `@dp_debug(max_depth=50)`, `func` is `None` and you must return the decorator itself.

## Hint 2

Keep a list `stack` of the states in progress (and a set of the same states for fast lookups). Before computing a state:

- already in `table`? It is a hit, return it.
- already in the stack? A cycle: the cycle is the part of the stack from that state to the end, plus the state again.
- the stack already holds `max_depth` states? Missing base case.

Otherwise push, compute, pop. Do the pop in a `finally:` block, so an exception cannot leave old states behind.

## Hint 3

```
def decorate(f):
    @functools.wraps(f)
    def wrapper(*args):
        wrapper.calls += 1
        if args in wrapper.table: wrapper.hits += 1; return wrapper.table[args]
        if args in open_states: raise CyclicState(path from args back to args)
        if len(stack) >= max_depth: raise MissingBaseCase(... show(args) ...)
        stack.append(args); open_states.add(args)
        wrapper.deepest = max(wrapper.deepest, len(stack))
        try: value = f(*args)
        finally: stack.pop(); open_states.discard(args)
        wrapper.table[args] = value
        return value
    wrapper.reset = ...   # sets table, calls, hits, deepest, stack, open_states back
    wrapper.reset()
    return wrapper
return decorate(func) if func is not None else decorate
```

`show(state)` = `f"{f.__name__}({', '.join(map(repr, state))})"`.
