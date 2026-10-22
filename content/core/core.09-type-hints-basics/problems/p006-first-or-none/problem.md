# first_or_none: a maybe-value

Write two functions in `solution.py`, with hints.

1. `first_or_none(items)` takes a list of whole numbers and returns the **first** item, or `None`
   if the list is empty. Its return hint must say that the result may be `None`.
2. `first_or_default(items, default)` takes a list of whole numbers and a whole-number default,
   and returns the first item, or `default` if the list is empty. This one never returns `None`.

Hints required by the tests:

- `first_or_none(items: list[int]) -> int | None`
- `first_or_default(items: list[int], default: int) -> int`

**Careful**: `0` is a valid first item. `first_or_none([0, 5])` is `0`, not `None`.

**Examples**

```python
first_or_none([4, 5])           # 4
first_or_none([])               # None
first_or_none([0, 5])           # 0
first_or_default([], -1)        # -1
first_or_default([7], -1)       # 7
```
