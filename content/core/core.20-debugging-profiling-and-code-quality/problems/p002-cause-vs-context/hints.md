## Hint 1

For each function ask two separate questions. (1) Was another exception **being handled**
(are we inside an `except` block) when the new one was raised? Then `__context__` is that one.
(2) Is there a `from`? Then `__cause__` is what follows `from` (`None` for `from None`) and
`__suppress_context__` is `True`.

## Hint 2

Two special cases. `from None` does **not** erase `__context__`; it only hides it. A bare
`raise` inside `except` re-raises the **same** object, and an exception is never its own
context.

```
explicit:   cause=ValueError  context=ValueError   suppress=True
implicit:   cause=None        context=KeyError     suppress=False
hidden:     cause=None        context=ZeroDivision suppress=True
...work out the other four the same way
```
