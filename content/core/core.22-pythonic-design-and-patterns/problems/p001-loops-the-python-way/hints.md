## Hint 1

Ask of each loop: do I need the **position**, or only the **item**? If you need the position
and the item, `enumerate` gives both. If you walk two lists together, what does `zip` do when
one list is shorter, and does that match what the old code did?

## Hint 2

For the yes/no function: `any(condition for item in items)` stops at the first `True`.
For counting: a comparison like `x == y` is `True` or `False`, and `sum` treats those as 1 and 0.

```
indexed_lines          -> [f"{n}: {line}" for n, line in enumerate(lines, start=1)]
add_lists              -> [x + y for x, y in zip(a, b)]
has_negative           -> any(n < 0 for n in numbers)
count_equal_positions  -> sum(x == y for x, y in zip(a, b))
```
