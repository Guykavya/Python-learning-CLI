## Hint 1

Run the file through mypy if you can, or reason about the promise: what does each function tell the checker when it returns `True`? And when it returns `False`?

## Hint 2

In the `else` branch of an `isinstance(v, str)` check on an `int | str`, what is left? Which of the two helpers promises enough for the checker to do the same?

## Hint 3

For question 3, test `is_non_empty("")`. It is a `str`, and the function returns `False`. What would `TypeIs` conclude about it? For question 4, remember the rule: the narrowed type of a `TypeIs` must be a *subtype* of the input type. Is `list[str]` a subtype of `list[object]`?
