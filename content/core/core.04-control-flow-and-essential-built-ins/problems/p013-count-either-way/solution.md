## Approach

Pick the step first. Then the stop is always `b + step`, one step beyond `b` in the
direction of travel.

## Code

```python
a = int(input())
b = int(input())
step = 1 if a <= b else -1
line = ""
for n in range(a, b + step, step):
    line += f"{n} "
print(line.strip())
```

## Why `b + step` works both ways

Going up, `b + 1` is just past `b`. Going down, `b + (-1)` is just below `b`. One formula,
because the step carries the direction.

## Another way

`for n in range(min(a, b), max(a, b) + 1)` gives the numbers in increasing order; wrap it in
`reversed(...)` when `a > b`.
