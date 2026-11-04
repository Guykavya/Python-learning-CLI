# Trace the probes of a closed binary search

Predict **exactly** what this program prints. Do not run it.

```python
a = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
x = 40
lo, hi = 0, len(a) - 1
probes = 0
while lo <= hi:
    mid = (lo + hi) // 2
    probes += 1
    print("lo", lo, "mid", mid, "hi", hi, "a[mid]", a[mid])
    if a[mid] == x:
        print("found at", mid)
        break
    elif a[mid] < x:
        lo = mid + 1
    else:
        hi = mid - 1
else:
    print("not found, lo", lo, "hi", hi)
print("probes", probes)
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

Write down `lo`, `mid` and `hi` before each comparison. The ten numbers sit at indices 0 to 9. The target 40 is **not** in the list, so watch how the loop ends:
the condition `lo <= hi` becomes false and the `else` branch of the `while` runs (it runs only when the loop was not left through `break`).

## After you answer

1. Why did the search need exactly 4 probes for 10 numbers? What is the largest number of probes for a list of 10?
2. At the end, `lo` is 7. What does that number mean for the value 40? (Hint: compare with the insertion point from section 6.)
3. Change `x` to 23 and trace again. At which probe is it found?
