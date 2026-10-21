## Approach

Walk the tokens once, comparing each with the **last run** (`runs[-1]`). Each run is a small
list `[token, count]` so its count can be increased in place.

## Code

```python
runs = []
for token in input().split():
    if runs and runs[-1][0] == token:
        runs[-1][1] += 1
    else:
        runs.append([token, 1])
pieces = [t if n == 1 else f"{t}*{n}" for t, n in runs]
print(" ".join(pieces) if pieces else "(empty)")
print("Runs:", len(runs))
```

## Complexity

O(n) for n tokens.

## Why a list and not a tuple for each run

A tuple cannot change, so `runs[-1][1] += 1` would fail. You could also replace the last
tuple: `runs[-1] = (token, count + 1)`.
