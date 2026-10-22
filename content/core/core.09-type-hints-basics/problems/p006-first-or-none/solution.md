## Approach

`first_or_none` checks for the empty list and returns `None`, otherwise returns `items[0]`. Its return type is the union `int | None`, because both can happen.

`first_or_default` calls `first_or_none` and narrows the result with `is None`. Using `is None` (not `if not first`) matters: `0` is a valid first item and must not be replaced by the default. After the check, mypy knows `first` is an `int`, so returning it satisfies `-> int`.

## Code

```python
def first_or_none(items: list[int]) -> int | None:
    if not items:
        return None
    return items[0]


def first_or_default(items: list[int], default: int) -> int:
    first = first_or_none(items)
    if first is None:
        return default
    return first
```

## Complexity

O(1) for both.

## Another way

`first_or_default` can also be written as `return items[0] if items else default`, which skips `first_or_none` entirely. The version above is a good exercise in narrowing, which you need whenever a function returns `X | None`.
