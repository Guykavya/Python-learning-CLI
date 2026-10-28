# trace_calls: show every recursive call as a tree

When you decorate a recursive function, the recursive calls **also** go through the wrapper.
Why? Inside the body, the name `fact` is looked up **when the call happens**, and by then the
name `fact` refers to the wrapper. You can use this to draw a call tree.

Write a decorator factory `trace_calls(log)` in `solution.py`. For each call of the decorated
function it appends two lines to the list `log`:

- on entry: `INDENT + "name(arguments)"`
- on return: `INDENT + "-> " + repr(result)`

where `INDENT` is two spaces for each level of depth: 0 for the outermost call, 1 for a call made
from inside it, and so on. Arguments are written with `repr` and joined by `", "`; keyword
arguments come after positional ones as `key=repr(value)`.

If the function raises, append `INDENT + "!! " + exception class name` instead of the `->` line,
and let the exception continue. The depth must always go back down, even after an exception, so
the next call starts at depth 0 again. Each decorated function keeps its own depth. Use
`functools.wraps`.

**Example**

```python
log = []

@trace_calls(log)
def fact(n):
    return 1 if n <= 1 else n * fact(n - 1)

fact(3)
print("\n".join(log))
```

```text
fact(3)
  fact(2)
    fact(1)
    -> 1
  -> 2
-> 6
```

A string argument shows with quotes: `greet('ann', loud=True)`.

**Think about it:** what does `fact.__wrapped__(3)` log? The outer call skips the wrapper, but
the recursive call inside still uses the global name `fact`. (A test checks this. Your code does
not need anything special for it; just understand why.)
