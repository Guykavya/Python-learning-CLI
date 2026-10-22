## Hint 1

What does "the list is empty" look like in code? Which of `if items:` and `if len(items) == 0:` is clearer to read? What do you return for an empty list in the first function?

## Hint 2

`first_or_none` can return an `int` on one path and `None` on another, so its hint is a union. For `first_or_default`, can you build it on top of `first_or_none`? Then you must handle the `None` before returning.

## Hint 3

```
def first_or_none(items: list[int]) -> int | None:
    if not items: return None
    return items[0]

def first_or_default(items: list[int], default: int) -> int:
    first = first_or_none(items)
    if first is None: return default
    return first
```
