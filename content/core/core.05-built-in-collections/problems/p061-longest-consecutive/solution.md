## Approach

A set gives O(1) membership. A value `x` starts a run only if `x - 1` is missing. From each
start, walk upward while the next value exists. Every value is visited in exactly one walk, so
the whole thing is O(n).

## Code

```python
values = set(int(x) for x in input().split())
best_len, best_start = 0, None
for x in values:
    if x - 1 not in values:
        length = 1
        while x + length in values:
            length += 1
        if length > best_len or (length == best_len and x < best_start):
            best_len, best_start = length, x
print("Length:", best_len)
if best_len:
    print(f"Run: {best_start} to {best_start + best_len - 1}")
```

## Complexity

O(n) average time and O(n) extra space.

## Another way

Sort the distinct values, then scan once, extending the current run while each value is one
more than the previous. O(n log n), simple and also fast enough here.
