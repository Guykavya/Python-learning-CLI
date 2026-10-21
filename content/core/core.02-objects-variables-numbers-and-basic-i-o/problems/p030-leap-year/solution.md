## Approach

Turn each rule into a comparison and combine them with `and` / `or`.

## Code

```python
year = int(input())
print((year % 4 == 0 and year % 100 != 0) or year % 400 == 0)
```

## Why it works

- 2024: divisible by 4, not by 100, so the first part is `True`.
- 1900: divisible by 100, first part `False`; not divisible by 400, second part `False`.
- 2000: first part `False`; divisible by 400, so `True`.

`and` binds tighter than `or`, so the brackets are not strictly needed, but they make the intent clear.

## Another way

`year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)` gives the same result.
