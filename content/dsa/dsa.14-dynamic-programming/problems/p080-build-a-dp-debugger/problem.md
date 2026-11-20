# Build a DP debugger

`functools.cache` memoises, but when a recursion is wrong it tells you nothing: you get a wrong number, a `RecursionError` after 1,000 frames, or a program that never ends. Build a decorator `dp_debug` that memoises **and** shows what happened (chapter section 23, "Debugging a DP").

## What to build

`starter.py` already defines three exception classes: `DPError`, and its two subclasses `MissingBaseCase` and `CyclicState`. Write `dp_debug` so that it can be used in two ways:

```python
@dp_debug
def fib(n): ...

@dp_debug(max_depth=50)
def countdown(n): ...
```

The decorated function takes **positional arguments only**; the tuple of arguments is the **state**. The wrapper must:

1. **Memoise.** Each state is computed once. Its value goes into `wrapper.table`, a `dict` from the state tuple to the value, in the order the states **finish** (so `(5,)` for `fib(5)`).
2. **Count.** `wrapper.calls` = how many times the wrapper was called (memo hits included); `wrapper.hits` = how many of those were answered from the table; `wrapper.deepest` = the largest number of states that were in progress at the same time.
3. **Catch a missing base case.** When a call would put more than `max_depth` states (default 200) in progress at once, raise `MissingBaseCase` instead of computing. The message must contain that state written like a call, e.g. `bad(-200)`.
4. **Catch a cycle.** When a state is called while it is **already in progress** (it needs its own value), raise `CyclicState`. The message must show the cycle, e.g. `spin(1) -> spin(2) -> spin(3) -> spin(1)`.
5. **Stay usable after an error.** Whatever exception is raised (yours or one from the function), the in-progress states must be cleared, so the next call works normally.
6. **`wrapper.reset()`** empties the table and sets the counters back to 0.
7. Keep the function's name: `fib.__name__ == "fib"` (use `functools.wraps`).

## Example

```python
>>> @dp_debug
... def fib(n):
...     return n if n < 2 else fib(n - 1) + fib(n - 2)
>>> fib(30)
832040
>>> len(fib.table), fib.calls, fib.hits, fib.deepest
(31, 59, 28, 30)
>>> list(fib.table)[:3]
[(1,), (0,), (2,)]

>>> @dp_debug
... def bad(n):                    # no base case
...     return bad(n - 1) + 1
>>> bad(0)
Traceback (most recent call last):
  ...
MissingBaseCase: depth limit 200 reached at bad(-200): missing base case? last states: bad(-196) -> bad(-197) -> bad(-198) -> bad(-199) -> bad(-200)

>>> @dp_debug
... def spin(n):                   # 1 needs 2, 2 needs 3, 3 needs 1
...     return spin(n % 3 + 1)
>>> spin(1)
Traceback (most recent call last):
  ...
CyclicState: cycle: spin(1) -> spin(2) -> spin(3) -> spin(1)
```

Your messages may use other words; the tests only look for the states (`bad(-200)`, and the cycle `spin(1) -> spin(2) -> spin(3) -> spin(1)`).

## Think about

1. Why are `fib.calls` 59 and `fib.hits` 28 for `fib(30)`? (Each computed state `n >= 2` makes two calls.)
2. Why does `fib.table` start with `(1,)` and not `(0,)` or `(30,)`?
3. How can the wrapper know which states are "in progress"? What must happen to that record when the function raises an exception halfway?
4. Why is it better to raise `MissingBaseCase` at depth 200 than to let Python raise `RecursionError` at about 1,000 frames?
