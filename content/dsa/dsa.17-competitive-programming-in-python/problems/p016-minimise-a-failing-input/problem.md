# Minimise a failing input

A stress test found a failing input with 40 numbers. Tracing it by hand is hopeless; a failing input with 2 numbers is easy. Write

```python
shrink(case, fails)
```

where `case` is a list and `fails(candidate)` is a function that returns `True` when the program **still fails** on `candidate`.

- If `fails(case)` is `False`, raise `ValueError` (there is nothing to shrink).
- Otherwise return a smaller list `result` such that `fails(result)` is `True` and **removing any single element** of `result` makes `fails` return `False`. (This is called a *1-minimal* case.)
- Do not change the list you receive: return a new list. Keep the order of the elements that stay.
- Do not call `fails` more than `n * (n + 1) + 2` times for a list of `n` elements.

## Example

```python
fails = lambda c: 7 in c and 3 in c and c.index(7) < c.index(3)
print(shrink([5, 7, 1, 9, 3, 3, 8], fails))     # [7, 3]
```

Removing `7` or `3` from `[7, 3]` makes the failure disappear, so the case cannot be smaller by single removals.
