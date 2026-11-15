# Trace the search for a ship capacity

Predict **exactly** what this program prints. Do not run it.

```python
w = [3, 2, 2, 4, 1, 4]
days = 3


def days_needed(cap):
    d, load = 1, 0
    for x in w:
        if load + x > cap:
            d += 1
            load = 0
        load += x
    return d


lo, hi = max(w), sum(w)
while lo < hi:
    mid = (lo + hi) // 2
    d = days_needed(mid)
    print("lo", lo, "hi", hi, "mid", mid, "days", d, "ok", d <= days)
    if d <= days:
        hi = mid
    else:
        lo = mid + 1
print("answer", lo)
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

The weights are `[3, 2, 2, 4, 1, 4]`. For every `mid` first work out `days_needed(mid)` by hand: add the packages one by one and start a new day when the next one does not fit.
Remember that `lo = max(w) = 4` and `hi = sum(w) = 16` at the start. A line is printed for each probe of the search, with the `ok` value as Python prints it (`True` or `False`).

## After you answer

1. At which probe did the search first see that capacity 5 is too small? What did it do with `lo`?
2. The final answer is 6. Check by hand that capacity 6 uses 3 days and capacity 5 needs 4.
3. How many probes did the search need? How many candidates were there at the start?
