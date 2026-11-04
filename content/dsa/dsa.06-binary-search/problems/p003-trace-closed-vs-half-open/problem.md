# Trace: closed against half-open

Predict **exactly** what this program prints. Do not run it.

```python
a = [1, 3, 5, 7, 9, 11, 13]


def closed(x):
    lo, hi, probes = 0, len(a) - 1, []
    while lo <= hi:
        mid = (lo + hi) // 2
        probes.append(mid)
        if a[mid] == x:
            return probes, mid
        elif a[mid] < x:
            lo = mid + 1
        else:
            hi = mid - 1
    return probes, -1


def half_open(x):
    lo, hi, probes = 0, len(a), []
    while lo < hi:
        mid = (lo + hi) // 2
        probes.append(mid)
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return probes, lo


for x in (9, 10, 1, 14):
    print(x, "closed", closed(x), "half-open", half_open(x))
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

Run both functions by hand for each of the four targets. `closed` uses `lo = 0, hi = n - 1` and `while lo <= hi`; `half_open` uses `hi = n` and `while lo < hi`.
Each function returns a pair: the list of probed indices, and the result. Python prints a tuple of a list and a number as `([3, 5, 4], 4)`.

## After you answer

1. For which targets did both templates probe the same indices? Why?
2. For a missing target the closed version returns `-1`, the half-open version returns an index. What does that index mean?
3. The closed version stops as soon as it finds the value. Does the half-open version ever stop early? What does that cost and what does it buy?
