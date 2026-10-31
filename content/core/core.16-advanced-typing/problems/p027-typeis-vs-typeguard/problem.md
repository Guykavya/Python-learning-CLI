# Explain: TypeIs versus TypeGuard

Asha writes two helper functions that look almost the same, and a function that uses them
(Python 3.13+, or `typing_extensions` before that):

```python
from typing import TypeGuard, TypeIs


def guard_str(x: object) -> TypeGuard[str]:
    return isinstance(x, str)


def is_str(x: object) -> TypeIs[str]:
    return isinstance(x, str)


def f(v: int | str) -> None:
    if guard_str(v):
        reveal_type(v)      # line A
    else:
        reveal_type(v)      # line B
    if is_str(v):
        reveal_type(v)      # line C
    else:
        reveal_type(v)      # line D
```

In `answer.md` (about 150 to 300 words), explain:

1. What type does mypy reveal on each of the lines A, B, C and D?
2. Why do B and D differ, although both helpers return the same `bool` at run time?
3. Asha now writes `def is_non_empty(x: object) -> TypeIs[str]: return isinstance(x, str) and x != ""`.
   What goes wrong? Which of `TypeIs` and `TypeGuard` should she use instead, and why?
4. Give one more situation where only `TypeGuard` is allowed. (Hint: think of a `list[object]`
   that you want to treat as `list[str]`.)

See the model answer shown when you check.
