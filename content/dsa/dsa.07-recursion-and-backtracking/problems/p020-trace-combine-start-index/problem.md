# Trace: combinations n choose k

This is `combine(n, k)` from chapter section 7, with a `print` at the start of every call showing the `start` value and the current `path`.

Predict **exactly** what the program prints. Do not run it.

```python
def combine(n, k):
    result, path = [], []

    def go(start):
        print("start", start, "path", path)
        if len(path) == k:
            result.append(path[:])
            return
        for x in range(start, n + 1):
            path.append(x)
            go(x + 1)
            path.pop()

    go(1)
    return result


print(combine(4, 2))
```

Write your answer in `answer.txt`, one printed line per line, for example `start 3 path [1, 2]`. The last line is the returned list.

## How to work

Each call either records a full path (length `k = 2`) and returns, or loops `x` from `start` to `n = 4`. After choosing `x`, the child starts at `x + 1`. Note that a call is printed **before** the length check, so even complete paths print a line.

## After you answer

1. Which call loops over an empty range? Why is it still printed?
2. How many calls are there in total? How many of them record an answer?
3. The pruned version (section 7, "Pruning the tail") stops the loop at `n - need + 1`. Which printed line would disappear?
