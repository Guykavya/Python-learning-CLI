## Approach

`TypeGuard[X]` as a return type turns a boolean function into a narrowing tool: in the `if` branch
where it returned `True`, the checker treats the argument as `X`. The checker cannot see inside
your function, so the body is plain code: `all(...)` over the items with `isinstance`.
`all([])` is `True`, which is the right answer for "no item is wrong".

The `bool` special case comes from Python: `True` is an instance of `int`, so a count check must
exclude it explicitly.

## Code

```python
from typing import TypeGuard


def is_str_list(value: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(item, str) for item in value)


def is_int_dict(value: dict[str, object]) -> TypeGuard[dict[str, int]]:
    return all(isinstance(v, int) and not isinstance(v, bool) for v in value.values())


def join_if_strings(items: list[object]) -> str:
    if is_str_list(items):
        return ", ".join(items)
    return ""


def sum_counts(data: dict[str, object]) -> int:
    if is_int_dict(data):
        return sum(data.values())
    raise ValueError("every value must be an int")
```

## Complexity

O(n) for each function (the guards stop at the first bad item).

## Another way

Without a guard you can use `cast`: `", ".join(cast(list[str], items))`, but then nothing checks
the list. Another option is to build a new, checked list: `[x for x in items if isinstance(x, str)]`
is a real `list[str]` and needs no guard, at the cost of silently dropping bad items.
`TypeIs` (next problem) is the stricter sibling, but it requires the narrowed type to be a
subtype of the input type, and `list[str]` is not a subtype of `list[object]` (lists are
invariant), so `TypeGuard` is the right tool here.
