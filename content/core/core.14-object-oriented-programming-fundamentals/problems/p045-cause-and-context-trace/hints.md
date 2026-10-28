## Hint 1

For each function, ask two questions. (1) Was the new exception raised **inside an `except`
block**, while another exception was being handled? If yes, that other one is the `__context__`.
(2) Was there a `from`? If `from X`, then `__cause__` is `X` and `__suppress_context__` is `True`;
`from None` gives `__cause__ = None` but **also** sets `__suppress_context__` to `True`.

## Hint 2

Fill in a small table before writing the output:

```text
func  raised inside except?  from ...?     cause   context   suppress
a     yes (ValueError)       no            ?       ?         ?
b     yes (KeyError)         from e        ?       ?         ?
c     yes (IndexError)       from None     ?       ?         ?
d     no                     from OSError  ?       ?         ?
e     yes (ZeroDivision)     no            ?       ?         ?
f     no (handled, finished) no            ?       ?         ?
```

`from None` does **not** erase `__context__`; it only hides it in the traceback.

## Hint 3

In `e`, the `NameError` happens inside the `except` block, so it is chained to the
`ZeroDivisionError` like any other exception. In `f`, the `except` block finished before the
`raise`, so nothing is being handled any more. For `g`, follow `__cause__` only:
`RuntimeError` was raised `from` the `ConfigError` of `b()`, which itself was raised `from` the
`KeyError`.
