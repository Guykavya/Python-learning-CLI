## Approach

Each yes/no question is a comparison, and a comparison is already a `bool` that `print` can show.
Ranges are expressed with chained comparisons.

## Code

```python
marks = int(input())
total = int(input())
pct = marks / total * 100
print(f"Percentage: {pct:.2f}")
print("Passed:", pct >= 40)
print("Distinction:", 75 <= pct <= 100)
print("Valid:", 0 <= marks <= total)
```

## Why the upper limit matters

Bad input such as 120 out of 100 gives 120%. Without the upper limit, it would count as a
distinction. Range checks should normally have two ends.

## Another way

`pct >= 75 and pct <= 100` is the same as the chained form, just longer.
