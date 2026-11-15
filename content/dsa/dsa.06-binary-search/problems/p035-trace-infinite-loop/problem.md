# Trace a loop that never ends

Predict **exactly** what this program prints. Do not run it.

```python
a = [1, 3, 5, 7]
x = 7
lo, hi = 0, len(a) - 1
steps = 0
while lo < hi and steps < 6:
    mid = (lo + hi) // 2
    steps += 1
    if a[mid] < x:
        lo = mid
    else:
        hi = mid
    print("step", steps, "mid", mid, "lo", lo, "hi", hi)
print("stopped:", "lo", lo, "hi", hi, "steps", steps)
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

This version of the search has a bug: it uses `lo = mid` instead of `lo = mid + 1`. To keep the experiment safe the loop also stops after 6 steps (`steps < 6`); in a real program it would run forever.
Trace each step: the program prints `step`, the step number, then `mid`, `lo` and `hi` **after** the update.

## After you answer

1. In which step did the range stop changing? What were `lo` and `hi` then?
2. Which exact values of `lo` and `hi` make `lo = mid` stuck?
3. Name two different fixes. (One changes the update, one changes how `mid` is computed.)
