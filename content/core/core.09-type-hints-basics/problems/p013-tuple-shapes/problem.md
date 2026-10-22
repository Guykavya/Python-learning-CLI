# Fixed tuples and tuple[int, ...]

Write four annotated functions in `solution.py`. Choose between the **fixed** tuple (one type per
position) and the **any-length** tuple (`tuple[int, ...]`).

1. `min_max(numbers: list[int]) -> tuple[int, int]` returns `(smallest, largest)`.
2. `sorted_unique(numbers: tuple[int, ...]) -> tuple[int, ...]` returns a tuple with the
   duplicates removed, sorted from smallest to largest.
3. `split_name(full: str) -> tuple[str, str]` splits a full name at the **first** space into
   `(first, rest)`. A single word gives `(word, "")`. An empty string gives `("", "")`.
4. `head_tail(numbers: tuple[int, ...]) -> tuple[int | None, tuple[int, ...]]` returns the first
   item (or `None` for an empty tuple) and a tuple of all the others.

**Examples**

```python
min_max([4, 9, 1, 7])            # (1, 9)
sorted_unique((3, 1, 3, 2, 1))   # (1, 2, 3)
split_name("Mary Ann Lee")       # ("Mary", "Ann Lee")
split_name("Asha")               # ("Asha", "")
head_tail((5, 6, 7))             # (5, (6, 7))
head_tail(())                    # (None, ())
```
