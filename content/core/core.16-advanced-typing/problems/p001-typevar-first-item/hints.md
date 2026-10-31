## Hint 1

If the parameter is `Sequence[int]` the result is an `int`; if it is `Sequence[str]` the result is a `str`. What do you write in place of `int` or `str` so that one definition covers every case? And what must the return hint be, so the two are *linked*?

## Hint 2

Use one `TypeVar` in both places: `Sequence[T]` for the parameter and `T` for the return. In `first_or`, the default is also an item, so it is also a `T`. For `last_or_none` the result is "an item or nothing": `T | None`. How do you test for an empty sequence without breaking when the last item is `0`?

## Hint 3

```
T = TypeVar("T")

def first(items: Sequence[T]) -> T:
    return items[0]               # IndexError for free

def first_or(items: Sequence[T], default: T) -> T:
    if len(items) == 0: return default
    return items[0]

def last_or_none(items: Sequence[T]) -> T | None:
    if len(items) == 0: return None
    return items[-1]
```
