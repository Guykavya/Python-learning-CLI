## Approach

`int()` raises `ValueError` for text that is not a whole number, so `safe_int` wraps it in `try/except ValueError` and returns `None` in the `except`. Its return type is `int | None`.

`safe_int_or` calls `safe_int` and narrows the result with `if n is None`. After that check mypy knows `n` is an `int`. Using `is None` keeps `0` a valid answer.

`parse_all` maps `safe_int` over the texts and keeps the items that `is not None`. mypy understands that inside such a comprehension filter the items are plain `int`, so the declared `list[int]` is correct.

## Code

```python
def safe_int(text: str) -> int | None:
    try:
        return int(text.strip())
    except ValueError:
        return None


def safe_int_or(text: str, default: int) -> int:
    n = safe_int(text)
    if n is None:
        return default
    return n


def parse_all(texts: list[str]) -> list[int]:
    return [n for n in map(safe_int, texts) if n is not None]
```

## Complexity

`safe_int` and `safe_int_or` are O(len(text)). `parse_all` is O(total length of all texts).

## Another way

`parse_all` with an ordinary loop: create `result: list[int] = []`, loop over the texts, call `safe_int`, and `append` only when the result `is not None`.
