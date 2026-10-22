## Approach

One annotation per variable, in the form `name: type = value`. The empty collections are the important ones: `tags: list[str] = []` tells mypy what will be stored, so a later `tags.append(7)` can be flagged. The pair of ints is a fixed-shape tuple, `tuple[int, int]`. The "text or nothing" variable is `str | None`.

## Code

```python
count: int = 0
price: float = 9.5
title: str = "Report"
tags: list[str] = []
stock: dict[str, int] = {}
origin: tuple[int, int] = (0, 0)
nickname: str | None = None
```

## Complexity

No runtime cost: variable annotations on a module are only stored, never checked.

## Another way

For a variable that is assigned right away with a non-empty value, such as `count = 0`, mypy infers `int` by itself and a hint is optional. The hints here are required because the exercise is about writing them, and because `tags`, `stock` and `nickname` could not be inferred.
