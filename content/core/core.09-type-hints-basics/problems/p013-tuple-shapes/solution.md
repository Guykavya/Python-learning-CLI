## Approach

A function that returns "a low and a high" has a fixed shape: `tuple[int, int]`. A function that takes or returns a sequence of unknown length uses `tuple[int, ...]`. `head_tail` combines the two: a fixed pair of (maybe an int, an any-length tuple).

`sorted(set(numbers))` removes duplicates and sorts, but returns a list, so `tuple(...)` converts it back. In `split_name`, `str.split(maxsplit=1)` splits at the first run of whitespace and gives a list of 0, 1 or 2 parts. Slicing a tuple (`numbers[1:]`) gives a tuple.

## Code

```python
def min_max(numbers: list[int]) -> tuple[int, int]:
    return min(numbers), max(numbers)


def sorted_unique(numbers: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(set(numbers)))


def split_name(full: str) -> tuple[str, str]:
    parts = full.split(maxsplit=1)
    if len(parts) == 0:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def head_tail(numbers: tuple[int, ...]) -> tuple[int | None, tuple[int, ...]]:
    if not numbers:
        return None, ()
    return numbers[0], numbers[1:]
```

## Complexity

`min_max` O(n). `sorted_unique` O(n log n). `split_name` O(len(full)). `head_tail` O(n) because slicing copies.

## Another way

`split_name` could use `full.partition(" ")`, which always returns a fixed 3-tuple `(before, separator, after)` and never needs the length checks. Be careful: `partition` splits at a space only and does not strip leading spaces.
