## Hint 1

Which built-in answers "is this true for every item?" What should it return for an empty list? And where does `TypeGuard` go: on the argument or on the return type?

## Hint 2

The return hint `TypeGuard[list[str]]` means "if I return `True`, the argument is a `list[str]`". The body is an ordinary boolean expression with `all(...)` and `isinstance`. For the dict, remember that `isinstance(True, int)` is `True`, so add `and not isinstance(v, bool)`.

## Hint 3

```
from typing import TypeGuard

def is_str_list(value: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(item, str) for item in value)

def is_int_dict(value: dict[str, object]) -> TypeGuard[dict[str, int]]:
    return all(isinstance(v, int) and not isinstance(v, bool) for v in value.values())

join_if_strings: if is_str_list(items): return ", ".join(items) ; return ""
sum_counts:      if is_int_dict(data): return sum(data.values()) ; raise ValueError
```
