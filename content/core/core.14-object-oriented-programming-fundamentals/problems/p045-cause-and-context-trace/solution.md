## Approach

Two different mechanisms link exceptions (chapter section 18):

- **Implicit chaining** (`__context__`): whenever an exception is raised while another one is being
  handled (inside an `except` block), Python stores the old one in `__context__`. You do not ask for
  it; it always happens.
- **Explicit chaining** (`__cause__`): `raise New from old` stores `old` in `__cause__` and sets
  `__suppress_context__ = True`, so the traceback shows "The above exception was the direct cause
  of the following exception" and not the context message. `raise New from None` sets
  `__cause__ = None` and `__suppress_context__ = True`: the traceback shows only the new error. The
  context is **still stored**; it is just not shown.

Now each function:

| func | why | cause | context | suppress |
|---|---|---|---|---|
| `a` | raised inside `except ValueError`, no `from` | None | ValueError | False |
| `b` | `from e`, and also inside `except KeyError` | KeyError | KeyError | True |
| `c` | `from None`, inside `except IndexError` | None | IndexError | True |
| `d` | `from OSError(...)`, not inside any `except` | OSError | None | True |
| `e` | the `NameError` (typo `totl`) happens inside `except ZeroDivisionError` | None | ZeroDivisionError | False |
| `f` | the `except` block already finished | None | None | False |

`e` shows why tracebacks say "During handling of the above exception, another exception occurred":
a bug **inside** a handler is chained to the error being handled.

`g`: `RuntimeError` has `__cause__` = the `ConfigError("missing port")` from `b()`, whose `__cause__`
is the `KeyError`, whose `__cause__` is `None`. The loop prints `RuntimeError -> ConfigError -> KeyError`.

## Output

```text
a: ConfigError - bad number
  cause: None
  context: ValueError
  suppress: False
b: ConfigError - missing port
  cause: KeyError
  context: KeyError
  suppress: True
c: ConfigError - empty list
  cause: None
  context: IndexError
  suppress: True
d: ConfigError - direct
  cause: OSError
  context: None
  suppress: True
e: NameError - name 'totl' is not defined
  cause: None
  context: ZeroDivisionError
  suppress: False
f: ConfigError - after
  cause: None
  context: None
  suppress: False
RuntimeError -> ConfigError -> KeyError
```

## Complexity

Not applicable.

## Another way

Run each function without the `try` around it and read the full traceback Python prints. With
`a` and `e` you see "During handling of the above exception, another exception occurred"; with `b`
and `d` "The above exception was the direct cause of the following exception"; with `c` only the
`ConfigError`. Those three traceback shapes are exactly the three combinations of `__cause__`,
`__context__` and `__suppress_context__`.
