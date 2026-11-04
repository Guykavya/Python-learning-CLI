# Trace a half-open lower bound with duplicates

Predict **exactly** what this program prints. Do not run it.

```python
a = [1, 2, 2, 2, 5, 7, 7, 9]


def lower_bound(x):
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        print("  lo", lo, "mid", mid, "hi", hi, "a[mid]", a[mid])
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


for x in (2, 7, 8):
    print("x =", x)
    print("  answer", lower_bound(x))
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

Keep `lo`, `mid`, `hi` in a small table for each target. The list has the value 2 three times (indices 1, 2, 3) and 7 twice (indices 5, 6).
Note that every step prints `a[mid]` **before** the decision is taken. Lines inside a search are indented by two spaces.

## After you answer

1. For x = 2 the loop never stops when it sees a 2 at `mid`. What does it do instead, and why is that what we want?
2. What is the relation between the answer for x = 7 and the number of elements smaller than 7?
3. For x = 8, which element does `lo` end up pointing to? Is it equal to 8?
