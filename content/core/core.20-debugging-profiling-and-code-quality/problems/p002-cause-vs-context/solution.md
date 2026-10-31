## Approach

Go function by function and answer three questions: what was being handled (context), what
follows `from` (cause), and was `from` used at all (suppress).

| Function | Being handled | `from` | Result |
|---|---|---|---|
| `explicit` | `ValueError` from `int("x")` | `from e` (the same ValueError) | cause and context are both `ValueError`, suppress `True` |
| `implicit` | `KeyError` | none | cause `None`, context `KeyError`, suppress `False` |
| `hidden` | `ZeroDivisionError` | `from None` | cause `None`, context **still** `ZeroDivisionError`, suppress `True` |
| `broken_handler` | `IndexError` | none (a bug in the handler raised `NameError`) | context `IndexError` |
| `plain` | nothing | none | all empty |
| `reraise` | the `OSError` itself | bare `raise` re-raises the same object | its context was empty when it was first raised and stays empty |
| `cause_only` | nothing | `from AttributeError(...)` | cause `AttributeError`, context `None`, suppress `True` |

The surprising one is `hidden`: `from None` only sets `__cause__ = None` and
`__suppress_context__ = True`. The old exception is still there in `__context__`, the printer
just does not show it. That is useful when debugging: the information is not lost.

`broken_handler` is the classic "bug inside an except block". Its traceback says *"During
handling of the above exception, another exception occurred"*, and the useful error is the
**second** one (the typo), not the `IndexError`.

## Output

```text
explicit KeyError ValueError ValueError True
implicit TypeError NoneType KeyError False
hidden ValueError NoneType ZeroDivisionError True
broken_handler NameError NoneType IndexError False
plain RuntimeError NoneType NoneType False
reraise OSError NoneType NoneType False
cause_only LookupError AttributeError NoneType True
```
