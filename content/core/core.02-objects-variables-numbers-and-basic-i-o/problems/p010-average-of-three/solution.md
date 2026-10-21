## Approach

Read three floats, add them once, reuse the total for the average.

## Code

```python
a = float(input())
b = float(input())
c = float(input())
total = a + b + c
print(f"Total: {total:.2f}")
print(f"Average: {total / 3:.2f}")
```

## Why brackets or a name matter

`/` has higher precedence than `+`, so `a + b + c / 3` means `a + b + (c / 3)`.
Giving the total a name avoids the problem and makes the code easier to read.

## Another way

`print(f"Average: {(a + b + c) / 3:.2f}")` with explicit brackets.
